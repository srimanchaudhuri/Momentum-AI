"""Application-level domain exceptions.

These are HTTP-agnostic but carry enough context for the global
exception handlers to build a proper response.
"""


class AppException(Exception):
    """Base exception for all domain errors."""

    def __init__(self, detail: str = "An unexpected error occurred.", status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource", identifier: str = ""):
        detail = f"{resource} not found." if not identifier else f"{resource} '{identifier}' not found."
        super().__init__(detail=detail, status_code=404)


class DuplicateError(AppException):
    """Raised when a unique constraint would be violated."""

    def __init__(self, detail: str = "Resource already exists."):
        super().__init__(detail=detail, status_code=409)


class InvalidIdError(AppException):
    """Raised when a provided ID is not a valid ObjectId."""

    def __init__(self, value: str = ""):
        detail = f"Invalid ID format: '{value}'." if value else "Invalid ID format."
        super().__init__(detail=detail, status_code=400)


class AuthenticationError(AppException):
    """Raised when credentials are invalid or a token is expired/malformed."""

    def __init__(self, detail: str = "Invalid credentials."):
        super().__init__(detail=detail, status_code=401)


class AuthorizationError(AppException):
    """Raised when a user tries to access a resource they don't own."""

    def __init__(self, detail: str = "You do not have permission to access this resource."):
        super().__init__(detail=detail, status_code=403)
