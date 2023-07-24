from datetime import datetime
import uuid

from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session

from core.dependencies.sessions import get_db

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
    return {'status': 'success', 'results': len(companies), 'companies': companies}

@router.post('/companies', status_code=status.HTTP_201_CREATED, response_model=CompanyResponse, tags=["Companies"])
def create_company(company: CreateCompanySchema, db: Session = Depends(get_db)):#, owner_id: str = Depends(require_user)):
    # post.user_id = uuid.UUID(owner_id)
    new_company = Company(**company.dict())
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