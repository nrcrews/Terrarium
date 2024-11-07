from typing import override
from ..tool import Tool


__all__ = ["WriteFile"]


class WriteFile(Tool):

    @override
    @classmethod
    def name(self) -> str:
        return "write_file"

    @override
    @property
    def obj(self) -> dict:
        return {
            "name": WriteFile.name(),
            "description": "Writes a file.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the file.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content of the file.",
                    },
                },
                "additionalProperties": False,
                "required": ["path", "content"],
            },
        }

    @override
    def call(self, args: dict) -> str:
        path = args["path"]
        content = args["content"]

        with open(path, "w") as f:
            f.write(content)

        return f"File created at {path}"
