"""Базовый класс для всех команд эмулятора."""

from abc import ABC, abstractmethod


class Command(ABC):
    """Абстрактная команда эмулятора."""

    name: str = ""

    @abstractmethod
    def execute(self, args: list[str]) -> str:
        """Выполнить команду и вернуть строку для вывода."""
