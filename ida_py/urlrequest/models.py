"""Ida's urlrequest models."""
import json
from dataclasses import dataclass, field


@dataclass
class Response:
    """Represent a Response."""

    body: bytes
    status_code: int = 200
    content_type: str = "text/html"
    headers: dict[str, str] = field(default_factory=dict)

    def json(self):
        """Convert the body to a dictionary using the json module."""
        return json.loads(self.body)
