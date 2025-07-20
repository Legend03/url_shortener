from fastapi import APIRouter, HTTPException
from fastapi import Response
from fastapi.params import Depends


from app.repositories.userRepository import UserRepository
from app.schemes.userSchemes import SCreateUser, SLoginUser

router = APIRouter(prefix='/user', tags=["Work with user"])

def set_cookie(response: Response, to_encode_data: str):
    response.set_cookie(
        key='access_token',
        value=to_encode_data,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=30 * 24 * 60 * 60
    )

@router.post('/register', summary="Register new user")
async def register_user(response: Response, user_data: SCreateUser = Depends()) -> dict:
    try:
        encode_jwt = await UserRepository.register_user(user_data)
        set_cookie(response, encode_jwt)
        return { 'message': 'User registered successfully!' }
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post('/login', summary="Login user")
async def login_user(response: Response, user_data: SLoginUser = Depends()) -> dict:
    try:
        encode_jwt = await UserRepository.login_user(user_data)
        set_cookie(response, encode_jwt)
        return { 'message': 'User logged successfully!' }
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post('/logout', summary="Logout user")
async def logout_user(response: Response) -> dict:
    response.delete_cookie('access_token')
    return { 'message': 'User logout successfully!' }