from datetime import timedelta, datetime
from typing import Annotated
from core.exceptions.auth import UnauthorisedUserException
from pydantic import TypeAdapter
from core.exceptions.base import BadRequestException, DuplicateValueException, ForbiddenException, NotFoundException
from fastapi import Depends, HTTPException, status, APIRouter, Response, Path
from modules.files.models import File, FileType
from modules.files.schemas import File as FileSchema
from modules.users.models import UserType
from modules.users.schemas import BaseClient, BaseUser
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user
from core.helpers.schemas import CustomResponse, CustomListResponse
from core.helpers.text_utils import to_slug

from modules.users.models import Company, CompanyProfile

from .models import Job, Application
from .schemas import *
from .repository import JobAssessmentRepository

router = APIRouter(
    prefix="/jobs"
)

jobAssessmentRepo = JobAssessmentRepository()


@router.get("/", response_model=CustomListResponse[BaseJob], tags=["Jobs"])
async def fetch_jobs(current_user: Annotated[BaseUser, Depends(get_current_user)],
                     db: Session = Depends(get_db), 
                     limit: int = 10, page: int = 1, search: str = ''):
    
    skip = (page - 1) * limit
    jobs_query = db.query(Job).options(joinedload(Job.company).joinedload(Company.profile))
    # if user is candidate; get industry related tags
    if (current_user.role == UserType.CANDIDATE):
        jobs_query = db.query(Job).options(
            joinedload(Job.company)
            .joinedload(Company.profile)).filter(Job.status == JobStatus.ACTIVE)
        if search:
            jobs_query.filter(
            Job.tags.contains([search]))
    # if user is client; filter by company jobs
    # elif(current_user.user.role == UserType.CLIENT):
    elif(current_user.role == UserType.CLIENT):
        # print('HEERE', current_user.client_profile.company, flush=True)
        company = db.query(Company).options(
                joinedload(Company.profile)).filter(Company.owner_id == str(current_user.id)).first()
        if company:
            current_user.client_profile.company = company
        # print('HEERE', current_user.client_profile.company.id, flush=True)
        if current_user.client_profile and current_user.client_profile.company:
            # print('HEERE2', current_user.client_profile.company,  flush=True)
            jobs_query = db.query(Job).options(
                joinedload(Job.company).joinedload(Company.profile)).filter(
                Job.company_id == current_user.client_profile.company.id)
        else:
            return {'message': 'You have created no Jobs'}
            # raise NotFoundException('You have created no Jobs')
    # if no user; no jobs
    # if thirdparty; filter tier [distinct user]
    jobs = jobs_query.order_by(Job.created_at.desc()).limit(limit).offset(skip).all()
    total_count = jobs_query.count()
    if len(jobs) < 1: 
        raise NotFoundException('No Jobs found')
    return {'message': 'Jobs retrieved successfully', 'total_count': total_count, 'next_page': 1,'count': len(jobs), 'data': jobs}

@router.get("/recommended", response_model=CustomListResponse[BaseJob], tags=["Jobs"])
async def fetch_recommended_jobs(current_user: Annotated[BaseUser, Depends(get_current_user)],
                     db: Session = Depends(get_db)):

    # if user is candidate; get industry related tags
    jobs_query = db.query(Job).options(joinedload(Job.company).joinedload(Company.profile))

    if current_user.candidate_profile:
        jobs_query.filter(
            Job.tags.contains([current_user.candidate_profile.skills]),
            Job.status == JobStatus.ACTIVE)
    
    jobs = jobs_query.order_by(Job.deadline.desc()).limit(5).all()
    job_count = jobs_query.count()
    if len(jobs) < 1: 
        raise NotFoundException('No Jobs found')
    return {'message': 'Jobs retrieved successfully', 'total_count': job_count, 'next_page': 1,'count': len(jobs), 'data': jobs}

@router.get('/applications', response_model=CustomListResponse[BaseApplication], tags=["Applications"])
async def get_candidate_applications(current_user: Annotated[BaseUser, Depends(get_current_user)],
                                db: Session = Depends(get_db),):
    '''
    Candidate:
    if just applications; get all the applications of the candidate
    if appended with job id return job_id and appliication [possibly unnecessary]
    '''
    if (current_user.role == UserType.CLIENT):
        raise BadRequestException("Get applications by job!")
    
    query = db.query(Application).filter(Application.applicant_id==current_user.id)
    applications = query.all()
    # elif current_user.role == UserType.CLIENT: # check if client -> company -> job -> application ownership
    #     query = db.query(Application).filter(Application.job_id)
    if len(applications) < 1:
        raise NotFoundException("No Applications Found")
    return {"message":"Applications retrieved successful","count": len(applications),"data": applications}


