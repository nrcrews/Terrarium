from pydantic import BaseModel
from enum import Enum
from .tools import Tools

__all__ = ["AIModel", "AgentConfiguration", "RunConfiguration"]


# eum of models
class AIModel(str, Enum):
    """
    Enum of models.
    """

    gpt4o = "gpt-4o"
    gpt4oMini = "gpt-4o-mini"


class AgentConfiguration(BaseModel):
    """
    Configuration for the agent.
    """

    assistant_id: str
    """
    The assistant ID.
    """

    instructions: str
    """
    The instructions to follow.
    """

    model: AIModel
    """
    The model to use.
    """

    temperature: float
    """
    The temperature.
    """
    tools: Tools


class RunConfiguration(BaseModel):
    """
    Configuration for the run.
    """

    instructions: str
    """
    The agent configuration.
    """

    parallel_tool_calls: bool
    """
    Whether to parallelize tool calls.
    """
