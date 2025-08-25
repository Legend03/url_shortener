from fastapi import APIRouter, HTTPException, Response, Form, Request
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr, ValidationError as PydanticValidationError
from starlette.templating import _TemplateResponse

from app.core.exceptions import PasswordValidationException, EmailValidationException
from app.core.validators import PasswordValidator, EmailValidator
from app.repositories.userRepository import UserRepository
from app.schemes.userSchemes import SCreateUser, SLoginUser

router = APIRouter(prefix='/users', tags=["Work with user"])
templates = Jinja2Templates(directory="app/templates")

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
async def register_user(request: Request,
                        response: Response,
                        email: str = Form(...),
                        password: str = Form(...),
                        password_confirm: str = Form(...)
                        ) -> _TemplateResponse:
    errors = []

    if password != password_confirm:
        errors.append("Passwords don't match")

    if password_errors := PasswordValidator.validate(password):
        for error in password_errors:
            errors.append(error)

    if email_error := EmailValidator.validate(email):
        errors.append(email_error)

    if errors:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": errors,
            "email": email,
        })

    try:
        userData = SCreateUser(email=email, password=password)
        encodeJWT = await UserRepository.register_user(userData)
        set_cookie(response, encodeJWT)
        return templates.TemplateResponse('index.html', {
            'request': request,
            'message': 'User registered successfully!'
        })
    except (PasswordValidationException, EmailValidationException, ValueError) as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": [str(e)],
            "email": email
        })

@router.post('/login', summary="Login user")
async def login_user(request: Request,
                     response: Response,
                     email: str = Form(...),
                     password: str = Form(...),
                    ) -> _TemplateResponse:
    try:
        userData = SLoginUser(email=email, password=password)
        encode_jwt = await UserRepository.login_user(userData)
        set_cookie(response, encode_jwt)
        return templates.TemplateResponse('index.html', {
            'request': request,
            'message': 'User logged successfully!'
        })
    except PydanticValidationError as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": str(e),
            "email": email
        })

@router.post('/logout', summary="Logout user")
async def logout_user(response: Response) -> dict:
    response.delete_cookie('access_token')
    return { 'message': 'User logout successfully!' }