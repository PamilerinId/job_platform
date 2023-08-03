from pydantic import BaseModel, Field, EmailStr, constr
from services.users.schemas import CreateUser


class RegisterUserSchema(CreateUser):
    password: constr(min_length=8)


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class RefreshTokenSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")

class PasswordResetRequestSchema(BaseModel):
    email: EmailStr
    
class PasswordChangeSchema(BaseModel):
    password: constr(min_length=8)