@router.get('/{job_id}', tags=["Jobs"], response_model=CustomResponse[BaseJob])
def get_job(job_id: Annotated[UUID, Path(title="The ID of the job to be fetched")],
            current_user: Annotated[BaseUser, Depends(get_current_user)],
            db: Session = Depends(get_db),):
    
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if job is None:
        raise NotFoundException("Job not found!")
    
    return {"message":"Job fetched successfully","data": job}


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=CustomResponse[BaseJob], tags=["Jobs"])
def create_job(payload: CreateJobSchema,
                   current_user: Annotated[BaseUser, Depends(get_current_user)],
                   db: Session = Depends(get_db), ):
    
    #TODO: Refactor to utils
    # TODO: update tags with field slugs
    if current_user.role == UserType.CANDIDATE:
        raise ForbiddenException("User not authorised to create jobs")
    

    if current_user.role == UserType.ADMIN:
        company = db.query(Company).filter(Company.id == str(payload.company_id)).first()
    else:
        company = db.query(Company).filter(Company.owner_id == str(current_user.id)).first()

    # company = db.query(Company).filter(Company.owner_id == str(current_user.id)).first()
    if company is None:
        raise BadRequestException('Please complete company profile')
    title_slug = to_slug(payload.title)
    job = db.query(Job).filter(Job.company_id == company.id ,Job.slug == title_slug).first()
    if job:
        # Contact company owner message, reach out to support email
        raise DuplicateValueException("There may be a similar job ad already created by your company, Check 'All Jobs' tab")
    
    new_job = Job(**payload.__dict__)
    new_job.slug = title_slug
    new_job.tags = [title_slug, to_slug(payload.type), to_slug(payload.title), to_slug(payload.title)]
    new_job.company_id = company.id
    new_job.updated_at = datetime.now()
    new_job.deadline = datetime.now() + timedelta(days=10)
    new_job.status =  JobStatus.ACTIVE
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {"message":"Job ad draft has been created successfully","data": BaseJob.from_orm(new_job)}

