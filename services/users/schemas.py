from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, EmailStr, constr


from services.users.models import UserType

class BaseCompany(BaseModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    logo_url: Optional[str]

    class Config:
        from_attributes=True
        validate_assignment = True
    
class CreateCompanySchema(BaseCompany):
    pass

class ListCompanyResponse(BaseModel):
    status: str
    results: int
    companies: List[BaseCompany]

class CompanyResponse(BaseCompany):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UpdateCompanySchema(BaseModel):
    name: str
    description: str
    logo_url: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


####################### Users #################
class BaseUser(BaseModel):
    email: EmailStr = Field(None, description="email")
    first_name: str = Field(None, description="First Name")
    last_name: str = Field(None, description="Last Name")
    role: Optional[UserType]=None

    class Config:
        orm_mode = True
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