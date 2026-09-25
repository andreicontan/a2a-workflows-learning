import re

_users = {"existing@example.com"}


def validate_email_format(email: str) -> bool:
    if not isinstance(email, str) or "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Invalid email format")
    return True


def validate_password_strength(password: str) -> bool:
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    return True


def validate_password_complexity(password: str) -> bool:
    if not isinstance(password, str):
        raise ValueError("Invalid password")
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_upper and has_digit):
        raise ValueError("Password must contain an uppercase letter and a digit")
    return True


def check_email_uniqueness(email: str) -> bool:
    if email in _users:
        raise ValueError("Email already exists")
    return True


def register_user(email: str, password: str) -> bool:
    validate_email_format(email)
    check_email_uniqueness(email)
    validate_password_strength(password)
    validate_password_complexity(password)
    _users.add(email)
    return True