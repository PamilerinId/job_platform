from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from core.dependencies.sessions import get_db
from core.exceptions.base import BadRequestException, NotFoundException
from .models import JobAssessment
from .schemas import CreateJobAssessment, BaseJobAssessment 


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
    
    

class JobAssessmentRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()
        
    async def get_list(self, page: int, limit: int, filter: str):
        skip = (page - 1) * limit

        jobAssessments = self.db.query(JobAssessment
                                    ).limit(limit).offset(skip).all()

        if len(jobAssessments) is None:
            raise NotFoundException("No Job Assessments found!")
        
        return jobAssessments
    
    
    async def get_by_id(self, job_assessment_id: UUID):
        jobAssessment = self.db.query(JobAssessment).filter(JobAssessment.id==job_assessment_id).first()
        
        if jobAssessment is None:
            raise NotFoundException("Job assessment not found!")
        
        return jobAssessment
    
    
    
    async def get_by_job(self, page: int, limit: int, filter: str, job_id: UUID):
        skip = (page - 1) * limit
        jobAssessments = self.db.query(JobAssessment).filter(JobAssessment.job_id==job_id).all()
                                                        
        if jobAssessments is None:
            raise NotFoundException("No Job assessments found!")
        return jobAssessments
    
        
    async def create(self, payload: CreateJobAssessment):
        job_assessment_obj = self.db.query(JobAssessment).filter(JobAssessment.assessment_id == payload.assessment_id).all()
        
        if len(job_assessment_obj):
            raise BadRequestException("Assessment has already been selected for this job!")
            
        new_jobAssemssent = JobAssessment(**payload.__dict__)
        
        self.db.add(new_jobAssemssent)
        self.db.commit()
        self.db.refresh(new_jobAssemssent)
        
        return new_jobAssemssent
    
    async def update(self, payload: BaseJobAssessment):
        job_assessment_obj = self.db.query(JobAssessment).filter(JobAssessment.assessment_id == payload.assessment_id).first()
        
        if job_assessment_obj:
            raise BadRequestException("Assessment has already been selected for this job!")
        
        print("here")
        jobAssessment = self.db.query(JobAssessment).filter(JobAssessment.id == payload.id)
        jobAssessment.update(payload.__dict__, synchronize_session=False)
        
        self.db.commit()
        
        return jobAssessment
    
    
    async def delete(self, job_id: UUID, job_assessment_id: UUID):
        self.get_by_id(job_id)
        jobAssessment = self.db.query(JobAssessment).filter(JobAssessment.id == job_assessment_id).first()
        
        try:
            self.db.delete(jobAssessment)
            self.db.commit()
            return {"message": "Job assessment deleted successfully"}
        except BadRequestException:
            self.db.rollback()
            raise BadRequestException("Job assessment delete failed")
