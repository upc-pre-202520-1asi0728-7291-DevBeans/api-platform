from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from shared.infrastructure.persistence.database.repositories.settings import settings
from shared.domain.database import init_db
from iam_profile.interfaces.rest.controllers.auth_controller import router as auth_router
from iam_profile.interfaces.rest.controllers.profile_controller import router as profile_router
from coffee_lot_management.interfaces.rest.controllers.coffee_lot_controller import router as coffee_lot_router
from grain_classification.interfaces.rest.controllers.classification_controller import router as classification_router

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Eventos de inicio y cierre del ciclo de vida de la aplicación"""
    # Startup
    init_db()
    print("Database initialized successfully")
    print(f"{settings.PROJECT_NAME} is running")
    print(f"API Documentation: http://localhost:8000/docs")

    yield  # Aquí FastAPI empieza a aceptar peticiones

    # Shutdown
    print("Application shutting down...")


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
app.include_router(classification_router)


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

@app.get("/health", tags=["Default Backend Status"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )