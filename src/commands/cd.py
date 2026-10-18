"""Команда cd — заглушка (этап 1)."""

from .base import Command


class CdCommand(Command):
    """Команда cd. Пока ничего не делает с VFS."""

    name = "cd"

    def execute(self, args: list[str]) -> str:
        """Вернуть строку с именем команды и аргументами.

        Args:
            args: аргументы, переданные пользователем.

        Returns:
            Строка вида "cd: ['/home']".
        """
        return f"cd: {args}"
