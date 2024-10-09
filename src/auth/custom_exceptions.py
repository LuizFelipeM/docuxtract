from fastapi import HTTPException


class BadCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Bad credentials")


class PermissionDeniedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Permission denied")


class RequiresAuthenticationException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Requires authentication")


class UnableCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500,
            detail="Unable to verify credentials",
        )
