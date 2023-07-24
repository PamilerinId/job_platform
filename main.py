import os
import uvicorn
from dotenv import load_dotenv

load_dotenv() 

from core.env import config

def main():
    uvicorn.run(
        app="core.settings:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True if config.ENV != "production" else False,
        workers=1,
    )


if __name__ == "__main__":
    main()
