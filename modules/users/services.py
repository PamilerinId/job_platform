from datetime import datetime
import secrets
from typing import Annotated, List, Optional
from core.exceptions.auth import DuplicateEmailException
from core.exceptions.base import BadRequestException
from core.helpers import password
from pydantic import parse_obj_as
from uuid import UUID
from slugify import slugify

from sqlalchemy import or_

from fastapi import Depends, HTTPException, status, APIRouter, Response, Path
from sqlalchemy.orm import Session, joinedload

from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user
from core.exceptions import DuplicateCompanyException, UnauthorisedUserException, NotFoundException
from core.helpers.schemas import CustomListResponse, CustomResponse

from .models import CandidateProfile, ClientProfile, Company, CompanyProfile, User, UserType
from .schemas import BaseUser, BaseCompany, CreateCompanySchema, CreateUser, UpdateCompanySchema, UpdateUserProfile

router = APIRouter(
    prefix="/users",
)

# ADMIN Routes
@router.post('/', response_model=CustomResponse[BaseUser], tags=["User"])
async def create_user(payload: CreateUser,
    current_user: Annotated[BaseUser, Depends(get_current_user)],
                  db: Session = Depends(get_db)):
    
    if current_user.role != UserType.ADMIN:
        raise UnauthorisedUserException("User is not authorised to access this view")
    
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user:
        raise DuplicateEmailException
    #  Hash the password
    payload.password = password.hash_password(payload.password)
    new_user = User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # update related models
    if payload.role == UserType.CANDIDATE:
        new_candidate_profile = CandidateProfile(user_id=new_user.id)
        new_candidate_profile.updated_at = datetime.now()
        db.add(new_candidate_profile)
    elif payload.role == UserType.CLIENT:
        new_client_profile = ClientProfile(user_id=new_user.id)
        new_client_profile.updated_at = datetime.now()
        db.add(new_client_profile)

    db.commit()
    
    return {'message': 'User created successfully', 'data': new_user}


@router.get('/admin', response_model=CustomListResponse[BaseUser], tags=["User"])
async def fetch_admin(current_user: Annotated[BaseUser, Depends(get_current_user)],
                  db: Session = Depends(get_db), 
                  limit: int = 10, page: int = 1, search: str = ''):#, user_id: str = Depends(require_user)):
    
    if current_user.role != UserType.ADMIN:
        raise UnauthorisedUserException("User is not authorised to access this view")
    
    skip = (page - 1) * limit
    users_query = db.query(User).filter(User.role == UserType.ADMIN)
    user_count = users_query.count()
    users = users_query.limit(limit).offset(skip).all()
    return {'message': 'Admin list retrieved successfully', 'total_count': user_count, 'count': len(users), 'next_page': page + 1,'data': users}


@router.get('/clients', response_model=CustomListResponse[BaseUser], tags=["User"])
async def fetch_clients(current_user: Annotated[BaseUser, Depends(get_current_user)],
                  db: Session = Depends(get_db), 
                  limit: int = 10, page: int = 1, search: str = ''):#, user_id: str = Depends(require_user)):
    
    if current_user.role != UserType.ADMIN:
        raise UnauthorisedUserException("User is not authorised to access this view")
    
    skip = (page - 1) * limit
    users_query = db.query(User).options(
                joinedload(User.client_profile)
                .joinedload(ClientProfile.company)).filter(User.role == UserType.CLIENT)
    if search:
        users_query = users_query.filter(or_(User.first_name.like(f"%{search}%"), User.last_name.like(f"%{search}%"), 
                                             ))
    user_count = users_query.count()
    users = users_query.limit(limit).offset(skip).all()
    return {'message': 'Client list retrieved successfully', 'total_count': user_count, 'count': len(users), 'next_page': page + 1,'data': users}


