

from sqlalchemy.orm import Session

from core.dependencies.sessions import get_db


class JobRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()

    async def create(self):
        pass

    async def get(self):
        pass

    async def get_list(self):
        pass

    async def update(self):
        pass

    async def delete(self):
        pass