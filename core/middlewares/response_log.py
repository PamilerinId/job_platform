import http
import time

from fastapi import Request
from typing import Optional
from pydantic import ConfigDict, BaseModel, Field
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from core.dependencies.logging import logger

class ResponseInfo(BaseModel):
    headers: Optional[Headers] = Field(default=None, title="Response header")
    body: str = Field(default="")
    status_code: Optional[int] = Field(default=None, title="Status code")
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ResponseLogMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        response_info = ResponseInfo()

        async def _logging_send(message: Message) -> None:
            if message.get("type") == "http.response.start":
                response_info.headers = Headers(raw=message.get("headers"))
                response_info.status_code = message.get("status")
            elif message.get("type") == "http.response.body":
                if body := message.get("body"):
                    response_info.body += body.decode("utf8")

            await send(message)

        await self.app(scope, receive, _logging_send)


async def log_request_middleware(request: Request, call_next):
    """
    This middleware will log all requests and their processing time.
    E.g. log:
    0.0.0.0:1234 - GET /ping 200 OK 1.00ms
    """
    logger.debug("middleware: log_request_middleware")
    url = f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    try:
        status_phrase = http.HTTPStatus(response.status_code).phrase
    except ValueError:
        status_phrase=""
    logger.info(f'{host}:{port} - "{request.method} {url}" {response.status_code} {status_phrase} {formatted_process_time}ms')
    return response
