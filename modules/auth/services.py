from datetime import timedelta
from typing import Annotated
from pydantic import TypeAdapter

from fastapi import Request
from fastapi import Depends, HTTPException, status, APIRouter, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from modules.files.models import File, FileType
from sqlalchemy.orm import Session, joinedload

from core.dependencies.sessions import get_db
from core.dependencies.auth import TokenHelper, get_current_user
from core.helpers import password
from core.helpers.schemas import CustomResponse
from core.env import config
from core.exceptions import *

from modules.auth.schemas import LoginUserSchema, PasswordChangeSchema, PasswordResetRequestSchema, RegisterUserSchema
from modules.users.models import CandidateProfile, ClientProfile, Company, User
from modules.users.schemas import *

from modules.files.schemas import File as FileSchema

router = APIRouter(
    prefix="/auth", tags=["Auth"]
)



################### Functions ########################



################### ROUTES ###########################

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username.lower()).first()
    if not user:
        raise UserNotFoundException

    # Check if user verified his email
    # if not user.email_verified:
    #     raise UnauthorisedUserException

    # Check if the password is valid
    if not password.verify_password(form_data.password, user.password):
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
async def create_candidate(payload: RegisterUserSchema, db: Session = Depends(get_db)):
    # Check if user already exist
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user:
        raise DuplicateEmailException
    #  Hash the password
    payload.password = password.hash_password(payload.password)
    new_user = User(**payload.dict())
    new_user.role = UserType.CANDIDATE
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # update related models
    new_candidate_profile = CandidateProfile(user_id=new_user.id)
    new_candidate_profile.updated_at = datetime.now()
    db.add(new_candidate_profile)
    db.commit()
    # TODO: Generate confirm email OTP and Send Welcome email
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
async def create_client(payload: RegisterUserSchema, db: Session = Depends(get_db)):
    # Check if user already exist
    user = db.query(User).filter(
        User.email == payload.email.lower()).first()
    if user:
        raise DuplicateEmailException
    #  Hash the password
    payload.password = password.hash_password(payload.password)
    payload.email = payload.email.lower()
    new_user = User(**payload.dict())
    new_user.role = UserType.CLIENT
    # TODO: Refactor to repository
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # update related models
    new_client_profile = ClientProfile(user_id=new_user.id)
    new_client_profile.updated_at = datetime.now()
    db.add(new_client_profile)
    db.commit()
    #TODO: Generate confirm email OTP and Send Welcome email
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
def login(payload: LoginUserSchema, db: Session = Depends(get_db)):
    # Check if the user exist
    user = db.query(User).filter(
        User.email == payload.email.lower()).first()
    if not user:
        raise UserNotFoundException

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
    # TODO: blacklist in redis cache
    return {'status': 'success'}

@router.post('/reset-password',
             response_model=CustomResponse, 
             response_model_exclude_none=True)
async def password_reset_request(payload: PasswordResetRequestSchema, 
                                 db: Session = Depends(get_db)):
    # Check if the user exist
    user = db.query(User).filter(
        User.email == payload.email.lower()).first()
    if not user:
        raise UserNotFoundException
    
    # Generate token and TODO: send mail
    data =  {"token":TokenHelper.encode({"id": user.id, "email": user.email}, 900)}
    
    return  {"message": "Password reset requested successfully", "data":data}


@router.post('/change-password',
             response_model=CustomResponse[BaseUser], 
             response_model_exclude_none=True)
async def change_password(payload: PasswordChangeSchema, 
                          current_user: Annotated[BaseUser, Depends(get_current_user)],
                          db: Session = Depends(get_db)):
    
    payload.password = password.hash_password(payload.password)
    # TODO: Refactor to repository
    # new_user.modified = datetime.utcnow()
    user = db.query(User).filter(User.email == current_user.email)
    new_user = user.first()
    if user is None:
        raise UserNotFoundException
    user.update(payload.dict())
    db.commit()
    db.refresh(new_user)
    # TODO: Trigger email confirmation
    return  {"message": "Password update successful", "data": BaseUser.from_orm(user.first())}


@router.post('/confirm-email')
async def confirm_email():
    # Get token as header and update confirm email field
    return True


def onboarding_checker(current_user: BaseUser, db):
    # get full user profile
    user = db.query(User).filter(User.email == current_user.email)
    new_user = user.first()

    if user is None:
        raise UserNotFoundException
    
    # check db values and update
    # email verification
    onboarding_status = Onboarding(verify_email=new_user.email_verified)
    # client profile checks
    # candidate profile checks

    return onboarding_status


@router.get('/me', status_code=status.HTTP_200_OK,
            
            response_model=CustomResponse[BaseUser]
            )
def get_current_user(current_user: Annotated[BaseUser, Depends(get_current_user)], db: Session = Depends(get_db)):
    if(current_user.role == UserType.CANDIDATE):
        cv_files = db.query(File).filter(
            File.owner_id == current_user.id, File.type == FileType.RESUME)\
            .order_by(File.created_at.desc()).limit(3).all()
        if current_user.candidate_profile:
            current_user.candidate_profile.cv = TypeAdapter(List[FileSchema]).validate_python(cv_files)
    else:
        company = db.query(Company).options(
                joinedload(Company.profile)).filter(Company.owner_id == str(current_user.id)).first()
        if company:
            current_user.client_profile.company = company

    current_user.onboarding_steps = onboarding_checker(current_user, db)
    return  {"message": "User profile successfully retrieved", "data": current_user}

#  TODO: 
# - Confirm email /confirm-email