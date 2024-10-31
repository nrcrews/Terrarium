import os

__all__ = ["is_debug"]

is_debug = os.getenv("ENV") != "production"