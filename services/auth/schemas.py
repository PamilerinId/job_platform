from pydantic import BaseModel, Field, EmailStr, constr
from services.users.schemas import BaseUser


class RegisterUserSchema(BaseUser):
    password: constr(min_length=8)
    passwordConfirm: str


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class RefreshTokenSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")

class PasswordChangeSchema(BaseModel):
    password: constr(min_length=8)

