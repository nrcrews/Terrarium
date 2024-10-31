import os, json
from openai import OpenAI
from .utils import announce, prompt_list, prompt_confirm, prompt_string
from src.agent.config import AgentConfiguration, RunConfiguration
from src.conductor import Conductor

__all__ = ["main"]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def main():
    announce("Welcome to Terrarium!", prefix="🌱 ")

    custom_agent_config = prompt_confirm(
        "Would you like to use a custom agent configuration?", default=False
    )

    if custom_agent_config:
        agent_config = AgentConfiguration(
            assistant_id=prompt_string("Assistant ID: "),
            instructions=prompt_string("Agent instructions: "),
            model=prompt_list("Select a model:", ["gpt-4o", "gpt-4o-mini"]),
            temperature=float(prompt_string("Temperature: ")),
        )
    else:
        config_file = "./resources/agent_config.json"
        agent_config = AgentConfiguration(**json.load(open(config_file)))

    conductor = Conductor(client=client, config=agent_config)

    custom_run_config = prompt_confirm(
        "Would you like to use a custom run configuration?", default=False
    )

    if custom_run_config:
        run_config = RunConfiguration(
            instructions=prompt_string("Run instructions: "),
            parallel_tool_calls=prompt_confirm("Parallelize tool calls?", default=True),
        )
    else:
        run_config = RunConfiguration(instructions=None, parallel_tool_calls=True)

    while True:
        action = prompt_list(
            "What would you like to do?",
            [
                "New message",
                "Run agent",
                "Register Tool",
                "Remove Tool",
                "Update run configuration",
                "Exit",
            ],
        )

        if action == "New message":
            text = prompt_string("Text:")
            image_file = prompt_string("Image file (optional):")
            conductor.add_message(text=text, image_file=image_file)
        elif action == "Run agent":
            conductor.run(config=run_config)

        elif action == "Register Tool":
            selected_tool = prompt_list(
                "Select a tool:", conductor.registry.available_tools
            )

            if selected_tool:
                conductor.registry.register_tool(name=selected_tool)

        elif action == "Remove Tool":
            selected_tool = prompt_list(
                "Select a tool:", conductor.registry.registered_tools.keys()
            )

            if selected_tool:
                conductor.registry.deregister_tool(name=selected_tool)

        elif action == "Update run configuration":
            run_config = RunConfiguration(
                instructions=prompt_string("Run instructions: "),
                parallel_tool_calls=prompt_confirm(
                    "Parallelize tool calls?", default=True
                ),
            )
        elif action == "Exit":
            break
