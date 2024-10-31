import logging
from .tools import Tool
from .tools.current_date_time import CurrentDateTime

__all__ = ["Registry"]

Log = logging.getLogger("Registry")


class Registry:

    def __init__(self):
        self.registered_tools: dict[str, Tool] = {}
        self.tools: dict[str, Tool] = {"get_current_date_time": CurrentDateTime()}

    @property
    def available_tools(self) -> list[str]:
        return list(self.tools.keys())

    def register_tool(self, name: str):
        if not self.tools.get(name):
            raise Exception(f"Tool with name {name} not found.")

        self.registered_tools[name] = self.tools[name]
        Log.info(f"Registered tool {name}")

    def deregister_tool(self, name: str):
        del self.registered_tools[name]
        Log.info(f"Deregistered tool {name}")

    @property
    def agent_tools(self) -> list[dict]:
        return [
            {"type": "function", "function": tool.obj}
            for tool in self.registered_tools.values()
        ]
