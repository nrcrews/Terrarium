import os
from typing import override
from .tool import Tool


__all__ = ["MoveFile"]


class MoveFile(Tool):

    @override
    @classmethod
    def name(self) -> str:
        return "move_file"

    @override
    @property
    def obj(self) -> dict:
        return {
            "name": MoveFile.name(),
            "description": "Moves a file.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "from_path": {
                        "type": "string",
                        "description": "The path of the file to move.",
                    },
                    "to_path": {
                        "type": "string",
                        "description": "The path to move the file to.",
                    },
                },
                "additionalProperties": False,
                "required": ["from_path", "to_path"],
            },
        }

    @override
    def call(self, args: dict) -> str:
        from_path = args["from_path"]
        to_path = args["to_path"]

        os.rename(from_path, to_path)

        return f"File moved from {from_path} to {to_path}"
