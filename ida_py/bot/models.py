"""Ida's telegram bot models."""
from __future__ import annotations  # Required to support `Command.new()` return-type

from dataclasses import dataclass, field
from enum import Enum


class Command(Enum):
    """Represent possible commands to be handled by the bot."""

    WORK = "work"
    HOLIDAY = "holiday"
    SICK = "sick"
    CUSTOM = "custom"

    @classmethod
    def new(cls, value: str) -> Command | None:
        """Safely create an instance of Command by returning None in case of an error."""
        try:
            return cls(value)
        except ValueError:
            return None


@dataclass
class Chat:
    """Represent a Chat from telegram.

    References
    ----------
    https://core.telegram.org/bots/api#chat
    """

    id: int
    type: str
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


@dataclass
class User:
    """Represent a User from telegram.

    References
    ----------
    https://core.telegram.org/bots/api#user
    """

    id: int
    is_bot: bool
    first_name: str
    language_code: str | None = None


@dataclass
class Message:
    """Represent a Message from telegram.

    References
    ----------
    https://core.telegram.org/bots/api#message
    """

    date: int
    chat: Chat
    message_id: int
    from_: User | None = field(default=None, metadata={"alias": "from"})
    text: str | None = None


@dataclass
class TelegramUpdate:
    """Represent an incoming update from telegram.

    References
    ----------
    https://core.telegram.org/bots/api#update
    """

    update_id: int
    message: Message | None = None
