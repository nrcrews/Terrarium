from typing import override
from datetime import datetime
from .tool import Tool


__all__ = ["CurrentDateTime"]


class CurrentDateTime(Tool):

    @override
    @classmethod
    def name(self) -> str:
        return "get_current_date_time"

    @override
    @property
    def obj(self) -> dict:
        return {
            "name": CurrentDateTime.name(),
            "description": "Get the current date and time.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
                "required": [],
            },
        }

    @override
    def call(self, args: dict) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
