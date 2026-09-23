"""Пользовательские исключения эмулятора."""


class ShellError(Exception):
    """Базовое исключение эмулятора."""


class UnknownCommandError(ShellError):
    """Команда не найдена."""

    def __init__(self, name: str) -> None:
        super().__init__(f"unknown command: '{name}'")
        self.name = name


class InvalidArgumentsError(ShellError):
    """Неверные аргументы команды."""

    def __init__(self, command: str, reason: str) -> None:
        super().__init__(f"{command}: {reason}")
        self.command = command
        self.reason = reason
