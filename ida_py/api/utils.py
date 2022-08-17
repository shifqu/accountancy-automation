"""Ida's HTTP API utils."""
import json
from typing import Any

from ida_py import server


def convert_to_json_dict(body: Any) -> dict:
    """Convert the body to a json loaded dictionary.

    Parameters
    ----------
    body : Any
        The body to be json loaded and converted.

    Returns
    -------
    dict
        The json loaded body.

    Raises
    ------
    ApiException
        Whenever the body is invalid or unsupported JSON.
    """
    try:
        update_json = json.loads(body)
    except json.JSONDecodeError:
        raise server.ApiException({"ok": False, "error": "Invalid JSON."}, status_code=400)

    if not isinstance(update_json, dict):
        raise server.ApiException({"ok": False, "error": "Unsupported JSON."}, status_code=400)
    return update_json


def assert_post(method: str) -> None:
    """Assert that the method is of type "POST" or raise an ApiException.

    Parameters
    ----------
    method : str
        The method to be checked.

    Raises
    ------
    ApiException
        Whenever the method is not POST.
    """
    if method != "POST":
        error = f"{method} not supported."
        headers = {"Allow": "POST"}
        raise server.ApiException({"ok": False, "error": error}, status_code=405, headers=headers)
