"""Команда cd — заглушка (этап 1)."""

from .base import Command


class CdCommand(Command):
    """Команда cd."""

    name = "cd"

    def execute(self, args: list[str]) -> str:
        """Вернуть строку с именем команды и аргументами."""
        return f"cd: {args}"
