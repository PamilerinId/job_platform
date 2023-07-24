from datetime import timedelta

from fastapi import Depends, HTTPException, status, APIRouter, Response
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.orm import Session

from core.dependencies.sessions import get_db
from core.dependencies.auth import TokenHelper
from core.helpers import password
from core.helpers.schemas import CustomResponse
from core.middlewares.authentication import AuthBackend
from core.env import config
from core.exceptions import *

from services.auth.schemas import LoginUserSchema, RefreshTokenSchema, RegisterUserSchema
from services.users.models import Company, User
from services.users.schemas import *


router = APIRouter(
    prefix="/auth", tags=["Auth"]
)

################### ROUTES ###########################

@router.post("/token", response_model=RefreshTokenSchema)
async def login_for_access_token(
    payload: LoginUserSchema, 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == payload.email.lower()).first()
    if not user:
        raise IncorrectEmailException

    # Check if user verified his email
    # if not user.email_verified:
    #     raise UnauthorisedUserException

    # Check if the password is valid
    if not password.verify_password(payload.password, user.password):
        raise PasswordDoesNotMatchException

    access_token = TokenHelper.encode(jsonable_encoder(BaseUser.from_orm(user)))
    return {"access_token": access_token, "token_type": "bearer"}



'''
    Register Candidate
    - creates candidate user
    - generates JWT token
    - triggers welcome/verification email 
'''
@router.post('/signup', 
             status_code=status.HTTP_201_CREATED, 
             response_model=CustomResponse[AuthUser], 
             response_model_exclude_none=True)
async def create_user(payload: RegisterUserSchema, db: Session = Depends(get_db)):
    # Check if user already exist
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Account already exist')
    # Compare password and passwordConfirm
    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
    #  Hash the password
    payload.password = password.hash_password(payload.password)
    del payload.passwordConfirm
    payload.role = UserType.CANDIDATE
    payload.email = payload.email.lower()
    new_user = User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    data =  { **jsonable_encoder(BaseUser.from_orm(new_user)), 
            "token":TokenHelper.encode(jsonable_encoder(BaseUser.from_orm(new_user)))}
    
    return  {"message": "Candidate registered successfully", "data": data}

'''
    Register Client User
    - creates client user
    - generates JWT token
    - triggers welcome/verification email 
'''
@router.post('/client/signup', 
             status_code=status.HTTP_201_CREATED, 
             response_model=CustomResponse[AuthUser], 
             response_model_exclude_none=True)
async def create_user(payload: RegisterUserSchema, db: Session = Depends(get_db)):
    # Check if user already exist
    user = db.query(User).filter(
        User.email == payload.email.lower()).first()
    if user:
        raise DuplicateEmailException
    # Compare password and passwordConfirm
    if payload.password != payload.passwordConfirm:
        raise PasswordDoesNotMatchException
    #  Hash the password
    payload.password = password.hash_password(payload.password)
    del payload.passwordConfirm
    payload.role = UserType.CLIENT
    payload.email = payload.email.lower()
    new_user = User(**payload.dict())
    # TODO: Refactor to repository
    db.add(new_user)
    await db.commit()
    db.refresh(new_user)
    data =  { **jsonable_encoder(BaseUser.from_orm(new_user)), 
            "token":TokenHelper.encode(jsonable_encoder(BaseUser.from_orm(new_user)))}
    
    return  {"message": "Client registered successfully", "data": data}

'''
Login User
Pass email, password
- fetch user
- validate user
'''
@router.post('/login',
             status_code=status.HTTP_200_OK,
             response_model=CustomResponse[AuthUser], 
             response_model_exclude_none=True)
def login(payload: LoginUserSchema, response: Response, db: Session = Depends(get_db)):
    # Check if the user exist
    user = db.query(User).filter(
        User.email == payload.email.lower()).first()
    if not user:
        raise IncorrectEmailException

    # Check if user verified his email
    # if not user.email_verified:
    #     raise UnauthorisedUserException

    # Check if the password is valid
    if not password.verify_password(payload.password, user.password):
        raise PasswordDoesNotMatchException

    data =  { **jsonable_encoder(BaseUser.from_orm(user)), 
            "token":TokenHelper.encode(jsonable_encoder(BaseUser.from_orm(user)))}
    
    return  {"message": "User logged in successfully", "data": data}


@router.get('/logout', status_code=status.HTTP_200_OK)
def logout(response: Response):
    response.set_cookie('logged_in', '', -1)

    return {'status': 'success'}


@router.post('/reset-password')
async def reset_password():
    return True


@router.post('/change-password')
async def change_password():
    return True


@router.post('/confirm-email')
async def confirm_email():
    return True


@router.get('/me', status_code=status.HTTP_200_OK,
            # response_model=CustomResponse[BaseUser], 
            response_model_exclude_none=True)
def get_current_user(user: BaseUser = Depends(AuthBackend)):
    return user


# TODO: 
# - Reset password /reset-password
# - Change password /change-password
# - Confirm email /confirm-email