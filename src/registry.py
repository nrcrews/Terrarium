import logging
from .tools import Tool

__all__ = ["Registry"]

Log = logging.getLogger("Registry")


class Registry:

    def __init__(self):
        self.registered_tools: dict[str, Tool] = {}
        self.tools: dict[str, Tool] = local_tools()

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


from .tools.current_date_time import CurrentDateTime
from .tools.read_file import ReadFile
from .tools.delete_file import DeleteFile
from .tools.write_file import WriteFile
from .tools.move_file import MoveFile
from .tools.list_files import ListFiles


def local_tools() -> dict[str, Tool]:
    return {
        CurrentDateTime.name(): CurrentDateTime(),
        ReadFile.name(): ReadFile(),
        DeleteFile.name(): DeleteFile(),
        WriteFile.name(): WriteFile(),
        MoveFile.name(): MoveFile(),
        ListFiles.name(): ListFiles(),
    }
