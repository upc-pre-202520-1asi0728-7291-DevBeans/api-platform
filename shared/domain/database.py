from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from shared.infrastructure.persistence.database.repositories.settings import settings


# Validación de la URL de conexión
print(f"[DEBUG] Inicializando engine con URL: {settings.DATABASE_URL.split('@')[0]}@***")

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,  # Cambiar a True para debug SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    try:
        print("[INFO] Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        print("[INFO] Tablas creadas exitosamente")
    except Exception as e:
        print(f"[ERROR] Error al crear tablas: {e}")
        raise