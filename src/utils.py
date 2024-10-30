import os

__all__ = ["is_debug", "log"]

is_debug = os.getenv("ENV") != "production"


# Only executes the message closure if it's debug mode
def log(message_callable: callable):
    if is_debug:
        print(message_callable(), flush=True)