"""Ida's urlrequest main functionality."""
import json as _json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.response import addinfourl

from ida_py.urlrequest.errors import RequestError
from ida_py.urlrequest.models import Response


def get(url: str, headers: dict[str, str] = None, timeout: int = 10) -> Response:
    """Perform a GET request."""
    return _request("GET", url, headers=headers, timeout=timeout)


def post(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: int = 10,
    form: dict = None,
    json: dict = None,
) -> Response:
    """Perform a POST request.

    `form` and `json` can both be None.
    `form` and `json` cannot both have a truthy value.
    """
    assert not (form and json), "Either pass form or json, not both."
    headers = headers or {}
    data = _get_data(headers, form, json)
    response = _request("POST", url, headers, data=data, timeout=timeout)
    return response


def _request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    timeout: int = 10,
) -> Response:
    """Perform an HTTP request.

    Returns
    -------
    Response
        The response received from the server.

    Raises
    ------
    RequestError
        When the request could not reach the server.

    Notes
    -----
    The timeout does not seem to be taken into account. The socket timeout seems to take precedence.
    """
    parsed_url = urlparse(url)
    assert parsed_url.scheme == "https", f"Missing or unsupported scheme: {parsed_url.scheme}"
    request = Request(url, headers=headers or {}, data=data, method=method)
    try:
        return _perform_request(request, timeout=timeout)
    except HTTPError as exc:
        return _handle_http_error(exc)
    except URLError as exc:
        raise RequestError(exc.reason)


def _handle_http_error(exc: HTTPError) -> Response:
    return Response(
        exc.reason.encode(),
        status_code=exc.status or 500,
        content_type=exc.headers.get_content_type(),
        headers=dict(exc.headers),
    )


def _perform_request(request: Request, timeout: int = 10) -> Response:
    """Perform the request by calling urlopen.

    Notes
    -----
    B310:
        urlopen allows unsafe redirects and supports other schemes than https (e.g.: ftp).
        This opens up a vulnerability when the user can manipulate the opened url. They could for
        example open a website that returns a 302 and redirect to a ftp or other unsupported scheme.
        Therefore this module should only be used to make requests to pre-defined URLs and not
        accept user-input to define the URL. Note that this is not enforced (yet).
    no-redef:
        Allow redefining `response` to add typing. This is for convenience because the IDE will then
        correctly auto-complete for the current use-case. Since our tests always mock urlopen, the
        return of this method is never really tested, therefore it is important to statically ensure
        that accessed attributes exist.
    """
    with urlopen(request, timeout=timeout) as response:  # nosec B310
        response: addinfourl  # type: ignore[no-redef]
        print(response.status)
        return Response(
            response.read(),
            status_code=response.status,
            content_type=response.headers.get_content_type(),
            headers=response.headers,
        )


def _get_data(headers: dict[str, str], form: dict = None, json: dict = None) -> bytes | None:
    if json:
        headers["Content-Type"] = "application/json"
        data = _json.dumps(json).encode()
    elif form:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = urlencode(form).encode()
    else:
        data = None
    return data
