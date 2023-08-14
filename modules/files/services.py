from datetime import datetime
from typing import Annotated, List
from uuid import UUID
from slugify import slugify


from fastapi import Depends, status, APIRouter, File, UploadFile
from sqlalchemy.orm import Session, joinedload

from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user
from core.exceptions import NotFoundException, BadRequestException
from core.helpers.schemas import CustomListResponse, CustomResponse

from .models import Company, CompanyProfile, User, UserType
from .schemas import BaseUser, BaseCompany, CreateCompanySchema, UpdateCompanySchema

router = APIRouter(
    prefix="/files",
)

@router.get("/", response_model=CustomListResponse, tags=["Files"])
async def fetch_my_files(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = '', 
                          current_user: str = Depends(get_current_user)):
    skip = (page - 1) * limit

    companies = db.query(Company).options(joinedload(Company.profile)).filter(
        Company.name.contains(search)).limit(limit).offset(skip).all()
    
    if len(companies) < 1: 
        raise NotFoundException('No Companies found')
    return {'message': 'Company list retrieved successfully', 'count': len(companies),'data': companies}


@router.post("/upload", response_model=CustomListResponse, tags=["Files"])
async def create_upload_file(file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}


# @router.po("/", response_model=CustomListResponse, tags=["Files"])
# async def fetch_my_files(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = '', 
#                           current_user: str = Depends(get_current_user)):
#     pass