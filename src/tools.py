__all__ = ["Tools"]


class Tools:

    def __init__(self, tools: dict):
        self.tools = tools
        self.list = [{"type": "function", "function": tool} for tool in tools]
