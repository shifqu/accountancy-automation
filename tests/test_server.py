"""Ida's HTTP server tests."""
import os

import pytest
from pytest_mock import MockerFixture

from ida_py.errors import ConfigurationError
from ida_py.server.config import ServerConfig, server_config
from ida_py.server.main import Application, TCPHandler
from ida_py.server.models import Response
from ida_py.server.utils import _build_body_str


def test_write_to_file(mocker: MockerFixture):
    """Test that we can write to a file from the TCPHandler."""
    mocker.patch("ida_py.server.main.SERVER_CONFIG", ServerConfig(write_to_file=1))
    patched_write = mocker.patch("ida_py.server.main.Path.write_text")
    mocker.patch("ida_py.server.main.Path.mkdir")
    TCPHandler._write_to_file("foo", "test.txt")
    assert patched_write.call_args[0][0] == "foo"


def test_misconfiguration(mocker: MockerFixture):
    """Test that the correct error is thrown when something is wrong with the configuration."""
    mocker.patch.dict(os.environ, {"WRITE_TO_FILE": "YESSIR"})  # ValueError
    with pytest.raises(ConfigurationError):
        server_config()

    mocker.patch.dict(os.environ, {"DUMMY": ""}, clear=True)  # KeyError
    cfg = server_config()
    assert cfg.write_to_file == ServerConfig.__dataclass_fields__["write_to_file"].default


def test_shutdown():
    """Test that the shutdown method raises the expected exception."""
    with pytest.raises(KeyboardInterrupt):
        Application.shutdown()


def test_build_body_str():
    """Ensure that the response.body is returned if it's a string."""
    dummy = "dummy"
    response = Response(dummy)
    assert _build_body_str(response) == dummy
