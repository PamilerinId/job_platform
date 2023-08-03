from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, EmailStr, constr, HttpUrl, validator


from services.users.models import CompanySize, UserType

class CompanyProfile(BaseModel):
    id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    address: str
    location: str
    website : Optional[HttpUrl]
    support_mail: Optional[EmailStr]
    linkedin_url: Optional[HttpUrl]
    funding: Optional[str]
    size: Optional[CompanySize]

class BaseCompany(BaseModel):
    id: Optional[UUID] = None
    name: str = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    profile: Optional[CompanyProfile]

    class Config:
        from_attributes=True

    # @validator("id", "logo_url")
    # def validate_uuids(cls, value):
    #     if value:
    #         return str(value)
    #     return value

class CreateCompanySchema(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str]

    class Config:
        from_attributes=True
        validate_assignment = True
    
    # @validator("logo_url")
    # def validate_uuids(cls, value):
    #     if value:
    #         return str(value)
    #     return value

class UpdateCompanySchema(BaseModel):
    name: str
    description: str
    logo_url: HttpUrl
    profile: CompanyProfile 

    class Config:
        from_attributes = True


####################### Users #################
class BaseUser(BaseModel):
    id: Optional[UUID] = None
    email: EmailStr = Field(None, description="email")
    first_name: str = Field(None, description="First Name")
    last_name: str = Field(None, description="Last Name")
    role: Optional[UserType]=None

    class Config:
        from_attributes=True
        validate_assignment = True

class CreateUser(BaseModel):
    email: EmailStr = Field(None, description="email")
    first_name: str = Field(None, description="First Name")
    last_name: str = Field(None, description="Last Name")

    class Config:
        from_attributes=True
        validate_assignment = True

class AuthUser(BaseUser):
    token_type: str = "bearer"
    token: str
    refresh_token: Optional[str] = None

class ListUserResponse(BaseModel):
    status: str
    results: int
    users: List[BaseUser]


class BaseCandidate(BaseModel):
    user: BaseUser
    cv: str

class BaseClient(BaseModel):
    user: BaseUser
    company: Optional[BaseCompany]
    title: str 