@router.get('/candidates', response_model=CustomListResponse[BaseUser], tags=["User"])
async def fetch_candidates(current_user: Annotated[BaseUser, Depends(get_current_user)],
                     db: Session = Depends(get_db), 
                  limit: int = 10, page: int = 1, search: str = ''):#, user_id: str = Depends(require_user)):
    
    if current_user.role != UserType.ADMIN:
        raise UnauthorisedUserException("User is not authorised to access this view")
    
    skip = (page - 1) * limit
    users_query = db.query(User).options(
                joinedload(User.candidate_profile)).filter(User.role == UserType.CANDIDATE)
    if search:
        users_query = users_query.filter(or_(User.first_name.like(f"%{search}%"), User.last_name.like(f"%{search}%"), 
                                            ))
    user_count = users_query.count()
    users = users_query.limit(limit).offset(skip).all()
    return {'message': 'Candidate list retrieved successfully', 'total_count': user_count, 'count': len(users), 'next_page': page + 1,'data': users}



@router.get("/admin/{user_id}", response_model=CustomResponse[BaseUser], tags=["User"])
async def fetch_admin_details(
    current_user: Annotated[BaseUser, Depends(get_current_user)],
    user_id: Annotated[UUID, Path(title="The ID of the User to be retrieved")],
    db: Session = Depends(get_db)):#, user_id: str = Depends(require_user)):

    if current_user.role != UserType.ADMIN:
        raise UnauthorisedUserException("User is not authorised to access this view")

    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise NotFoundException("User not found!")
    

    return {'message': 'User details retrieved successfully', 'data': user}


@router.get("/candidate/{user_id}", response_model=CustomResponse[BaseUser], tags=["User"])
async def fetch_candidate_details(
    current_user: Annotated[BaseUser, Depends(get_current_user)],
    user_id: Annotated[UUID, Path(title="The ID of the User to be retrieved")],
    db: Session = Depends(get_db)):#, user_id: str = Depends(require_user)):

    if current_user.role != UserType.ADMIN:
        raise UnauthorisedUserException("User is not authorised to access this view")

    user = db.query(User).options(
                joinedload(User.candidate_profile)).filter(User.id == user_id).first()
    
    if user is None:
        raise NotFoundException("User not found!")
    

    return {'message': 'User details retrieved successfully', 'data': user}

@router.get("/client/{user_id}", response_model=CustomResponse[BaseUser], tags=["User"])
async def fetch_client_details(
    current_user: Annotated[BaseUser, Depends(get_current_user)],
    user_id: Annotated[UUID, Path(title="The ID of the User to be retrieved")],
    db: Session = Depends(get_db)):#, user_id: str = Depends(require_user)):

    if current_user.role != UserType.ADMIN:
        raise UnauthorisedUserException("User is not authorised to access this view")

    user = db.query(User).options(
                joinedload(User.client_profile)
                .joinedload(ClientProfile.company)).filter(User.id == user_id).first()
    
    if user is None:
        raise NotFoundException("User not found!")
    

    return {'message': 'User detals retrieved successfully', 'data': user}

# ##################################
@router.get("/companies", response_model=CustomListResponse[BaseCompany], tags=["Companies"])
async def fetch_companies(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):#, user_id: str = Depends(require_user)):
    skip = (page - 1) * limit

    companies = db.query(Company).options(joinedload(Company.profile)).filter(
        Company.name.contains(search))
    
    company_count = companies.count()

    companies_object = companies.limit(limit).offset(skip).all()
    
    if len(companies_object) < 1: 
        raise NotFoundException('No Companies found')
    return {'message': 'Company list retrieved successfully', 'total_count': company_count,'count': len(companies_object), 'next_page': page + 1, 'data': companies_object}


