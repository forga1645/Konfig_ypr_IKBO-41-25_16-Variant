"""Реестр всех команд эмулятора."""

from .base import Command
from .cd import CdCommand
from .exit import ExitCommand
from .ls import LsCommand

COMMANDS: dict[str, Command] = {
    "ls": LsCommand(),
    "cd": CdCommand(),
    "exit": ExitCommand(),
}


def get_command(name: str) -> Command | None:
    """Получить команду по имени.

    Args:
        name: имя команды.

    Returns:
        Экземпляр команды или None, если не найдена.
    """
    return COMMANDS.get(name)
