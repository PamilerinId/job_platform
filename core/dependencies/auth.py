import os
import base64
from datetime import datetime, timedelta
from typing import Annotated

import jwt
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload

from modules.users.schemas import BaseCandidate, BaseClient, BaseUser
from modules.auth.schemas import RefreshTokenSchema
from modules.users.models import ClientProfile, User, UserType, Company

from core.env import config
from core.dependencies.sessions import get_db
from core.exceptions.base import UnauthorizedException
from core.exceptions.auth import DecodeTokenException, ExpiredTokenException, UserNotFoundException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# Set up oauth
config_data = {'GOOGLE_CLIENT_ID': config.GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': config.GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
custom_oauth = OAuth(starlette_config)

# google reg
custom_oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
# linkedin reg
# custom_oauth.register(name="linkedin",)



class TokenHelper:
    @staticmethod
    def encode(data: dict, expire_period: int = 3600) -> str:
        token = jwt.encode(
            payload = {
                **data,
                "exp": datetime.utcnow() + timedelta(seconds=expire_period),
            },
            key=config.JWT_SECRET_KEY
        )
        return token

    @staticmethod
    def decode(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                config.JWT_SECRET_KEY,
            )
        except jwt.exceptions.DecodeError:
            raise DecodeTokenException("Something went wrong decoding your access token")
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredTokenException(message="Your token has expired")

    @staticmethod
    def decode_expired_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                config.JWT_ALGORITHM,
                options={"verify_exp": False},
            )
        except jwt.exceptions.DecodeError:
            raise DecodeTokenException("Token has expired")
        
    async def create_refresh_token(
        self,
        token: str,
        refresh_token: str,
    ) -> RefreshTokenSchema:
        token = TokenHelper.decode(token=token)
        refresh_token = TokenHelper.decode(token=refresh_token)
        if refresh_token.get("sub") != "refresh":
            raise DecodeTokenException("Token has expired")

        return RefreshTokenSchema(
            token=TokenHelper.encode(payload={"user_id": token.get("user_id")}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )


async def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_scheme)], 
                           db: Session = Depends(get_db)) -> BaseUser:
    user_decoded_string : str
    # TODO: Refactor token capture, decode and validation into middleware [using oauth bearer doesnt work in middleware]
    # Get decoded token from auth middleware
    try:
        if request.user:
            user_decoded_string = request.user  
        else: # Get token from headers
            user_decoded_string = TokenHelper.decode(token)
    except:
        raise DecodeTokenException("Something went wrong decoding your access token")
    

    user_email: str = user_decoded_string.get("email")
    role: str = user_decoded_string.get("role")

    if user_email is None:
        raise UnauthorizedException(message="Could not validate credentials")
    
    if (role == UserType.CLIENT):
        user = db.query(User).options(
                joinedload(User.client_profile)
                .joinedload(ClientProfile.company)).filter(User.email == user_email).first()
    elif (role == UserType.CANDIDATE):
        user = db.query(User).options(
                joinedload(User.candidate_profile)).filter(User.email == user_email).first()
    else:
        user = db.query(User).filter(User.email == user_email).first()

    return BaseUser.from_orm(user)


async def get_current_user_object(request: Request, token: Annotated[str, Depends(oauth2_scheme)], 
                           db: Session = Depends(get_db)) -> User:
    user_decoded_string : str
    # TODO: Refactor token capture, decode and validation into middleware [using oauth bearer doesnt work in middleware]
    # Get decoded token from auth middleware
    try:
        if request.user:
            user_decoded_string = request.user  
        else: # Get token from headers
            user_decoded_string = TokenHelper.decode(token)
    except:
        raise UnauthorizedException(message="Could not validate credentials")
    user_email: str = user_decoded_string.get("email")
    if user_email is None:
        raise UnauthorizedException(message="Could not validate credentials")
    
    role: str = user_decoded_string.get("role")
    if (role == UserType.CLIENT):
        user = db.query(User).options(
                joinedload(User.client_profile)).filter(User.email == user_email).first()
    elif (role == UserType.CANDIDATE):
        user = db.query(User).options(
                joinedload(User.candidate_profile)).filter(User.email == user_email).first()
    else:
        user = db.query(User).filter(User.email == user_email).first()

    if user is None:
        raise UserNotFoundException
    return user

