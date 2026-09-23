"""Команда ls — заглушка (этап 1)."""

from .base import Command


class LsCommand(Command):
    """Команда ls. Пока ничего не делает с VFS."""

    name = "ls"

    def execute(self, args: list[str]) -> str:
        """Вернуть строку с именем команды и аргументами."""
        return f"ls: {args}"
