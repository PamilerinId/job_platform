from dotenv import load_dotenv
load_dotenv()

import os

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8005
    SECRET_KEY: str | None = os.environ.get("SECRET_KEY")
    POSTGRES_USER : str | None = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD:str | None = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_SERVER : str | None= os.environ.get("POSTGRES_SERVER")
    POSTGRES_PORT : int | None = os.environ.get("POSTGRES_PORT",5432) # default postgres port is 5432
    POSTGRES_DB : str | None = os.environ.get("POSTGRES_DATABASE")
    WRITER_DB_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    READER_DB_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    JWT_SECRET_KEY: str | None = os.environ.get("SECRET_KEY")
    JWT_ALGORITHM: str | None = os.environ.get("JWT_ALGORITHM")
    JWT_PRIVATE_KEY: str | None = os.environ.get("JWT_PRIVATE_KEY")
    JWT_PUBLIC_KEY: str | None = os.environ.get("JWT_PUBLIC_KEY")
    REFRESH_TOKEN_EXPIRES_IN: int | None = os.environ.get("REFRESH_TOKEN_EXPIRES_IN", 60)
    ACCESS_TOKEN_EXPIRES_IN: int | None = os.environ.get("ACCESS_TOKEN_EXPIRES_IN", 15)
    SENTRY_DSN: str | None = os.environ.get("SENTRY_DSN")
    POSTMARK_API_KEY: str | None = os.environ.get("POSTMARK_SERVER_TOKEN")
    AWS_ACCESS_KEY_ID: str | None = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: str | None = os.environ.get("AWS_S3_BUCKET")
    AWS_S3_REGION: str | None = os.environ.get("AWS_S3_REGION")
    AWS_S3_FOLDER_BASE: str | None = os.environ.get("AWS_S3_FOLDER_BASE")
    AWS_S3_FOLDER_PHOTOS: str | None = os.environ.get("AWS_S3_FOLDER_PHOTOS")
    AWS_S3_FOLDER_CVS: str | None = os.environ.get("AWS_S3_FOLDER_CVS")
    AWS_S3_FOLDER_PROCTOR: str | None = os.environ.get("AWS_S3_FOLDER_PROCTOR")
    AWS_S3_FOLDER_ASSESSMENT: str | None = os.environ.get("AWS_S3_FOLDER_ASSESSMENT")
    GOOGLE_CLIENT_ID: str | None = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str | None = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    CLIENT_CANDIDATE_BASE_URL: str = 'https://dashboard.job_board.ai'
    AUTH: str = '/auth'
    CHANGE_PASSWORD: str = '/change-password'
    
    # CELERY_BROKER_URL: str = "amqp://user:bitnami@localhost:5672/"
    # CELERY_BACKEND_URL: str = "redis://:password123@localhost:6379/0"
    # REDIS_HOST: str = "localhost"
    # REDIS_PORT: int = 6379


class DevelopmentConfig(Config):
    # WRITER_DB_URL: str = f"mysql+aiomysql://root:fastapi@db:3306/fastapi"
    # READER_DB_URL: str = f"mysql+aiomysql://root:fastapi@db:3306/fastapi"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    POSTMARK_TEST_MODE: bool = True


class LocalConfig(Config):
    # WRITER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    # READER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    POSTMARK_TEST_MODE: bool = True


class ProductionConfig(Config):
    ENV: str = "production"
    DEBUG: bool = False
    # WRITER_DB_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    # READER_DB_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


def get_config():
    env = os.environ.get("ENV", "local")
    config_type = {
        "development": DevelopmentConfig(),
        "local": LocalConfig(),
        "production": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