@router.get("/companies/{company_id}", response_model=CustomResponse[BaseCompany], tags=["Companies"])
async def fetch_company(
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
    
    if current_user.role == UserType.CANDIDATE:
        raise UnauthorisedUserException("You are not authorized to create company profiles")
    
    #TODO: Refactor to utils
    slug = slugify(payload.name, max_length=15, word_boundary=True, 
                separator=".", stopwords=['the', 'and', 'of'])

    if current_user.role == UserType.ADMIN:
        if not payload.client_id:
            raise BadRequestException("Kindly pass client id")
        user_query = db.query(User).filter(User.id == payload.client_id)
    else:
        user_query = db.query(User).filter(User.id == current_user.id)


    company = db.query(Company).filter(Company.slug == slug).first()

    if company:
        # Contact company owner message, reach out to support email
        raise DuplicateCompanyException
    
    user_object = user_query.first()
    if user_object is None:
        raise NotFoundException('No such client')
    
    new_company = Company(**payload.dict(exclude={'client_id'}))
    new_company.slug = slug
    new_company.owner_id = user_object.id
    new_company.secret_key = secrets.token_urlsafe()
    db.add(new_company)
    db.commit()
    # update related models
    user_object.company_id = new_company.id
    new_company_profile = CompanyProfile(company_id=new_company.id)
    new_company_profile.updated_at = datetime.now()
    db.add(new_company_profile)
    db.commit()

    db.refresh(new_company)
    return {'message': 'Company created successfully', 'data': BaseCompany.from_orm(new_company)}   

@router.patch('/companies/{company_id}', response_model=CustomResponse[BaseCompany], tags=["Companies"])
async def update_company_profile(company_id: Annotated[UUID, Path(title="The ID of the company to be updated")],
                                 payload: UpdateCompanySchema,
               current_user: Annotated[BaseUser, Depends(get_current_user)],
               db: Session = Depends(get_db),):
    
    if current_user.role == UserType.CANDIDATE:
        raise UnauthorisedUserException("User is not authorised to edit company details")
    
    if current_user.role == UserType.ADMIN: 
        if not payload.client_id:
            raise BadRequestException("Kindly pass client id")
        user_query = db.query(User).filter(User.id == payload.client_id)
    else:
        user_query = db.query(User).filter(User.id == current_user.id)

    user = user_query.first()
    if user is None:
        raise NotFoundException('No such client')

    
    company_query = db.query(Company).filter(Company.id == company_id)
    company = company_query.first()

    if company is None:
        raise NotFoundException("Company not found!")
    

    if company.id != company_id:
        raise UnauthorisedUserException("User is not authorised to edit this company details")
    
    
    company_query.update(payload.dict(exclude={'profile', 'client_id'},exclude_unset=True), synchronize_session=False)
    if payload.profile != None:
        company_profile_query = db.query(CompanyProfile).filter(CompanyProfile.company_id == company_id)
        company_profile_query.update(payload.profile.dict(exclude={'company_id'}, exclude_unset=True), synchronize_session=False)
    
    db.commit()
    
    return {"message":"Company profile updated successfully","data": company}


@router.patch('/profile', response_model=CustomResponse[BaseUser],
            #   response_model_exclude_none=True, 
              tags=["User"])
async def update_user_profile(payload: Optional[UpdateUserProfile],
               current_user: Annotated[BaseUser, Depends(get_current_user)],
               db: Session = Depends(get_db),):
    
    user_query = db.query(User)
    
    if current_user.role == UserType.CANDIDATE:
        user = user_query.options(joinedload(User.candidate_profile)).filter(User.id == current_user.id).first()
        candidate_query = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id)
        candidate = candidate_query.first()
        
        if candidate is None and payload.candidate_profile == None:
            new_profile = CandidateProfile(user_id = current_user.id, updated_at = datetime.now())
            db.add(new_profile)
        elif candidate is None and payload.candidate_profile != None:
            new_profile = CandidateProfile(**payload.candidate_profile.dict())
            new_profile.user_id = current_user.id
            new_profile.updated_at = datetime.now()
            db.add(new_profile)
        elif candidate is not None and payload.candidate_profile != None:
            candidate_query.update(payload.candidate_profile.dict(exclude_unset=True))

    elif current_user.role == UserType.CLIENT:
        user = user_query.options(joinedload(User.client_profile)).filter(User.id == current_user.id).first()
        client_query = db.query(ClientProfile).filter(ClientProfile.user_id == current_user.id)
        client = client_query.first()

        if client is None and payload.client_profile == None:
            new_profile = ClientProfile(user_id = current_user.id, updated_at = datetime.now())
            db.add(new_profile)
        elif client is None and payload.client_profile != None:
            new_profile = ClientProfile(**payload.client_profile.dict())
            new_profile.user_id = current_user.id
            new_profile.updated_at = datetime.now()
            db.add(new_profile)
        elif client is not None and payload.client_profile != None:
            client_query.update(payload.client_profile.dict(exclude_unset=True))
    

    
    if user is None:
        raise NotFoundException("User not found!")
    if payload.first_name:
        user.first_name = payload.first_name
    if payload.last_name:
        user.last_name=payload.last_name 
    if payload.photo:
        user.photo= payload.photo
        
    db.commit()
    db.refresh(user)
    
    return {"message":"User profile updated successfully","data": user}


