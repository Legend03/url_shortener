from fastapi import HTTPException

class ValidationException(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code, detail)

class PasswordValidationException(ValidationException):
    def __init__(self, message: str):
        super().__init__(message)

class EmailValidationException(ValidationException):
    def __init__(self, message: str):
        super().__init__(message)