from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "BeanDetect AI"

    # Database Settings (Supabase)
    DATABASE_HOST: str = "aws-1-us-east-1.pooler.supabase.com"
    DATABASE_PORT: int = 6543
    DATABASE_NAME: str = "postgres"
    DATABASE_USER: str = "postgres.tswxhjvhakahpbqxtnoq"
    DATABASE_PASSWORD: str = "devbeans_db"
    DATABASE_POOL_MODE: str = "transaction"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # BLOB Storage
    MODEL_BLOB_URL: str = "https://devbeansteamstorage.blob.core.windows.net/ml-models/defect_detector.h5"

    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()