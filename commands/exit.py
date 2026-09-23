"""Команда exit — завершение работы эмулятора."""

from .base import Command


class ExitRequested(Exception):
    """Сигнал REPL-циклу о завершении работы."""


class ExitCommand(Command):
    """Команда exit. Завершает работу эмулятора."""

    name = "exit"

    def execute(self, args: list[str]) -> str:
        """Сигнализировать о завершении работы."""
        raise ExitRequested()
