__all__ = ["Tools"]


class Tools:

    def __init__(self, tools: dict):
        self.tools = [{"type": "function", "function": tool} for tool in tools]

    def __call__(self):
        return self.tools
