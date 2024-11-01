import os
from typing import override
from .tool import Tool


__all__ = ["DeleteFile"]


class DeleteFile(Tool):

    @override
    @classmethod
    def name(self) -> str:
        return "delete_file"

    @override
    @property
    def obj(self) -> dict:
        return {
            "name": DeleteFile.name(),
            "description": "Deletes a file.",
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

        os.remove(path)
        
        return f"File deleted at {path}"
