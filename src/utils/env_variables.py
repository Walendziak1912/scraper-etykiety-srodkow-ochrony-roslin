import os
from pathlib import Path

def get_env_variable_value(name: str) -> Path:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return Path(value)