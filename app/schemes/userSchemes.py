from pydantic import BaseModel, EmailStr, field_validator

from app.core.exceptions import PasswordValidationException, EmailValidationException
from app.core.validators import PasswordValidator, EmailValidator


class SUser(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class SCreateUser(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def check_password(cls, value):
        if error := PasswordValidator.validate(value):
            raise PasswordValidationException(error)
        return value

    @field_validator("email")
    def validate_email(cls, value):
        if error := EmailValidator.validate(value):
            raise EmailValidationException(error)
        return value

    class Config:
        from_attributes = True

class SLoginUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True