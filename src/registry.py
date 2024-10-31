from .tools import Tool
from .tools.prompt_user import PromptUserInput

__all__ = ["Registry"]


class Registry:

    def __init__(self):
        self.tools: dict[str, Tool] = {"prompt_user_input": PromptUserInput()}
        self.registered_tools: dict[str, Tool] = {}

    def available_tools(self) -> list[str]:
        return list(self.tools.keys())

    def register_tool(self, name: str):
        if not self.tools.get(name):
            raise Exception(f"Tool with name {name} not found.")

        self.registered_tools[name] = self.tools[name]

    def deregister_tool(self, tool: Tool):
        del self.registered_tools[tool.name]

    def agent_tools(self) -> list[dict]:
        return [
            {"type": "function", "function": tool.obj}
            for tool in self.registered_tools.values()
        ]
