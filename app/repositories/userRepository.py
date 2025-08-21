from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, Depends, Request
from sqlalchemy import select
from passlib.context import CryptContext
from starlette import status

from app.core.config import get_auth_data
from app.core.database import async_session_maker
from app.models.user import User
from app.schemes.userSchemes import SCreateUser, SLoginUser, SUser

pwd_context =  CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserRepository:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    async def user_exists(cls, user_data: SCreateUser | SLoginUser) -> User | None:
        async with async_session_maker() as session:
            query = select(User).where(User.email == user_data.email)
            result = await session.execute(query)

            return result.scalar_one_or_none()

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=30)
        to_encode.update({'exp': expire})

        auth_data = get_auth_data()
        encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])

        return encode_jwt

    @staticmethod
    def decode_access_token(token: str) -> dict:
        auth_data = get_auth_data()
        try:
            payload = jwt.decode(
                token,
                auth_data['secret_key'],
                algorithms=[auth_data['algorithm']]
            )
            return payload
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )

    @staticmethod
    def get_access_token_from_cookie(request: Request) -> str:
        token = request.cookies.get('access_token')
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
        return token

    @classmethod
    async def get_current_user(cls, token: str = Depends(get_access_token_from_cookie)) -> SUser:
        payload = cls.decode_access_token(token)

        expire = payload['exp']
        expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
        if not expire or expire_time < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')

        user_id = payload['sub']
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')

        user = SUser.model_validate({
            'id': int(payload['sub']),
            'email': payload['email'],
        })
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

        return user

    @classmethod
    async def login_user(cls, user_data: SLoginUser) -> str:
        existing_user = await cls.user_exists(user_data)
        if not existing_user:
            raise ValueError('Invalid email')

        if not cls.verify_password(user_data.password, existing_user.password_hash):
            raise ValueError('Invalid password')

        token_data = {
            'sub': str(existing_user.id),
            'email': existing_user.email,
        }
        access_token = cls.create_access_token(token_data)

        return access_token

    @classmethod
    async def register_user(cls, user_data: SCreateUser) -> str:
        async with async_session_maker() as session:
            if await cls.user_exists(user_data):
                raise ValueError('User already exists')

            new_user = User(
                email=user_data.email,
                password_hash = cls.get_password_hash(user_data.password)
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            token_data = {
                'sub': str(new_user.id),
                'email': user_data.email,
            }
            access_token = cls.create_access_token(token_data)

            return access_token