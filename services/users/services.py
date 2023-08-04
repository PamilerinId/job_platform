from datetime import datetime
import secrets
from typing import Annotated, List
from pydantic import parse_obj_as
import uuid
from slugify import slugify

from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session, joinedload

from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user
from core.exceptions import DuplicateCompanyException, UnauthorisedUserException, NotFoundException
from core.helpers.schemas import CustomListResponse, CustomResponse

from .models import Company, CompanyProfile, User, UserType
from .schemas import BaseUser, BaseCompany, CreateCompanySchema

router = APIRouter(
    prefix="/users",
)

@router.get("/companies", response_model=CustomListResponse, tags=["Companies"])
async def fetch_companies(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):#, user_id: str = Depends(require_user)):
    skip = (page - 1) * limit

    companies = db.query(Company).options(joinedload(Company.profile)).filter(
        Company.name.contains(search)).limit(limit).offset(skip).all()
    
    # print('##########################', companies[0].profile,  flush=True)
    if len(companies) < 1: 
        raise NotFoundException('No Companies found')
    return {'message': 'Company list retrieved successfully', 'count': len(companies), 'data': companies}

@router.post('/companies', status_code=status.HTTP_201_CREATED, response_model=CustomResponse[BaseCompany], tags=["Companies"])
async def create_company(payload: CreateCompanySchema,
                   current_user: Annotated[BaseUser, Depends(get_current_user)],
                   db: Session = Depends(get_db)):
    
    #TODO: Refactor to utils
    slug = slugify(payload.name, max_length=15, word_boundary=True, 
                separator=".", stopwords=['the', 'and', 'of'])
    
    company = db.query(Company).filter(Company.slug == slug).first()

    if company:
        # Contact company owner message, reach out to support email
        raise DuplicateCompanyException
    
    # Check that the client is a valid user and has role of CLIENT
    user = db.query(User).filter(User.id == current_user.id)

    if current_user.role != UserType.CLIENT:
        raise UnauthorisedUserException("You are not authorized to create company profiles")
    
    new_company = Company(**payload.dict())
    new_company.slug = slug
    new_company.owner_id = current_user.id
    new_company.secret_key = secrets.token_urlsafe()
    db.add(new_company)
    db.commit()
    # update related models
    user.company_id = new_company.id
    new_company_profile = CompanyProfile(company_id=new_company.id)
    new_company_profile.updated_at = datetime.now()
    db.add(new_company_profile)
    db.commit()

    db.refresh(new_company)
    return {'message': 'Company created successfully', 'data': BaseCompany.from_orm(new_company)}   

@router.patch('/companies', response_model=CustomResponse[BaseCompany], tags=["Companies"])
async def update_company_profile():
    pass



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