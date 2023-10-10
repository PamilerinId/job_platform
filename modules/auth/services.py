from datetime import timedelta
from typing import Annotated
from modules.jobs.models import Job
from pydantic import TypeAdapter
from fastapi import Request
from fastapi import Depends, HTTPException, status, APIRouter, Response, Path
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from authlib.integrations.starlette_client import OAuthError
from modules.files.models import File, FileType
from sqlalchemy.orm import Session, joinedload

from google.oauth2 import id_token 
from google.auth.transport import requests 

from core.dependencies.sessions import get_db
from core.dependencies.auth import TokenHelper, get_current_user, custom_oauth
from core.helpers import password
from core.helpers.schemas import CustomResponse, CandidateWelcomeEmail, ClientWelcomeEmail, PasswordResetEmail
from core.env import config
from core.exceptions import *
from core.helpers.mail_utils import *

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
    
    #Send welcome email
    email_payload = CandidateWelcomeEmail(first_name = payload.first_name)
    mail_notify(payload.email, CANDIDATE_WELCOME_MAIL, email_payload)
    
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
    
    #Send welcome email
    email_payload = ClientWelcomeEmail(first_name = payload.first_name)
    mail_notify(payload.email, CLIENT_WELCOME_MAIL, email_payload)
    
    
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


@router.post("/login/google", response_model=CustomResponse[AuthUser], 
             status_code=status.HTTP_200_OK)
async def login_via_google(request: Request,token:str,
                           db: Session = Depends(get_db)):
    # verify token google
    # fetch user profile from google
    try: 
        # Specify the CLIENT_ID of the app that accesses the backend: 
        user = id_token.verify_oauth2_token(token, requests.Request(), config.GOOGLE_CLIENT_ID) 

        request.session['user'] = dict({ 
            "email" : user['email'] 
        })

        # Check if the user exist
        user_object = db.query(User).filter(
            User.email == user['email'].lower()).first()

        if not user_object:
            # register user
            new_user = User(first_name=user['given_name'],
                            last_name=user['family_name'],
                            email=user['email'], 
                            photo=user['picture'], 
                            password='p@ss!234_')
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
        else:
            data =  { **jsonable_encoder(BaseUser.from_orm(user_object)), 
                    "token":TokenHelper.encode(jsonable_encoder(BaseUser.from_orm(user_object)))}

        
        return {"message":"User logged in successfully","data": data} 
  
    except ValueError: 
        raise UserNotFoundException
    
@router.post("/login/admin/google", response_model=CustomResponse[AuthUser], 
             status_code=status.HTTP_200_OK)
async def admin_login_via_google(request: Request,token:str,
                           db: Session = Depends(get_db)):
    # verify token google
    # fetch user profile from google
    try: 
        # Specify the CLIENT_ID of the app that accesses the backend: 
        user = id_token.verify_oauth2_token(token, requests.Request(), config.GOOGLE_CLIENT_ID) 
        print(user, flush=True)
        request.session['user'] = dict({ 
            "email" : user['email'] 
        })

        # check if user is distinct email
        if user['email'].split('@')[1] != 'distinct.ai': #config.domain_name
            raise UnauthorisedUserException('You are not authorised to access the page')

        # Check if the user exist
        user_object = db.query(User).filter(
            User.email == user['email'].lower()).first()

        if not user_object:
            # register user
            new_user = User(first_name=user['given_name'],
                            last_name=user['family_name'],
                            email=user['email'], 
                            photo=user['picture'], 
                            password='p@ss!234_')
            new_user.role = UserType.ADMIN
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            # TODO: Generate confirm email OTP and Send Welcome email
            data =  { **jsonable_encoder(BaseUser.from_orm(new_user)), 
                    "token":TokenHelper.encode(jsonable_encoder(BaseUser.from_orm(new_user)))}
        else:
            data =  { **jsonable_encoder(BaseUser.from_orm(user_object)), 
                    "token":TokenHelper.encode(jsonable_encoder(BaseUser.from_orm(user_object)))}

        
        return {"message":"User logged in successfully","data": data} 
  
    except ValueError: 
        raise UnauthorisedUserException


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
    
    #Send mail
    email_payload = PasswordResetEmail(first_name = user.first_name)
    mail_notify(payload.email, PASSWORD_RESET_MAIL, email_payload)
    
    data =  {"token":TokenHelper.encode({"id": str(user.id), "email": user.email}, 900)}
    
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
    # user = db.query(User).filter(User.email == current_user.email)
    # new_user = user.first()

    # if user is None:
    #     raise UserNotFoundException
    
    # check db values and update
    # email verification
    onboarding_status = Onboarding(verify_email=True if current_user.email else False) #bull
    onboarding_status.photo_uploaded = True if current_user.photo != None else False
    if current_user.first_name and current_user.last_name and current_user.photo:
        onboarding_status.profile_complete = True

    if current_user.role == UserType.CANDIDATE and current_user.candidate_profile.cv:
        onboarding_status.cv_uploaded = True

    if current_user.role == UserType.CLIENT and current_user.client_profile:
        if current_user.client_profile.company:
            onboarding_status.company_profile_complete = True
            jobs = db.query(Job).options(
                        joinedload(Job.company)
                        .joinedload(Company.profile)).filter(
                        Job.company_id == current_user.client_profile.company.id).limit(1).offset(0).all()
            
            if len(jobs) > 1: 
                onboarding_status.post_first_job = True
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