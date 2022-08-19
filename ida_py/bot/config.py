"""Ida's telegram bot configuration."""
import os
from dataclasses import dataclass

from ida_py import errors


@dataclass
class BotConfig:
    """Represent the configuration for the telegram bot."""

    chat_id: int
    domain_name: str
    endpoint: str
    bot_route: str
    webhook_token: str


def bot_config() -> BotConfig:
    """Attempt to get the config's fields from the environment."""
    try:
        chat_id = int(os.environ["CHAT_ID"])
        domain_name = os.environ["DOMAIN_NAME"]
        endpoint = os.environ["ENDPOINT"]
        bot_route = os.environ["BOT_ROUTE"]
        webhook_token = os.environ["WEBHOOK_TOKEN"]
    except KeyError as exc:
        raise errors.ConfigurationError(f"Please export {exc} as an environment variable.")
    except (TypeError, ValueError):
        received_value = os.environ["CHAT_ID"]
        raise errors.ConfigurationError(f"Could not cast CHAT_ID ({received_value}) to an int.")

    return BotConfig(
        chat_id=chat_id,
        domain_name=domain_name,
        endpoint=endpoint,
        bot_route=bot_route,
        webhook_token=webhook_token,
    )
