from pydantic import BaseModel, EmailStr, field_validator

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
        value = str(value)
        if len(value) < 8:
            raise ValueError("Password must have at least 8 characters")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must have at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("Password must have at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must have at least one digit")
        return value

    @field_validator("email")
    def validate_email(cls, v):
        if "@example.com" in v:
            raise ValueError("Invalid email domain")
        return v

    class Config:
        from_attributes = True

class SLoginUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True