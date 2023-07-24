from dotenv import load_dotenv
load_dotenv()

import os

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8005
    POSTGRES_USER : str | None = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD:str | None = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_SERVER : str | None= os.environ.get("POSTGRES_SERVER")
    POSTGRES_PORT : int | None = os.environ.get("POSTGRES_PORT",5432) # default postgres port is 5432
    POSTGRES_DB : str | None = os.environ.get("POSTGRES_DATABASE")
    WRITER_DB_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    READER_DB_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    JWT_SECRET_KEY: str = "fastapi"
    JWT_ALGORITHM: str = "HS256"
    JWT_PRIVATE_KEY: str | None = os.environ.get("JWT_PRIVATE_KEY")
    JWT_PUBLIC_KEY: str | None = os.environ.get("JWT_PUBLIC_KEY")
    REFRESH_TOKEN_EXPIRES_IN: int | None = os.environ.get("REFRESH_TOKEN_EXPIRES_IN", 60)
    ACCESS_TOKEN_EXPIRES_IN: int | None = os.environ.get("ACCESS_TOKEN_EXPIRES_IN", 15)
    # SENTRY_SDN: str = None
    # CELERY_BROKER_URL: str = "amqp://user:bitnami@localhost:5672/"
    # CELERY_BACKEND_URL: str = "redis://:password123@localhost:6379/0"
    # REDIS_HOST: str = "localhost"
    # REDIS_PORT: int = 6379


class DevelopmentConfig(Config):
    # WRITER_DB_URL: str = f"mysql+aiomysql://root:fastapi@db:3306/fastapi"
    # READER_DB_URL: str = f"mysql+aiomysql://root:fastapi@db:3306/fastapi"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


class LocalConfig(Config):
    # WRITER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    # READER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    ...


class ProductionConfig(Config):
    DEBUG: bool = False
    WRITER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/prod"
    READER_DB_URL: str = f"mysql+aiomysql://fastapi:fastapi@localhost:3306/prod"


def get_config():
    env = os.environ.get("ENV", "local")
    config_type = {
        "dev": DevelopmentConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
