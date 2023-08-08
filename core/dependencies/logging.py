import logging
from fastapi import BackgroundTasks


class Logging:
    def __init__(self, background_task: BackgroundTasks):
        background_task.add_task(self._send_log)

    async def _send_log(self):
        pass



# Disable uvicorn access logger
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.getLevelName(logging.DEBUG))