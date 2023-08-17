from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from pydantic import field_validator, ConfigDict, BaseModel, Field, EmailStr, constr, HttpUrl


from modules.users.models import CompanySize, UserType

class CompanyProfile(BaseModel):
    id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    address: Optional[str]= None
    location: Optional[str]= None
    website : Optional[str]= None
    support_mail: Optional[EmailStr]= None
    linkedin_url: Optional[str]= None
    funding: Optional[str] = None
    size: Optional[CompanySize] = None
    model_config = ConfigDict(from_attributes=True)


class BaseCompany(BaseModel):
    id: Optional[UUID] = None
    name: str = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    profile: Optional[CompanyProfile] = None
    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", "logo_url")
    @classmethod
    def validate_uuids(cls, value):
        if value:
            return str(value)
        return value

class CreateCompanySchema(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
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
    model_config = ConfigDict(from_attributes=True)


####################### Users #################

class BaseCandidate(BaseModel):
    cv: Optional[str] = None
    phone: Optional[str] = None
    industry_role: Optional[str] = None
    industries: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    current_earnings: Optional[str] = None
    desired_earnings: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

class BaseClient(BaseModel):
    company: Optional[BaseCompany]= None
    title: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
class BaseUser(BaseModel):
    id: Optional[UUID] = None
    email: EmailStr = Field(None, description="email")
    first_name: str = Field(None, description="First Name")
    last_name: str = Field(None, description="Last Name")
    role: Optional[UserType]=None
    client_profile : Optional[BaseClient] = None
    candidate_profile: Optional[BaseCandidate] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class UpdateUserProfile(BaseModel):
    first_name: str = Field(None, description="First Name")
    last_name: str = Field(None, description="Last Name")
    client_profile : Optional[BaseClient] = None
    candidate_profile: Optional[BaseCandidate] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

class CreateUser(BaseModel):
    email: EmailStr = Field(None, description="email")
    first_name: str = Field(None, description="First Name")
    last_name: str = Field(None, description="Last Name")
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    

class AuthUser(BaseUser):
    token_type: str = "bearer"
    token: str
    refresh_token: Optional[str] = None

class ListUserResponse(BaseModel):
    status: str
    results: int
    users: List[BaseUser]

