"""Команда uptime — время работы эмулятора."""

from datetime import datetime

from ..vfs import VFS
from .base import Command


class UptimeCommand(Command):
    """Команда uptime. Показывает время работы эмулятора."""

    name = "uptime"

    def __init__(self, started_at: datetime) -> None:
        """Создать команду с временем старта.

        Args:
            started_at: момент запуска эмулятора.
        """
        self.started_at = started_at

    def execute(self, args: list[str]) -> str:
        """Вычислить время работы.

        Args:
            args: аргументы (игнорируются).

        Returns:
            Строка вида "Up 5 minutes, 23 seconds".
        """
        delta = datetime.now() - self.started_at
        total_seconds = int(delta.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        parts: list[str] = []
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

        return "Up " + ", ".join(parts)
