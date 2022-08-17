"""Ida's telegram bot main functionality."""
from pathlib import Path
from typing import Any

import requests

from ida_py.bot.config import bot_config
from ida_py.bot.errors import ExecutionError
from ida_py.bot.models import Command, TelegramUpdate

LAST_MESSAGE_ID = Path(__file__).parent / "last_message_id"
BOT_CONFIG = bot_config()


def run(update: TelegramUpdate, token: str) -> None:
    """Validate the update and token, then register the command.

    Parameters
    ----------
    update : TelegramUpdate
        An update from Telegram.
    token : str
        The secret token, used to verify the origin of the update.

    Raises
    ------
    ExecutionError
        Whenever the update or token could not be validated.
    """
    if token != BOT_CONFIG.webhook_token:
        raise ExecutionError("Invalid token.")

    message = update.message
    if message is None:
        raise ExecutionError("Invalid update, no message found.")

    message_from_invalid = message.from_ is None or message.from_.id != BOT_CONFIG.chat_id
    if message.chat.id != BOT_CONFIG.chat_id or message_from_invalid:
        raise ExecutionError("Invalid chat id.")

    text = message.text or ""
    command = Command.new(text)
    if command is None:
        raise ExecutionError("Invalid command.")

    is_response_to_last_message = _read_last_message_id() + 1 == message.message_id
    if not is_response_to_last_message:
        raise ExecutionError("Invalid message_id.")

    _register(command)


def send_message(text: str) -> dict[str, Any]:
    """Use this method to send text messages. The message_id is returned.

    Parameters
    ----------
    text : str
        Text of the message to be sent.

    References
    ----------
    https://core.telegram.org/bots/api#sendmessage
    """
    text_work = {"text": Command.WORK.value}
    text_holiday = {"text": Command.HOLIDAY.value}
    text_sick = {"text": Command.SICK.value}
    buttons_row_1 = [text_work, text_holiday, text_sick]
    reply_markup = {
        "keyboard": [buttons_row_1],
        "resize_keyboard": False,
        "one_time_keyboard": True,
    }
    args = {"chat_id": BOT_CONFIG.chat_id, "text": text, "reply_markup": reply_markup}
    endpoint = BOT_CONFIG.endpoint + "sendMessage"
    response = requests.post(endpoint, json=args)
    print("Sent message", text)
    response_json = response.json()
    message_id = response_json["result"]["message_id"]
    _write_last_message_id(message_id)
    return response_json


def set_webhook():
    """Set a webhook.

    Notes
    -----
    Once a webhook is set, getUpdates no longer works.

    References
    ----------
    https://core.telegram.org/bots/api#setwebhook
    """
    endpoint = BOT_CONFIG.endpoint + "setWebhook"
    url = f"https://{BOT_CONFIG.domain_name}/{BOT_CONFIG.route_path_name}"
    args = {"url": url, "secret_token": BOT_CONFIG.webhook_token}
    response = requests.post(endpoint, json=args)
    response_json = response.json()
    if response_json["ok"] is False:
        print(f"Something went wrong while setting the webhook. {response_json}")
        exit(1)
    return response_json


def _write_last_message_id(message_id: int) -> None:
    LAST_MESSAGE_ID.write_text(str(message_id))


def _read_last_message_id() -> int:
    return int(LAST_MESSAGE_ID.read_text())


def _register(command: Command):
    if command is Command.WORK:
        print("Registering work")
    elif command is Command.HOLIDAY:
        print("Registering holiday")
    elif command is Command.SICK:
        print("Registering sick")
    else:
        print("Unknown action", command)


# def start():
#     args = sys.argv
#     if len(args) != 2:
#         print(f"This application requires precisely one extra argument. Received {args}")
#         exit(1)
#     command = args[1]
#     if command == "send":
#         send_message("What did you do today?")
#     elif command == "remind":
#         now = datetime.now(tz=timezone.utc)
#         if _get_timesheet_item(now.day - 1):
#             print("Timesheet item already found, nothing to do")
#             exit(0)
#         send_message("What did you do yesterday?")


if __name__ == "__main__":
    send_message("What did you do today?")
    # start()
    # r = set_webhook()
    # print(r)
