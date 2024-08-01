"""Exceptions for auth model."""

from starlette import status

from app.pkg.models.base import BaseAPIException

__all__ = [
    "PasswordHashingError",
    "IncorrectUsernameOrPassword",
    "InvalidPasswordHashValue",
    "IncorrectOTPCode",
    "PermissionDeniedForOperation",
]


class PasswordHashingError(BaseAPIException):
    message = (
        "Error occurred while processing user password. "
        "Please try again with different password."
    )
    status_code = status.HTTP_409_CONFLICT


class IncorrectUsernameOrPassword(BaseAPIException):
    message = "Incorrect username or password."
    status_code = status.HTTP_403_FORBIDDEN


class InvalidPasswordHashValue(BaseAPIException):
    message = "Internal error occurred while validating password."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class IncorrectOTPCode(BaseAPIException):
    message = "Incorrect user password."
    status_code = status.HTTP_403_FORBIDDEN


class PermissionDeniedForOperation(BaseAPIException):
    message = "Not enough permissions for this operation."
    status_code = status.HTTP_403_FORBIDDEN


__constrains__ = {
    "auth_password_hashing_error": PasswordHashingError,
    "auth_incorrect_username_or_password": IncorrectUsernameOrPassword,
    "auth_invalid_password_hash_value": InvalidPasswordHashValue,
    "auth_incorrect_otp_code": IncorrectOTPCode,
    "auth_permission_denied_for_operation": PermissionDeniedForOperation,
}
