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
# Importar routers
from iam_profile.interfaces.rest.controllers.auth_controller import router as auth_router
from iam_profile.interfaces.rest.controllers.profile_controller import router as profile_router
from iam_profile.interfaces.rest.controllers.user_controller import router as user_router
from coffee_lot_management.interfaces.rest.controllers.coffee_lot_controller import router as coffee_lot_router
from grain_classification.interfaces.rest.controllers.classification_controller import router as classification_router
from traceability_certification.interfaces.rest.controllers.certification_controller import router as certification_router


# Backend configuration
BACKEND_URL = os.environ.get(
    "BACKEND_URL",
    "https://bean-detect-ai-api-platform.azurewebsites.net"
)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Eventos de inicio y cierre del ciclo de vida de la aplicación"""
    print("=" * 60)
    print("🚀 Iniciando BeanDetect AI Backend")
    print("=" * 60)

    # Startup - Base de datos
    print("\n[1/1] Inicializando base de datos...")
    init_db()
    print("Base de datos inicializada")

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
    CORSMiddleware, # type: ignore
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(user_router)
app.include_router(coffee_lot_router)
app.include_router(classification_router)
app.include_router(certification_router)


# Endpoints
@app.get("/", tags=["Default Backend Status"])
async def root():
    """Endpoint raíz"""
    return {
        "service": "BeanDetect AI API",
        "version": "1.0.0",
        "status": "running",
        "backend": BACKEND_URL,
        "docs": "/docs",
        "re-docs": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )