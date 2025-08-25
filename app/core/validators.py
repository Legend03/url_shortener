class PasswordValidator:
    @staticmethod
    def validate(password: str):
        errors = []

        if len(password) < 8:
            errors.append("Password must have at least 8 characters")
        if not any(c.isupper() for c in password):
            errors.append("Password must have at least one uppercase letter")
        if not any(c.islower() for c in password):
            errors.append("Password must have at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            errors.append("Password must have at least one digit")

        return errors if errors else None

class EmailValidator:
    @staticmethod
    def validate(email: str):
        if "@example.com" in email:
            return "Invalid email domain"
        return None