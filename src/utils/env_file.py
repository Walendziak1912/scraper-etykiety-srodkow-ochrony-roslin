import os
import re
from pathlib import Path

from src.core.settings import get_settings

_ENV_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def update_env_variable(
    key: str,
    value: str,
    env_path: Path | str = ".env",
) -> None:
    path = Path(env_path)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    updated = False
    new_lines: list[str] = []

    for line in lines:
        match = _ENV_LINE.match(line.strip())
        if match and match.group(1) == key:
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{key}={value}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.environ[key] = value
    get_settings.cache_clear()
