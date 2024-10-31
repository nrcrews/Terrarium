from typing import override
from InquirerPy import prompt
from .tool import Tool


__all__ = ["PromptUserInput"]


class PromptUserInput(Tool):

    @override
    @property
    def name(self) -> str:
        return "prompt_user_input"

    @override
    @property
    def obj(self) -> dict:
        return {
            "name": "prompt_user_input",
            "description": "Prompt the user for input.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt message to display to the user.",
                    }
                },
                "additionalProperties": False,
                "required": ["prompt"],
            },
        }

    @override
    def call(self, args: dict) -> str:
        prompt = args.get("prompt")

        if not prompt:
            raise Exception("Prompt message is required.")

        user_input = prompt(
            {
                "type": "input",
                "name": "user_input",
                "message": prompt,
            }
        ).get("user_input")
        
        return user_input
