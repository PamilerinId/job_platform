from pydantic import constr, BaseModel, Field, EmailStr
from services.users.schemas import CreateUser
from typing_extensions import Annotated


class RegisterUserSchema(CreateUser):
    password: Annotated[str, constr(min_length=8)]


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: Annotated[str, constr(min_length=8)]

class RefreshTokenSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")

class PasswordResetRequestSchema(BaseModel):
    email: EmailStr
    
class PasswordChangeSchema(BaseModel):
    password: Annotated[str, constr(min_length=8)]

