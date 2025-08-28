from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, Request
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
    async def get_current_user_by_token(cls, token: str) -> SUser:
        payload = cls.decode_access_token(token)

        expire = payload['exp']
        expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
        if not expire or expire_time < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')

        user_id = payload['sub']
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found')

        async with async_session_maker() as session:
            query = select(User).where(User.id == int(user_id))
            result = await session.execute(query)
            user_model = result.scalar_one_or_none()

            if not user_model:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

            return SUser.model_validate(user_model)

    @staticmethod
    async def get_current_user(request: Request) -> SUser | None:
        try:
            token = UserRepository.get_access_token_from_cookie(request)
            current_user = await UserRepository.get_current_user_by_token(token)
            if not current_user:
                return None
            return current_user
        except HTTPException:
            return None

    @staticmethod
    async def require_auth(request: Request) -> SUser:
        try:
            token = UserRepository.get_access_token_from_cookie(request)
            current_user = await UserRepository.get_current_user_by_token(token)
            if not current_user:
                raise HTTPException(status_code=302, detail="Not authenticated")
            return current_user
        except HTTPException:
            raise HTTPException(status_code=302, detail="Not authenticated")
        except Exception:
            raise HTTPException(status_code=302, detail="Not authenticated")

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