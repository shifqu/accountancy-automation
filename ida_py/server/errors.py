"""Ida's HTTP server errors."""
from ida_py.server.models import JSONResponse


class ApiException(JSONResponse, BaseException):
    """Raised whenever an exception occurred during request/response handling."""
