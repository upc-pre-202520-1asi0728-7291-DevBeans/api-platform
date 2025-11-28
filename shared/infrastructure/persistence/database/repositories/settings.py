from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "BeanDetect AI"

    # Database Settings
    DATABASE_HOST: str = "dev-beans-production-db.postgres.database.azure.com"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "dev_beans_azure_db"  # nombre de la BD
    DATABASE_USER: str = "useradmin"  # nombre de usuario
    DATABASE_PASSWORD: str = "dev-beans-1234"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # BLOB Storage
    MODEL_BLOB_URL: str = "https://devbeansteamstorage.blob.core.windows.net/ml-models/defect_detector.h5"

    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = "your-cloud-name"
    CLOUDINARY_API_KEY: str = "your-api-key"
    CLOUDINARY_API_SECRET: str = "your-api-secret"

    # SMTP Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_SENDER_EMAIL: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()