"""Ida's telegram bot tests."""
import json
import os
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from ida_py import bot, transformer
from ida_py.bot.config import bot_config
from ida_py.bot.main import BOT_CONFIG, _register, send_message, set_webhook
from ida_py.bot.models import Command
from ida_py.errors import ConfigurationError
from tests.utils import template_data

ROOT_DIR = Path(__file__).parent / "data" / "bot"


def test_misconfiguration(mocker: MockerFixture):
    """Test that the correct error is thrown when something is wrong with the configuration."""
    mocker.patch.dict(os.environ, {"CHAT_ID": "abc"})  # TypeError or ValueError
    with pytest.raises(ConfigurationError):
        bot_config()

    mocker.patch.dict(os.environ, {"DUMMY": ""}, clear=True)  # KeyError
    with pytest.raises(ConfigurationError):
        bot_config()


@pytest.mark.parametrize(
    "dirname",
    [
        "invalid_chat_id",
        "invalid_command",
        "invalid_message_id",
        "invalid_token",
        "invalid_update_no_message",
    ],
)
def test_execution_error(dirname: str, mocker: MockerFixture):
    """Test that the bot raises an ExecutionError."""
    last_message_id = ROOT_DIR / dirname / "last_message_id"
    if last_message_id.exists():
        mocker.patch("ida_py.bot.main.LAST_MESSAGE_ID", last_message_id)

    token_path = ROOT_DIR / dirname / "token"
    if token_path.exists():
        token = token_path.read_text()
    else:
        token = BOT_CONFIG.webhook_token

    filepath = ROOT_DIR / dirname / "update.txt"
    data = filepath.read_text()

    dot_template = ROOT_DIR / dirname / ".template"
    if dot_template.exists():
        data = template_data(data)

    update_values = json.loads(data)
    update = transformer.from_dict(bot.TelegramUpdate, update_values)

    error_path = ROOT_DIR / dirname / "error.txt"
    error = error_path.read_text()

    with pytest.raises(bot.ExecutionError, match=error):
        bot.run(update, token)


def test_register():
    """Test the private method _register by directly calling it."""
    _register(Command.WORK)
    _register(Command.HOLIDAY)
    _register(Command.SICK)
    _register("UNKNOWN")


def test_set_webhook(mocker: MockerFixture):
    """Test the method `set_webhook` whilst mocking `requests.post`."""
    post_patched = mocker.patch("ida_py.bot.main.requests.post")

    json_return_value = {"ok": True}
    post_patched.return_value.json.return_value = json_return_value
    result = set_webhook()
    assert result == json_return_value

    json_return_value = {"ok": False}
    post_patched.return_value.json.return_value = json_return_value
    with pytest.raises(SystemExit):
        result = set_webhook()


def test_send_message(mocker: MockerFixture):
    post_patched = mocker.patch("ida_py.bot.main.requests.post")
    mocker.patch("ida_py.bot.main.Path.write_text")
    json_return_value = {"ok": True, "result": {"message_id": 100}}
    post_patched.return_value.json.return_value = json_return_value
    result = send_message("dummy")
    assert result == json_return_value
