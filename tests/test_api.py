"""Ida's HTTP API tests."""
import os
import socket
from pathlib import Path
from threading import Thread

import pytest
from pytest_mock import MockerFixture

from ida_py.api import run
from ida_py.api.config import api_config
from ida_py.errors import ConfigurationError

ROOT_DIR = Path(__file__).parent / "data" / "api"

HOST, PORT = "localhost", 9999


@pytest.fixture(scope="session")
def _server(session_mocker: MockerFixture):
    """Serve the api in a separate thread.

    By running in a separate thread, we can use the HTTP protocol to send/recv data. This emulates
    a real world server and enables us to record some request/responses and replay them.
    """
    cfg = api_config()
    cfg.host = HOST
    cfg.port = PORT
    session_mocker.patch("ida_py.api.main.API_CONFIG", cfg)
    serve_thread = Thread(target=run, daemon=True)
    serve_thread.start()
    _connect_or_retry()


@pytest.mark.parametrize(
    "dirname",
    [
        "get_ping_200",
        "get_notfound_404",
        "get_bot_405",
        "post_bot_200",
        "post_bot_400_invalid_json",
        "post_bot_400_invalid_update",
        "post_bot_400_unsupported_json",
        "post_bot_400_bot_executionerror",
    ],
)
@pytest.mark.usefixtures("_server")
def test_request(dirname: str, mocker: MockerFixture):
    """Test a request.

    dirname MUST contain at least request.txt and response.txt
    dirname CAN contain a last_message_id, which will mock LAST_MESSAGE_ID in the bot.
    dirname CAN contain an empty .template file, which will cause the test to template the request
    file. A templated variable should be an existing environment variable enclosed in ${}.
    For example: the content ${DUMMY} in request.txt would be extrapolated to the value of
    os.environ["DUMMY"]. A KeyError is not caught.

    The `_server` fixture is used.

    Parameters
    ----------
    dirname : str
        The name of the directory containing the files for the test.
    mocker : MockerFixture
        Mocker fixture provided by pytest-mock.
    """
    last_message_id = ROOT_DIR / dirname / "last_message_id"
    if last_message_id.exists():
        mocker.patch("ida_py.bot.main.LAST_MESSAGE_ID", last_message_id)

    filepath = ROOT_DIR / dirname / "request.txt"
    data = filepath.read_text()

    dot_template = ROOT_DIR / dirname / ".template"
    if dot_template.exists():
        data = _template_data(data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        data_bytes = data.encode()
        sock.sendall(data_bytes)

        # Receive data from the server
        received = str(sock.recv(1024), "utf-8")

    filepath = ROOT_DIR / dirname / "response.txt"
    expected_response = filepath.read_text()
    assert received == expected_response


def test_misconfiguration(mocker: MockerFixture):
    """Test that the correct error is thrown when something is wrong with the configuration."""
    mocker.patch.dict(os.environ, {"PORT": "abc"})
    with pytest.raises(ConfigurationError):
        api_config()

    mocker.patch.dict(os.environ, {"DUMMY": ""}, clear=True)
    with pytest.raises(ConfigurationError):
        api_config()


def _connect_or_retry(max_retries=5, _n=0):
    """Try to connect or retry for the given max_retries.

    This method is used to avoid a cold start issue where the client is making requests while the
    server is still binding to the address.

    Parameters
    ----------
    max_retries : int, optional
        Maximum number of retries to perform, by default 5
    _n : int, optional
        Internal variable used to keep count of how many times the function ran, by default 0
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server
            sock.connect((HOST, PORT))
    except Exception:
        _n += 1
        if _n < max_retries:
            _connect_or_retry(max_retries, _n)


def _template_data(data: str):
    """Replace all ${} enclosed strings with their value in `os.environ`.

    Parameters
    ----------
    data : str
        The data to replace data in

    Returns
    -------
    data : str
        A copy of the data with all template variables replaced.
    """
    start = None
    while (template_start := data.find("${", start)) != -1:
        template_end = data.find("}", template_start)
        replace_str = data[template_start : template_end + 1]
        environ_str = data[template_start + 2 : template_end]
        new_str = os.environ[environ_str]
        start = template_end
        data = data.replace(replace_str, new_str)
    return data
