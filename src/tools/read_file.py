from typing import override
from ..tool import Tool


__all__ = ["ReadFile"]


class ReadFile(Tool):

    @override
    @classmethod
    def name(self) -> str:
        return "read_file"

    @override
    @property
    def obj(self) -> dict:
        return {
            "name": ReadFile.name(),
            "description": "Reads a file.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the file.",
                    },
                },
                "additionalProperties": False,
                "required": ["path"],
            },
        }

    @override
    def call(self, args: dict) -> str:
        path = args["path"]

        with open(path, "r") as f:
            content = f.read()

        return content
