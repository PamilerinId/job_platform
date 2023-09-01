from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from pydantic import ConfigDict, BaseModel, Field, constr


from modules.jobs.enums import *
from modules.users.schemas import BaseCompany, BaseCandidate, BaseUser

class BaseJob(BaseModel):
    id: Optional[UUID] = None
    title: str = Field(index=True)
    description: str
    type: Optional[JobType] = None
    status: JobStatus
    experienceLevel: Optional[ExperienceLevel] = None
    location: str
    locationType: Optional[LocationType] = None
    qualifications: Optional[List[Qualification]] = None
    currency: Optional[Currency] = None
    salaryRangeFrom: int
    salaryRangeTo: int
    skills: List[str]
    benefits: List[str]
    deadline: Optional[datetime] = None #datetime

    tags: List[str]
    company: BaseCompany
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

class CreateJobSchema(BaseModel):
    title: str = Field(index=True)
    description: str
    type: Optional[JobType] = None
    experienceLevel: Optional[ExperienceLevel] = None
    location: str
    locationType: Optional[LocationType] = None
    qualifications: Optional[List[Qualification]] = None
    currency: Optional[Currency] = None
    salaryRangeFrom: int
    salaryRangeTo: int
    skills: List[str]
    benefits: List[str]
    # deadline: str


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
    model_config = ConfigDict(from_attributes=True)



# Applications
class BaseApplication(BaseModel):
    id: Optional[UUID] = None
    status: ApplicationStatus
    job: BaseJob
    applicant: BaseUser
    comment: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class UpdateApplication(BaseModel):
    status: Optional[ApplicationStatus] = None
    job_id: Optional[UUID] = None
    applicant_id: Optional[UUID] = None
    comment: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)