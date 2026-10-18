"""Чтение и выполнение стартового скрипта."""

from pathlib import Path
from typing import Callable


class StartupError(Exception):
    """Ошибка чтения или выполнения стартового скрипта."""


def load_script(path: Path) -> list[str]:
    """Прочитать стартовый скрипт.

    Пустые строки и строки, начинающиеся с '#', игнорируются.

    Args:
        path: путь к файлу скрипта.

    Returns:
        Список строк-команд.

    Raises:
        StartupError: если файл не найден.
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
    """Выполнить команды скрипта как диалог.

    Показывает ввод и вывод, имитируя работу пользователя.
    Ошибочные строки пропускает.

    Args:
        commands: список команд.
        prompt: строка приглашения.
        handler: функция обработки одной строки. Ошибки не пробрасываются.
    """
    for command in commands:
        print(f"{prompt}{command}")
        try:
            handler(command)
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}")