@router.patch('/profile/{user_id}', response_model=CustomResponse[BaseUser],
            #   response_model_exclude_none=True, 
              tags=["User"])
async def admin_update_user_profile(
    user_id: Annotated[UUID, Path(title="The ID of the job to be updated")],
    payload: Optional[UpdateUserProfile],
               current_user: Annotated[BaseUser, Depends(get_current_user)],
               db: Session = Depends(get_db),):
    
    if current_user.role != UserType.ADMIN:
        raise UnauthorisedUserException("User is not authorised to access this view")
    
    user_query = db.query(User)

    user_object = user_query.filter(User.id == user_id).first()

    if user_object is None:
        raise NotFoundException("User not found!")
    
    if user_object.role == UserType.CANDIDATE:
        user = user_query.options(joinedload(User.candidate_profile)).filter(User.id == user_object.id).first()
        candidate_query = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_object.id)
        candidate = candidate_query.first()
        
        if candidate is None and payload.candidate_profile == None:
            new_profile = CandidateProfile(user_id = user_object.id, updated_at = datetime.now())
            db.add(new_profile)
        elif candidate is None and payload.candidate_profile != None:
            new_profile = CandidateProfile(**payload.candidate_profile.dict())
            new_profile.user_id = user_object.id
            new_profile.updated_at = datetime.now()
            db.add(new_profile)
        elif candidate is not None and payload.candidate_profile != None:
            candidate_query.update(payload.candidate_profile.dict(exclude_unset=True))

    elif user_object.role == UserType.CLIENT:
        user = user_query.options(joinedload(User.client_profile)).filter(User.id == user_object.id).first()
        client_query = db.query(ClientProfile).filter(ClientProfile.user_id == user_object.id)
        client = client_query.first()

        if client is None and payload.client_profile == None:
            new_profile = ClientProfile(user_id = user_object.id, updated_at = datetime.now())
            db.add(new_profile)
        elif client is None and payload.client_profile != None:
            new_profile = ClientProfile(**payload.client_profile.dict())
            new_profile.user_id = user_object.id
            new_profile.updated_at = datetime.now()
            db.add(new_profile)
        elif client is not None and payload.client_profile != None:
            client_query.update(payload.client_profile.dict(exclude_unset=True))
    

    
    # if user is None:
    #     raise NotFoundException("User not found!")
    if payload.first_name:
        user.first_name = payload.first_name
    if payload.last_name:
        user.last_name=payload.last_name 
    if payload.photo:
        user.photo= payload.photo
        
    db.commit()
    db.refresh(user)
    
    return {"message":"User profile updated successfully","data": user}

# Admin Use
@router.delete('/{company_id}', response_model=CustomResponse, tags=["Companies"])
async def delete_company(company_id: Annotated[UUID, Path(title="The ID of the company to be deleted")],
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
# TODO: 
# CRUD Users
# - Candidates profile