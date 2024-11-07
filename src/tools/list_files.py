import os
from typing import override
from ..tool import Tool


__all__ = ["ListFiles"]


class ListFiles(Tool):

    @override
    @classmethod
    def name(self) -> str:
        return "list_files"

    @override
    @property
    def obj(self) -> dict:
        return {
            "name": ListFiles.name(),
            "description": "Lists the files amd directories in a directory.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the directory.",
                    },
                },
                "additionalProperties": False,
                "required": ["path"],
            },
        }

    @override
    def call(self, args: dict) -> str:
        path = args["path"]

        return str(os.listdir(path))
