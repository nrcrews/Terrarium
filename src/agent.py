from pydantic import BaseModel
from openai import OpenAI
from .config import AgentConfiguration, RunConfiguration
from .utils import log

class AgentToolCall(BaseModel):

    id: str
    name: str
    arguments: str


class AgentToolCallOutput(BaseModel):

    tool_call_id: str
    output: str


class AgentEventHandler:

    def __init__(self, thread_id: str = None):
        self.thread_id = thread_id
        self.run_id = None

    def on_run_done(self):
        pass

    def on_error(self, error: Exception):
        pass

    def on_text_changed(self, delta: str):
        pass

    def on_text_done(self, text: str):
        pass

    def on_tool_calls(self, tool_calls: list[AgentToolCall]):
        pass

    def on_tool_call_outputs(self, tool_call_output: list[AgentToolCallOutput]):
        pass


class Agent:

    def __init__(
        self,
        client: OpenAI,
        config: AgentConfiguration,
        thread_id: str = None,
    ):
        self.client = client
        self.agent_config = config
        if not thread_id:
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
        else:
            self.thread_id = thread_id

    def add_message(self, content: dict):
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=content
        )

    def run(self, config: RunConfiguration, event_handler: AgentEventHandler):
        event_handler.thread_id = self.thread_id
        pass

    def subbmit_tool_call_outputs(
        self,
        run_id: str,
        tool_call_outputs: list[AgentToolCallOutput],
        event_handler: AgentEventHandler,
    ):
        pass

    @classmethod
    def cancel_run(cls, client: OpenAI, thread_id: str, run_id: str):
        client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
