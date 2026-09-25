import re

REGISTERED_EMAILS = {"existing@example.com"}

def validate_email_format(email: str) -> bool:
    if not isinstance(email, str) or "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Invalid email format")
    return True

def validate_password_complexity(password: str) -> bool:
    if (not isinstance(password, str) or 
        len(password) < 8 or 
        not any(c.isupper() for c in password) or 
        not any(c.isdigit() for c in password)):
        raise ValueError("Weak password")
    return True

def check_email_uniqueness(email: str) -> bool:
    if email in REGISTERED_EMAILS:
        raise ValueError("Email already exists or is a duplicate")
    return True

def register_user(email: str, password: str) -> dict:
    validate_email_format(email)
    check_email_uniqueness(email)
    validate_password_complexity(password)
    REGISTERED_EMAILS.add(email)
    return {"status": "success"}