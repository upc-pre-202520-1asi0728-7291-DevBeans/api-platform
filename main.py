import os
import sys

sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from shared.infrastructure.persistence.database.repositories.settings import settings
from shared.domain.database import init_db
from iam_profile.interfaces.rest.controllers.auth_controller import router as auth_router
from iam_profile.interfaces.rest.controllers.profile_controller import router as profile_router
from coffee_lot_management.interfaces.rest.controllers.coffee_lot_controller import router as coffee_lot_router
# from grain_classification.interfaces.rest.controllers.classification_controller import router as classification_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Eventos de inicio y cierre del ciclo de vida de la aplicación"""
    print("=" * 60)
    print("🚀 Iniciando BeanDetect AI Backend")
    print("=" * 60)

    # Startup - Base de datos
    print("\n[1/3] Inicializando base de datos...")
    init_db()
    print("Base de datos inicializada")

    '''
    # Startup - Verificar modelo ML
    print("\n[2/3] Verificando modelo de Machine Learning...")
    model_url = settings.MODEL_BLOB_URL
    if model_url and model_url != "https://your-blob-storage-url-here":
        safe_url = model_url.split('?')[0] if '?' in model_url else model_url
        print(f"Blob Storage configurado: {safe_url}")
    else:
        print("MODEL_BLOB_URL no configurado - solo ruta local")

    # NUEVO: Precarga del modelo ML
    print("\n[3/3] Precargando modelo CNN...")
    try:
        from grain_classification.infrastructure.ml_predictor_service import MLPredictorService
        from grain_classification.domain.model.valueobjetcs.quality_models import CNN_COLOR_CLASSES

        model_path = "grain_classification/infrastructure/ml_models/defect_detector.h5"

        # Intentar cargar el modelo (descarga si no existe)
        predictor = MLPredictorService(model_path, CNN_COLOR_CLASSES)

        if predictor.cnn_model is not None:
            print("Modelo CNN listo para predicciones")
        else:
            print("Modelo CNN no disponible - las clasificaciones fallarán")

    except Exception as e:
        print(f"Error al precargar modelo: {e}")
        print("   El modelo se intentará cargar en la primera petición")
    '''

    print("\n" + "=" * 60)
    print(f"{settings.PROJECT_NAME} está corriendo")
    print(f"Documentación: http://localhost:8000/docs")
    print("=" * 60 + "\n")

    yield  # Aquí FastAPI empieza a aceptar peticiones

    # Shutdown
    print("\n🛑 Apagando servidor...")


# Crear aplicación FastAPI (usando lifespan)
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(coffee_lot_router)
# app.include_router(classification_router)


# Endpoints
@app.get("/", tags=["Default Backend Status"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "BeanDetect AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

'''
@app.get("/health", tags=["Default Backend Status"])
async def health_check():
    """Health check endpoint con verificación de configuración"""
    model_url = settings.MODEL_BLOB_URL
    model_configured = bool(model_url and model_url != "https://your-blob-storage-url-here")

    # Verificar si el modelo ya fue descargado
    model_path = "grain_classification/infrastructure/ml_models/defect_detector.h5"
    model_downloaded = os.path.exists(model_path)
    model_size_mb = None

    if model_downloaded:
        try:
            model_size_mb = round(os.path.getsize(model_path) / (1024 ** 2), 2)
        except:
            pass

    return {
        "status": "healthy",
        "database": "connected",
        "ml_model": {
            "blob_storage_configured": model_configured,
            "configured_url": model_url if model_configured else None,
            "model_downloaded": model_downloaded,
            "model_size_mb": model_size_mb,
            "fallback_strategy": "local → blob storage"
        }
    }
'''

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_delay=0.5,
        reload_includes=["*.py"],
        log_level="info"
    )