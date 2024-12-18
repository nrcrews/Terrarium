import logging
from pydantic import BaseModel
from openai import OpenAI
from openai import OpenAI
from openai.types.beta.threads import Message, Text, TextDelta
from typing_extensions import override
from pydantic import BaseModel
from openai import AssistantEventHandler, OpenAI
from openai.types.beta.threads.runs import (
    RunStep,
    FunctionToolCall,
    CodeInterpreterToolCall,
    FileSearchToolCall,
)
from .config import AgentConfiguration, RunConfiguration

Log = logging.getLogger("Agent")


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

    def on_text_started(self):
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

    def add_message(self, content: list[dict]):
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=content
        )
        Log.info(f"Message added > {content}")

    def run(
        self,
        config: RunConfiguration,
        tools: list[dict],
        event_handler: AgentEventHandler,
    ):
        Log.info(f"Run started with instructions > {config.instructions}")

        event_handler.thread_id = self.thread_id
        assistant_handler = EventHandler(
            client=self.client, thread_id=self.thread_id, handler=event_handler
        )

        with self.client.beta.threads.runs.stream(
            assistant_id=self.agent_config.assistant_id,
            model=self.agent_config.model,
            instructions=self.agent_config.instructions,
            temperature=self.agent_config.temperature,
            additional_instructions=config.instructions,
            parallel_tool_calls=config.parallel_tool_calls,
            event_handler=assistant_handler,
            tools=tools,
            thread_id=self.thread_id,
        ) as stream:
            stream.until_done()

    def subbmit_tool_call_outputs(
        self,
        run_id: str,
        tool_call_outputs: list[AgentToolCallOutput],
        event_handler: AgentEventHandler,
    ):
        Log.info(f"Tool call outputs > {tool_call_outputs}")
        event_handler.thread_id = self.thread_id
        assistant_handler = EventHandler(
            client=self.client,
            thread_id=self.thread_id,
            handler=event_handler,
            run_id=run_id,
        )

        with self.client.beta.threads.runs.submit_tool_outputs_stream(
            run_id=run_id,
            thread_id=self.thread_id,
            tool_outputs=[tool_call.model_dump() for tool_call in tool_call_outputs],
            event_handler=assistant_handler,
        ) as stream:
            stream.until_done()

    @classmethod
    def cancel_run(cls, client: OpenAI, thread_id: str, run_id: str):
        client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
        Log.info(f"Run cancelled > {run_id}")


class EventHandler(AssistantEventHandler):

    def __init__(
        self,
        client: OpenAI,
        thread_id: str,
        handler: AgentEventHandler,
        run_id: str = None,
    ):
        super().__init__()
        self.client = client
        self.thread_id = thread_id
        self.handler = handler
        self.handler.thread_id = thread_id
        self.run_id = run_id
        self.run_step = None
        self.tool_calls = []

    @override
    def on_end(self):
        if (
            self.run_step
            and self.run_step.status == "in_progress"
            and len(self.tool_calls) > 0
        ):
            tcs = [
                AgentToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=tool_call.function.arguments,
                )
                for tool_call in self.tool_calls
            ]
            Log.info(f"Tool calls > {tcs}")
            self.handler.on_tool_calls(tcs)
            return super().on_end()

        run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id, run_id=self.run_id
        )

        if run.status == "completed":
            self.handler.on_run_done()

        Log.info(f"Run status > {run.status}")
        return super().on_end()

    @override
    def on_exception(self, exception: Exception) -> None:
        """Fired whenever an exception happens during streaming"""
        Log.exception(f"Exception > {exception}")
        self.handler.on_error(exception)
        return super().on_exception(exception)

    @override
    def on_run_step_created(self, run_step: RunStep) -> None:
        self.run_id = run_step.run_id
        self.run_step = run_step
        self.handler.run_id = run_step.run_id
        self.tool_calls: list[FunctionToolCall] = []
        Log.info(f"Run step created > {run_step.id}")
        return super().on_run_step_created(run_step)

    @override
    def on_run_step_done(self, run_step: RunStep) -> None:
        Log.info(f"Run step done > {run_step.id}")
        return super().on_run_step_done(run_step)

    # Mark - Tool events

    @override
    def on_tool_call_done(
        self, tool_call: CodeInterpreterToolCall | FileSearchToolCall | FunctionToolCall
    ) -> None:
        if isinstance(tool_call, CodeInterpreterToolCall):
            return super().on_tool_call_done(tool_call)
        elif isinstance(tool_call, FileSearchToolCall):
            return super().on_tool_call_done(tool_call)

        run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id, run_id=self.run_id
        )

        if run.status == "completed":
            return
        elif run.status == "in_progress":
            self.tool_calls.append(tool_call)
        elif run.status == "requires_action":
            self.tool_calls.append(tool_call)

        return super().on_tool_call_done(tool_call)

    # Mark: - Text Events

    @override
    def on_text_created(self, text: Text) -> None:
        self.handler.on_text_started()
        return super().on_text_created(text)

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        self.handler.on_text_changed(delta.value)
        return super().on_text_delta(delta, snapshot)

    @override
    def on_text_done(self, text: Text) -> None:
        self.handler.on_text_done(text.value)
        Log.info(f"Text: {text.value}")
        return super().on_text_done(text)
