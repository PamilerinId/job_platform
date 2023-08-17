from datetime import datetime
import secrets
from typing import Annotated, List
from core.exceptions.base import BadRequestException
from pydantic import parse_obj_as
from uuid import UUID
from slugify import slugify

from fastapi import Depends, HTTPException, status, APIRouter, Response, Path
from sqlalchemy.orm import Session, joinedload

from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user
from core.exceptions import DuplicateCompanyException, UnauthorisedUserException, NotFoundException
from core.helpers.schemas import CustomListResponse, CustomResponse

from .models import Company, CompanyProfile, User, UserType
from .schemas import BaseUser, BaseCompany, CreateCompanySchema, UpdateCompanySchema, UpdateUserProfile

router = APIRouter(
    prefix="/users",
)

@router.get("/companies", response_model=CustomListResponse[BaseCompany], tags=["Companies"])
async def fetch_companies(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):#, user_id: str = Depends(require_user)):
    skip = (page - 1) * limit

    companies = db.query(Company).options(joinedload(Company.profile)).filter(
        Company.name.contains(search)).limit(limit).offset(skip).all()
    
    if len(companies) < 1: 
        raise NotFoundException('No Companies found')
    return {'message': 'Company list retrieved successfully', 'count': len(companies),'data': companies}


@router.get("/companies/{company_id}", response_model=CustomResponse[BaseCompany], tags=["Companies"])
async def fetch_companies(
    company_id: Annotated[UUID, Path(title="The ID of the company to be retrieved")],
    db: Session = Depends(get_db)):#, user_id: str = Depends(require_user)):

    company = db.query(Company).options(joinedload(Company.profile)).filter(
        Company.id == company_id).first()
    
    if company is None:
        raise NotFoundException("Company not found!")
    
    return {'message': 'Company profile retrieved successfully', 'data': company}


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
async def update_company_profile(company_id: Annotated[UUID, Path(title="The ID of the company to be updated")],
                                 payload: UpdateCompanySchema,
               current_user: Annotated[BaseUser, Depends(get_current_user)],
               db: Session = Depends(get_db),):
    
    if current_user.role == UserType.CANDIDATE:
        raise UnauthorisedUserException("User is not authorised to edit company details")
    
    if current_user.client_profile.company.id != company_id:
        raise UnauthorisedUserException("User is not authorised to edit company details")
    
    company_query = db.query(Company).filter(Company.id == company_id)
    company = company_query.first()
    if company is None:
        raise NotFoundException("Company not found!")
    
    company_query.update(payload.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    
    return {"message":"Company profile updated successfully","data": company}


@router.patch('/profile', response_model=CustomResponse[BaseUser], tags=["Users"])
async def update_user_profile(payload: UpdateUserProfile,
               current_user: Annotated[BaseUser, Depends(get_current_user)],
               db: Session = Depends(get_db),):
    
    user_query = db.query(User)

    if current_user.role == UserType.CANDIDATE:
        user = user_query.options(joinedload(User.candidate_profile)).filter(User.id == current_user.id).first()
    elif current_user.role == UserType.CLIENT:
        user = user_query.options(joinedload(User.client_profile)).filter(User.id == current_user.id).first()
    
    if user is None:
        raise NotFoundException("User not found!")
    
    user_query.update(payload.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    db.refresh(user)
    
    return {"message":"User profile updated successfully","data": user}

# Admin Use
@router.delete('/{company_id}', response_model=CustomResponse, tags=["Companies"])
async def delete_job(company_id: Annotated[UUID, Path(title="The ID of the company to be deleted")],
               current_user: Annotated[BaseUser, Depends(get_current_user)],
               db: Session = Depends(get_db),):
    
    if current_user.role != UserType.ADMIN:
        raise UnauthorisedUserException("User is not authorised to access this view")
    
    company = db.query(Company).filter(Company.id == company_id).first()

    if company is None:
        raise NotFoundException("Company not found!")
    try:
        db.delete(company)
        db.commit()
        return {"message": "Company profile deleted"}
    except BadRequestException:
        db.rollback()
        raise BadRequestException("Company delete failed")


# ADMIN Routes
@router.get('/clients', response_model=CustomListResponse[BaseUser], tags=["User"])
def fetch_clients(db: Session = Depends(get_db)):#, user_id: str = Depends(require_user)):
    users = db.query(User).filter(User.role == UserType.CLIENT).all()
    return {'message': 'Client list retrieved successfully', 'count': len(users),'data': users}

@router.get('/candidates', response_model=BaseUser, tags=["User"])
def fetch_candidates(db: Session = Depends(get_db)):#, user_id: str = Depends(require_user)):
    users = db.query(User).filter(User.role == UserType.CANDIDATE).all()
    return {'message': 'Candidate list retrieved successfully', 'count': len(users),'data': users}

# TODO: 
# CRUD Users
# - Candidates profile