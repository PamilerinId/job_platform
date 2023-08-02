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
    qualifications: Optional[Qualification]
    currency: Optional[Currency]
    salaryRangeFrom: int
    salaryRangeTo: int
    skills: List[str]
    benefits: List[str]
    deadline: str #datetime

    tags: List[str]
    company: BaseCompany

    class Config:
        from_attributes=True
        validate_assignment = True

class CreateJobSchema(BaseJob):
    id: None
    pass



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