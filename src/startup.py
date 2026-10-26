"""Чтение и выполнение стартового скрипта."""

from pathlib import Path
from typing import Callable


class StartupError(Exception):
    """Ошибка чтения или выполнения стартового скрипта."""


def load_script(path: Path) -> list[str]:
    """Прочитать стартовый скрипт.

    Пустые строки и строки с '#' игнорируются.
    """
    if not path.exists():
        raise StartupError(f"startup script not found: {path}")
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def run_script(
    commands: list[str],
    prompt: str,
    handler: Callable[[str], None],
) -> None:
    """Выполнить команды скрипта как диалог."""
    for command in commands:
        print(f"{prompt}{command}")
        try:
            handler(command)
        except Exception as exc:
            print(f"Error: {exc}")
