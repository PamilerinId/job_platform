from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, constr


from services.jobs.enums import *
from services.users.schemas import BaseCompany, BaseCandidate

class BaseJob(BaseModel):
    id: Optional[UUID] = None
    title: str = Field(index=True)
    description: str
    type: Optional[JobType]
    status: JobStatus
    experienceLevel: Optional[ExperienceLevel]
    location: str
    locationType: Optional[LocationType]
    qualifications: Optional[List[Qualification]]
    currency: Optional[Currency]
    salaryRangeFrom: int
    salaryRangeTo: int
    skills: List[str]
    benefits: List[str]
    deadline: Optional[datetime] #datetime

    tags: List[str]
    company: BaseCompany

    class Config:
        from_attributes=True
        validate_assignment = True

class CreateJobSchema(BaseModel):
    title: str = Field(index=True)
    description: str
    type: Optional[JobType]
    status: JobStatus
    experienceLevel: Optional[ExperienceLevel]
    location: str
    locationType: Optional[LocationType]
    qualifications: Optional[List[Qualification]]
    currency: Optional[Currency]
    salaryRangeFrom: int
    salaryRangeTo: int
    skills: List[str]
    benefits: List[str]
    deadline: str


class UpdateJobSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str]= None
    type: Optional[JobType]= None
    status: Optional[JobStatus]= None
    experienceLevel: Optional[ExperienceLevel]= None
    location: Optional[str]= None
    locationType: Optional[LocationType]= None
    qualifications: Optional[List[Qualification]]= None
    currency: Optional[Currency]= None
    salaryRangeFrom: Optional[int]= None
    salaryRangeTo: Optional[int]= None
    skills: Optional[List[str]]= None
    benefits: Optional[List[str]]= None

    class Config:
        from_attributes=True



# Applications
class BaseApplication(BaseModel):
    id: Optional[UUID] = None
    status: ApplicationStatus
    job: BaseJob
    applicant: BaseCandidate
    comment: Optional[str]

    class Config:
        from_attributes=True
        validate_assignment = True


class UpdateApplication(BaseModel):
    status: Optional[ApplicationStatus] = None
    job_id: Optional[UUID] = None
    applicant_id: Optional[UUID] = None
    comment: Optional[str] = None

    class Config:
        from_attributes=True
        validate_assignment = True