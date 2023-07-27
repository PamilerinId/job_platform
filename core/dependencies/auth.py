import base64
from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from services.users.schemas import BaseUser
from services.auth.schemas import RefreshTokenSchema
from services.users.models import User

from core.env import config
from core.dependencies.sessions import get_db
from core.exceptions.base import UnauthorizedException
from core.exceptions.auth import DecodeTokenException, ExpiredTokenException, UserNotFoundException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")



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
            raise DecodeTokenException
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredTokenException

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
            raise DecodeTokenException
        
    async def create_refresh_token(
        self,
        token: str,
        refresh_token: str,
    ) -> RefreshTokenSchema:
        token = TokenHelper.decode(token=token)
        refresh_token = TokenHelper.decode(token=refresh_token)
        if refresh_token.get("sub") != "refresh":
            raise DecodeTokenException

        return RefreshTokenSchema(
            token=TokenHelper.encode(payload={"user_id": token.get("user_id")}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )


async def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_scheme)], 
                           db: Session = Depends(get_db)) -> BaseUser:
    user_decoded_string : str
    # TODO: Refactor token capture, decode and validation into middleware [using oauth bearer doesnt work in middleware]
    # Get decoded token from auth middleware
    if request.user:
        user_decoded_string = request.user  
    else: # Get token from headers
        user_decoded_string = TokenHelper.decode(token)
    user_email: str = user_decoded_string.get("email")
    if user_email is None:
        raise UnauthorizedException(message="Could not validate credentials")
    user = db.query(User).filter(User.email == user_email).first()
    if user is None:
        raise UserNotFoundException
    return BaseUser.from_orm(user)