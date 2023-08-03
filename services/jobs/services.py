from typing import Annotated
from core.exceptions.base import DuplicateValueException, NotFoundException
from fastapi import Depends, HTTPException, status, APIRouter, Response
from services.users.models import UserType
from services.users.schemas import BaseUser
from sqlalchemy.orm import Session

from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user
from core.helpers.schemas import CustomResponse, CustomListResponse
from core.helpers.text_utils import to_slug

from .models import Job, Application
from .schemas import *

router = APIRouter(
    prefix="/jobs",
)


@router.get("/", response_model=CustomListResponse[BaseJob], tags=["Jobs"])
async def fetch_jobs(current_user: Annotated[BaseUser, Depends(get_current_user)],
                     db: Session = Depends(get_db), 
                     limit: int = 10, page: int = 1, search: str = ''):
    
    skip = (page - 1) * limit

    # if user is candidate; get industry related tags
    if (current_user.role == UserType.CANDIDATE):
        jobs_query = db.query(Job).group_by(Job.id).filter(
            Job.tags.contains([search]))
    # if user is client; filter by company jobs
    elif(current_user.role == UserType.CLIENT):
        jobs_query = db.query(Job).group_by(Job.id).filter(
            Job.company_id == current_user.company.id)
    # if no user; no jobs
    # if thirdparty; filter tier [distinct user]
    jobs = jobs_query.limit(limit).offset(skip).all()
    if len(jobs) < 1: 
        raise NotFoundException('No Jobs found')
    return {'message': 'Jobs retrieved successfully', 'data': jobs}


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=CustomResponse[BaseJob], tags=["Jobs"])
def create_job(payload: CreateJobSchema,
                   current_user: Annotated[BaseUser, Depends(get_current_user)],
                   db: Session = Depends(get_db), ):
    
    #TODO: Refactor to utils
    # TODO: update tags with field slugs
    title_slug = to_slug(payload.title)
    job = db.query(Job).filter(Job.company_id == current_user.company.id ,Job.slug == title_slug).first()
    if job:
        # Contact company owner message, reach out to support email
        raise DuplicateValueException
    
    new_job = Job(**payload.__dict__)
    new_job.slug = title_slug
    new_job.tags.append(title_slug, to_slug(payload.type), to_slug(payload.title), to_slug(payload.title))
    new_job.company_id = current_user.company.id
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {"message":"Job ad draft has been created successfully","data": new_job}

@router.patch('/')
def update_job():
    pass
# patch job
# create application [apply to job]
# fetch applications
#  candidate / clients / jobs
# update application status