"""
Application Configuration
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://bugcrowd:bugcrowd123@localhost:5432/bugcrowd_db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery / RabbitMQ
    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL",
        "amqp://guest:guest@localhost:5672//"
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/1"
    )
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # MinIO / S3
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "bugcrowd-uploads")
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()