@router.put('/{job_id}', response_model=CustomResponse[BaseJob] , tags=["Jobs"])
def update_job(job_id: Annotated[UUID, Path(title="The ID of the job to be updated")],
               payload: UpdateJobSchema,
               current_user: Annotated[BaseUser, Depends(get_current_user)],
               db: Session = Depends(get_db),):
    

    if current_user.role == UserType.ADMIN:
        company = db.query(Company).filter(Company.id == str(payload.company_id)).first()
    else:
        company = db.query(Company).filter(Company.owner_id == str(current_user.id)).first()
    
    job_query = db.query(Job).options(
        joinedload(Job.company)
        .joinedload(Company.profile)).filter(Job.id == job_id,
        Job.company_id == company.id)
    job = job_query.first()
    if job is None:
        raise NotFoundException("Job not found!")
    
    job_query.update(payload.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    
    return {"message":"Job updated successfully","data": job}

@router.patch('/publish/{job_id}', response_model=CustomResponse[BaseJob] , tags=["Jobs"])
def publish_job(job_id: Annotated[UUID, Path(title="The ID of the job to be updated")],
               current_user: Annotated[BaseUser, Depends(get_current_user)],
               db: Session = Depends(get_db),):
    
    # if current_user.role == UserType.ADMIN:
    #     company = db.query(Company).filter(Company.id == str(payload.company_id)).first()
    # else:
    #     company = db.query(Company).filter(Company.owner_id == str(current_user.id)).first()

    # if company is None:
    #     raise BadRequestException('Please complete company profile')


    if current_user.role == UserType.CANDIDATE:
        raise UnauthorisedUserException("User is not authorised to edit company details")

    job_query = db.query(Job).options(
        joinedload(Job.company)
        .joinedload(Company.profile)).filter(Job.id == job_id)
    
    job = job_query.first()
    if job is None:
        raise NotFoundException("Job not found!")
    
    if job.status == JobStatus.ACTIVE:
        raise BadRequestException('Job is already published')
    
    if job.status == JobStatus.CLOSED:
        raise BadRequestException('Job Deadline is past, contact support or create a new job')
    
    job_query.update({'status':JobStatus.ACTIVE}, synchronize_session=False)
    db.commit()
    
    return {"message":"Job updated successfully","data": job}

# Admin Use
@router.delete('/{job_id}', response_model=CustomResponse, tags=["Jobs"])
async def delete_job(job_id: Annotated[UUID, Path(title="The ID of the job to be deleted")],
               current_user: Annotated[BaseUser, Depends(get_current_user)],
               db: Session = Depends(get_db),):
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise NotFoundException("Job not found!")
    try:
        db.delete(job)
        db.commit()
        return {"message": "Job deleted"}
    except BadRequestException:
        db.rollback()
        raise BadRequestException("Job delete failed")
    


@router.post('/{job_id}/apply', response_model=CustomResponse[BaseApplication], tags=["Applications"])
async def create_application(job_id: Annotated[UUID, Path(title="The ID of the job, applied to")],
                             current_user: Annotated[BaseUser, Depends(get_current_user)],
                                db: Session = Depends(get_db),):
    # only candidate can apply
    if (current_user.role != UserType.CANDIDATE):
        raise ForbiddenException('Only candidates are allowed!')
    
    # check if job is live
    job  = db.query(Job).filter(Job.id==job_id).first()
    if (job is None) or (job.status != JobStatus.ACTIVE):
        raise NotFoundException("Job does not exist or has been closed.")

    application_query = db.query(Application).filter(Application.job_id == job_id,
                                                      Application.applicant_id == current_user.id).first()
    if application_query:
        raise DuplicateValueException("You may have applied for this job")
    
    if current_user.candidate_profile is None:
        raise BadRequestException("Candidate profile is incomplete, complete profile to apply")
    
    new_app = Application(**{"status":ApplicationStatus.PENDING,
                             "job_id" : job_id,
                             "applicant_id":current_user.id,
                             "comment": 'Application started'})
    new_app.updated_at = datetime.now()
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return {"message":"Job application successful","data": new_app}

@router.get('/{job_id}/applications', response_model=CustomListResponse[BaseApplication], tags=["Applications"])
async def get_job_applications(job_id: Annotated[Optional[UUID], Path(title="The ID of the jobs to fetch applications")],
                             current_user: Annotated[BaseUser, Depends(get_current_user)],
                                db: Session = Depends(get_db),):
    '''
     CLient:
    if just applications; get all your job related applications [may be more complicated and unnecessary]
    if appended with job id return the applications for those jobs
    '''
    if (current_user.role == UserType.CANDIDATE):
        raise BadRequestException('Check applications!')
    
    # check if job exists
    job  = db.query(Job).filter(Job.id==job_id).first()
    if (job is None) or (job.status == JobStatus.CLOSED):
        raise NotFoundException("Job does not exist or has been closed.")

    
    application_query = db.query(Application).options(
                                    joinedload(Application.job))
    
    if current_user.role == UserType.ADMIN:
        application_query = application_query.filter(Application.job_id == str(job.id))
    elif current_user.role == UserType.CLIENT: 
        company = db.query(Company).filter(Company.owner_id == str(current_user.id)).first()
        if company is None:
            raise ForbiddenException("You dont seem to have a company profile, contact support")
        application_query = application_query.filter(Application.job_id == job_id, Job.company_id == company.id, Application.status == ApplicationStatus.SHORTLISTED)#, Application.status == ApplicationStatus.SHORTLISTED)

    total_count = application_query.count()
    applications = application_query.all()
    if len(applications) < 1:
        # raise NotFoundException("No Applications Found")
        return {"message":"No Applications Found!"}

    
    for application in applications:
        cv_files = db.query(File).filter(
            File.owner_id == application.applicant.id, File.type == FileType.RESUME)\
            .order_by(File.created_at.desc()).limit(3).all()
        application.applicant.candidate_profile.cv = TypeAdapter(List[FileSchema]).validate_python(cv_files)
        
    return {"message":"Applications retrieved successful","count": len(applications), "total_count": len(applications), "data": applications}

@router.put('/applications/{application_id}', response_model=CustomResponse[BaseApplication], tags=["Applications"])
async def update_application(application_id: Annotated[UUID, Path(title="The ID of the application to be updated")],
                             payload: UpdateApplication,
                             current_user: Annotated[BaseUser, Depends(get_current_user)],
                                db: Session = Depends(get_db),):
    if current_user == UserType.CANDIDATE:
        raise ForbiddenException('You are not allowed to update this application!')

    application_query = db.query(Application).filter(or_(Application.id == application_id, Application.applicant_id == current_user.id))
    application = application_query.first()

    if application is None:
        raise NotFoundException("Application not found!")
    
    application_query.update(payload.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    
    return {"message":"Application updated successfully","data": application}

@router.put('/applications/shortlist/{application_id}', response_model=CustomResponse[BaseApplication], tags=["Applications"])
async def shortlist_application(application_id: Annotated[UUID, Path(title="The ID of the application to be updated")],
                             current_user: Annotated[BaseUser, Depends(get_current_user)],
                                db: Session = Depends(get_db),):
    if current_user == UserType.CANDIDATE:
        raise ForbiddenException('You are not allowed to update this application!')

    application_query = db.query(Application).filter(Application.id == application_id)
    application = application_query.first()

    if application is None:
        raise NotFoundException("Application not found!")
    
    if application.status == ApplicationStatus.SHORTLISTED:
        raise BadRequestException("This application has already been shortlisted.")
    
    application_query.update({'status': ApplicationStatus.SHORTLISTED}, synchronize_session=False)
    db.commit()
    
    return {"message":"Application updated successfully","data": application}

# Admin use
@router.delete('/applications/{application_id}', response_model=CustomResponse, tags=["Applications"])
async def delete_application(application_id: Annotated[UUID, Path(title="The ID of the application to be deleted")],
                             current_user: Annotated[BaseUser, Depends(get_current_user)],
                                db: Session = Depends(get_db),):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application is None:
        raise NotFoundException("Application not found!")
    try:
        db.delete(application)
        db.commit()
        return {"message": "Application deleted successfully"}
    except BadRequestException:
        db.rollback()
        raise BadRequestException("Application delete failed")

# fetch applications
#  candidate / clients / jobs









#Job Assessments
@router.get('/{job_id}/assessments', response_model=CustomListResponse[BaseJobAssessment],  tags=["Job Assessments", "Jobs"])
async def fetch_job_assessments(job_id: Annotated[UUID, Path(title="The ID of the job to be fetched")],
                            current_user: Annotated[BaseUser, Depends(get_current_user)],
                            limit: int = 10, page: int = 1, search: str = '',
                            db: Session = Depends(get_db)
                            ):
    
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if job is None:
        raise NotFoundException("Job not found!")
    
    jobAssessments = await jobAssessmentRepo.get_by_job(page=page, limit=limit, filter=search, job_id=job_id)

    return {'message': 'Assessments retrieved successfully', 'count': len(jobAssessments), 'data': jobAssessments}


@router.post('/{job_id}/assessments', response_model=CustomResponse[BaseJobAssessment], tags=["Job Assessments", "Jobs"])
async def create_job_assessment(job_id: Annotated[UUID, Path(title="The ID of the job to be fetched")], payload: CreateJobAssessment,
                                current_user: Annotated[BaseUser, Depends(get_current_user)],
                                db: Session = Depends(get_db),):
    
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if job is None:
        raise NotFoundException("Job not found!")
    
    
    jobAssessment = await jobAssessmentRepo.create(payload=payload)
    
    return {"message": 'Job assessment created successfully', 'data': jobAssessment}


@router.put('/{job_id}/assessments/{job_assessment_id}', response_model=CustomListResponse[BaseJobAssessment], tags=["Job Assessments", "Jobs"])
async def update_job_assessment(job_id: Annotated[UUID, Path(title="The ID of the job to be updated")], job_assessment_id: Annotated[UUID, Path(title="The ID of the job assessments to be updated")],
                            payload: BaseJobAssessment,
                            current_user: Annotated[BaseUser, Depends(get_current_user)]):
    
    await jobAssessmentRepo.get_by_id(job_assessment_id=job_assessment_id)
    jobAssessment = await jobAssessmentRepo.update(payload=payload)
    
    return {'message': 'Job Assessment updated successfully', 'data': jobAssessment}


@router.delete('/{job_id}/assessments/{job_assessment_id}', response_model=CustomResponse, tags=["Job Assessments", "Jobs"])
async def delete_job_assessment(job_id: Annotated[UUID, Path(title="The ID of the job to be updated")], 
                            job_assessment_id: Annotated[UUID, Path(title="The ID of the job assessments to be updated")],
                            current_user: Annotated[BaseUser, Depends(get_current_user)]):
    
    await jobAssessmentRepo.delete(job_id=job_id, job_assessment_id=job_assessment_id)
    
    return {'message': 'Job Assessment deleted successfully'}




