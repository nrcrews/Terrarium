import json, weakref, logging
from typing import override
from openai import OpenAI
from .registry import Registry
from .agent import Agent, AgentEventHandler, AgentToolCall, AgentToolCallOutput
from .agent.config import AgentConfiguration, RunConfiguration

Log = logging.getLogger("Conductor")

__all__ = ["Conductor", "StreamHandler"]


class StreamHandler:
    
    def on_text_started(self):
        pass

    def on_text_changed(self, delta: str):
        pass
    
    def on_text_done(self, text: str):
        pass


class Conductor:

    def __init__(
        self, client: OpenAI, config: AgentConfiguration, stream_handler: StreamHandler
    ):
        self.client = client
        self.agent = Agent(client=client, config=config)
        self.registry = Registry()
        self.stream_handler = stream_handler

    def add_message(self, text: str = None, image_file: str = None):
        content = []
        if text:
            content.append({"type": "text", "text": text})
        if image_file:
            upl_file = self.client.files.create(
                file=open(image_file, "rb"), purpose="assistants"
            )
            content.append(
                {"type": "image_file", "image_file": {"file_id": upl_file.id}}
            )
        self.agent.add_message(content=content)

    def run(
        self,
        config: RunConfiguration = RunConfiguration(
            instructions=None, parallel_tool_calls=True
        ),
    ):
        event_handler = AgentHandler(
            agent=self.agent, registry=self.registry, stream_handler=self.stream_handler
        )

        try:
            self.agent.run(
                config=config,
                tools=self.registry.agent_tools,
                event_handler=weakref.proxy(event_handler),
            )
        except Exception as e:
            Log.exception(e)


class AgentHandler(AgentEventHandler):

    def __init__(self, agent: Agent, registry: Registry, stream_handler: StreamHandler):
        self.agent = agent
        self.registry = registry
        self.stream_handler = stream_handler

    @override
    def on_tool_calls(self, tool_calls: list[AgentToolCall]):
        outputs = []
        for tool_call in tool_calls:
            tool = self.registry.registered_tools.get(tool_call.name)
            args = json.loads(tool_call.arguments)
            output = tool.call(args)

            outputs.append(
                AgentToolCallOutput(tool_call_id=tool_call.id, output=output)
            )

        self.agent.subbmit_tool_call_outputs(
            run_id=self.run_id,
            tool_call_outputs=outputs,
            event_handler=weakref.proxy(self),
        )
        return super().on_tool_calls(tool_calls)

    @override
    def on_run_done(self):
        return super().on_run_done()

    @override
    def on_error(self, error: Exception):
        return super().on_error(error)

    @override
    def on_text_started(self):
        self.stream_handler.on_text_started()
        return super().on_text_started()

    @override
    def on_text_changed(self, delta: str):
        self.stream_handler.on_text_changed(delta)
        return super().on_text_changed(delta)

    @override
    def on_text_done(self, text: str):
        self.stream_handler.on_text_done(text)
        return super().on_text_done(text)