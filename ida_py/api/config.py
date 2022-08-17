"""Ida's HTTP API configuration."""
import os
from dataclasses import dataclass

from ida_py import errors


@dataclass
class APIConfig:
    """Represent the configuration for Ida's HTTP API."""

    host: str
    port: int
    route_path_name: str


def api_config() -> APIConfig:
    """Attempt to get the config's fields from the environment."""
    try:
        host = os.environ["HOST"]
        port = int(os.environ["PORT"])
        route_path_name = os.environ["ROUTE_PATH_NAME"]
    except KeyError as exc:
        raise errors.ConfigurationError(f"Please export {exc} as an environment variable.")
    except (TypeError, ValueError):
        received_value = os.environ["PORT"]
        raise errors.ConfigurationError(f"Could not cast PORT ({received_value}) to an int.")

    return APIConfig(host, port, route_path_name)
