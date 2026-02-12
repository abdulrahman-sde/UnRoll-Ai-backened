from typing import Dict, Optional
from fastapi import status


class AppException(Exception):
    def __init__(self, message: str, status_code: int, errors: dict | None):
        self.message = message
        self.status_code = status_code
        self.errors = errors


class ValidationException(AppException):
    def __init__(self, message: str = "Validation Error", errors: dict | None = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, errors)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict Error", errors: dict | None = None):
        super().__init__(message, status.HTTP_409_CONFLICT, errors)


class NotFoundException(AppException):
    def __init__(self, message: str, errors: Dict | None = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, errors)


class UnauthorizedException(AppException):
    def __init__(self, message: str, errors: Dict | None = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, errors)
