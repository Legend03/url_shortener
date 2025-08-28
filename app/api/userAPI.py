from fastapi import APIRouter, Response, Form, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from app.core.exceptions import PasswordValidationException, EmailValidationException
from app.core.validators import PasswordValidator, EmailValidator
from app.repositories.userRepository import UserRepository
from app.schemes.userSchemes import SCreateUser, SLoginUser, SUser

router = APIRouter(prefix='/users', tags=["Work with user"])
templates = Jinja2Templates(directory="app/templates")

def set_cookie(response: Response, to_encode_data: str):
    response.set_cookie(
        key='access_token',
        value=to_encode_data,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=30 * 24 * 60 * 60,
        path='/'
    )

@router.post('/register', summary="Register new user", response_model=None)
async def register_user(request: Request,
                        response: Response,
                        email: str = Form(...),
                        password: str = Form(...),
                        password_confirm: str = Form(...)
                        ) -> _TemplateResponse | RedirectResponse:
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

        redirect_response = RedirectResponse(url="/dashboard", status_code=303)
        set_cookie(redirect_response, encodeJWT)
        return redirect_response
    except (PasswordValidationException, EmailValidationException, ValueError) as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": [str(e)],
            "email": email
        })

@router.post('/login', summary="Login user", response_model=None)
async def login_user(request: Request,
                     response: Response,
                     email: str = Form(...),
                     password: str = Form(...),
                    ) -> _TemplateResponse | RedirectResponse:
    try:
        userData = SLoginUser(email=email, password=password)
        encodeJWT = await UserRepository.login_user(userData)

        redirect_response = RedirectResponse(url="/dashboard", status_code=303)
        set_cookie(redirect_response, encodeJWT)
        return redirect_response
    except (PasswordValidationException, EmailValidationException, ValueError) as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": str(e),
            "email": email
        })

@router.get('/logout', summary="Logout user")
async def logout_user(response: Response) -> RedirectResponse:
    redirect_response = RedirectResponse(url='/')
    redirect_response.delete_cookie('access_token')
    return redirect_response