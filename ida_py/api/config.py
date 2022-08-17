"""Ida's HTTP API configuration."""
import os
from dataclasses import dataclass

from ida_py import errors


@dataclass
class APIConfig:
    """Represent the configuration for Ida's HTTP API."""

    host: str
    port: int
    bot_route: str


def api_config() -> APIConfig:
    """Attempt to get the config's fields from the environment."""
    try:
        host = os.environ["HOST"]
        port = int(os.environ["PORT"])
        bot_route = os.environ["BOT_ROUTE"]
    except KeyError as exc:
        raise errors.ConfigurationError(f"Please export {exc} as an environment variable.")
    except (TypeError, ValueError):
        received_value = os.environ["PORT"]
        raise errors.ConfigurationError(f"Could not cast PORT ({received_value}) to an int.")

    return APIConfig(host, port, bot_route)
