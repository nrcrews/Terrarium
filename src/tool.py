__all__ = ["Tool"]


class Tool:

    def __init__(self):
        pass

    @classmethod
    def name(self) -> str:
        return self._name

    @property
    def obj(self) -> dict:
        return self._obj

    def call(self, args: dict) -> str:
        pass
