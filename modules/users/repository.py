from sqlalchemy.orm import Session, joinedload

from core.dependencies.sessions import get_db

from .models import Company, User, CandidateProfile, ClientProfile, CompanyProfile


class UserRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()

    async def create(self):
        pass

    async def get_by_email(self, email):
        user = self.db.query(User).filter(User.email == email.lower()).first()
        return user

    async def get_by_email_role(self, email, role):
        pass

    async def get_client_profile(self, email):
        user_profile = self.db.query(User).options(
                joinedload(User.client_profile)
                .joinedload(ClientProfile.company)).filter(User.email == email).first()
        return user_profile

    async def get_candidate_profile(self, email):
        user_profile = self.db.query(User).options(
                joinedload(User.candidate_profile)).filter(User.email == email).first()
        return user_profile

    async def get_list(self):
        pass

    async def update(self):
        pass

    async def delete(self):
        pass

class CompanyRepository:
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