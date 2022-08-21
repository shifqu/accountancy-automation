"""Ida's request tests."""
import json
from http.client import HTTPMessage
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

import pytest
from pytest_mock import MockerFixture

from ida_py import urlrequest


def test_post_json(mocker: MockerFixture):
    """Test a POST request whilst providing the `json` argument."""
    urlopen_patch = mocker.patch("ida_py.urlrequest.main.urlopen")
    data = {"hello": "world"}
    url = "https://httpbin.org/post"
    urlrequest.post(url, json=data)
    urlopen_request: Request = urlopen_patch.call_args[0][0]
    assert urlopen_request.method == "POST"
    assert urlopen_request.full_url == url
    assert urlopen_request.headers["Content-type"] == "application/json"
    assert urlopen_request.data == json.dumps(data).encode()


def test_post_form(mocker: MockerFixture):
    """Test a POST request whilst providing the `form` argument."""
    urlopen_patch = mocker.patch("ida_py.urlrequest.main.urlopen")
    data = {"hello": "world"}
    url = "https://httpbin.org/post"
    urlrequest.post(url, form=data)
    urlopen_request: Request = urlopen_patch.call_args[0][0]
    assert urlopen_request.method == "POST"
    assert urlopen_request.full_url == url
    assert urlopen_request.headers["Content-type"] == "application/x-www-form-urlencoded"
    assert urlopen_request.data == urlencode(data).encode()


def test_post_no_data(mocker: MockerFixture):
    """Test a POST request whilst providing the `form` argument."""
    urlopen_patch = mocker.patch("ida_py.urlrequest.main.urlopen")
    url = "https://httpbin.org/post"
    urlrequest.post(url)
    urlopen_request: Request = urlopen_patch.call_args[0][0]
    assert urlopen_request.method == "POST"
    assert urlopen_request.full_url == url
    assert urlopen_request.data is None


def test_get(mocker: MockerFixture):
    """Test a GET request."""
    urlopen_patch = mocker.patch("ida_py.urlrequest.main.urlopen")
    url = "https://httpbin.org/get"
    urlrequest.get(url)
    urlopen_request: Request = urlopen_patch.call_args[0][0]
    assert urlopen_request.method == "GET"
    assert urlopen_request.full_url == url


def test_response_json():
    """Test that the `json` method on a response parses to json or raises a JSONDecodeError."""
    body = b'{"hello": "world"}'
    assert urlrequest.Response(body=body).json() == {"hello": "world"}

    body = b'garble":'
    with pytest.raises(json.JSONDecodeError):
        urlrequest.Response(body=body).json()


def test_failing_request_urlerror(mocker: MockerFixture):
    """Test that an URLError is converted to a RequestError."""
    urlopen_patch = mocker.patch("ida_py.urlrequest.main.urlopen")
    urlopen_patch.side_effect = URLError("Dummy Reason")
    with pytest.raises(urlrequest.RequestError, match="Dummy Reason"):
        urlrequest.get("https://garble")


def test_failing_request_httperror(mocker: MockerFixture):
    """Test that an HTTPError is returned as a Response with the respective reason and status."""
    urlopen_patch = mocker.patch("ida_py.urlrequest.main.urlopen")
    urlopen_patch.side_effect = HTTPError("https://dummy.url", 500, "DUMMY", HTTPMessage(), None)
    response = urlrequest.get("https://dummy.url")
    assert response.body == b"DUMMY"
    assert response.status_code == 500
