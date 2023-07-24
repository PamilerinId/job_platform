from enum import Enum
from typing_extensions  import Annotated
from typing import List


from fastapi import FastAPI, Request, Depends
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import sentry_sdk


from core.router import router
from core.env import config
from core.exceptions import CustomException
from core.dependencies import Logging, engine
from core.middlewares import (
    AuthenticationMiddleware,
    AuthBackend,
    # SQLAlchemyMiddleware,
    # ResponseLogMiddleware,
)
# from core.helpers.cache import Cache, RedisBackend, CustomKeyMaker
# from core.helpers.db import CoreModel


# def init_db(app_: FastAPI) -> None:
#     CoreModel.metadata.create_all(bind=engine)

def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error,
        ),
        # Middleware(SQLAlchemyMiddleware),
        # Middleware(ResponseLogMiddleware),
    ]
    return middleware


# def init_cache() -> None:
#     Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())

# TODO: Refactor sentry
# sentry_sdk.init(
#     dsn="https://e64a429e7e574a8e87e06bc4792304f1@o4505579758813184.ingest.sentry.io/4505579762286592",

#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production,
#     traces_sample_rate=1.0,
# )

def create_app() -> FastAPI:
    app_ = FastAPI(
        title="DistinctAI v2 API",
        description="",
        version="2.0.0",
        docs_url=None if config.ENV == "production" else "/docs",
        redoc_url=None if config.ENV == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    init_routers(app_=app_)
    init_listeners(app_=app_)
    # init_cache()
    return app_


app = create_app()