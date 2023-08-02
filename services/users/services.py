from datetime import datetime
import secrets
from typing import Annotated
import uuid
from slugify import slugify
from core.exceptions.auth import DuplicateCompanyException


from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session

from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user

from .models import Company, User
from .schemas import BaseUser, ListCompanyResponse, BaseCompany, CreateCompanySchema, CompanyResponse

router = APIRouter(
    prefix="/users",
)

@router.get("/companies", response_model=ListCompanyResponse, tags=["Companies"])
async def fetch_companies(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):#, user_id: str = Depends(require_user)):
    skip = (page - 1) * limit

    companies = db.query(Company).group_by(Company.id).filter(
        Company.name.contains(search)).limit(limit).offset(skip).all()
    return {'status': 'success', 'cout': len(companies), 'data': companies}

@router.post('/companies', status_code=status.HTTP_201_CREATED, response_model=CompanyResponse, tags=["Companies"])
def create_company(payload: CreateCompanySchema,
                   current_user: Annotated[BaseUser, Depends(get_current_user)],
                   db: Session = Depends(get_db), ):
    
    # Refactor to utils
    slug = slugify(payload.name, max_length=15, word_boundary=True, 
                separator=".", stopwords=['the', 'and', 'of'])
    
    company = db.query(Company).filter(Company.slug == slug).first()

    if company:
        # Contact company owner message, reach out to support email
        raise DuplicateCompanyException

    new_company = Company(**payload.dict())
    new_company.slug = slug
    new_company.owner_id = current_user.id
    new_company.secret_key = secrets.token_urlsafe()
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company



# @router.get('/me', response_model=BaseUser, tags=["User"])
# def get_me(db: Session = Depends(get_db)):#, user_id: str = Depends(require_user)):
#     user = db.query(User).filter(User.id == 1).first()
#     return user


@router.get('/clients', response_model=BaseUser, tags=["User"])
def fetch_clients(db: Session = Depends(get_db)):#, user_id: str = Depends(require_user)):
    user = db.query(User).filter(User.id == 1).first()
    return user

@router.get('/candidates', response_model=BaseUser, tags=["User"])
def fetch_candidates(db: Session = Depends(get_db)):#, user_id: str = Depends(require_user)):
    user = db.query(User).filter(User.id == 1).first()
    return user

# TODO: 
# CRUD Companies
# - Companies profile
# CRUD Users
# - Candidates profile