"""Реестр всех команд эмулятора."""

from collections.abc import Callable

from ..vfs import VFS
from .base import Command
from .cd import CdCommand
from .exit import ExitCommand
from .ls import LsCommand


# Фабрика: принимает VFS, возвращает готовую команду.
CommandFactory = Callable[[VFS], Command]

_COMMAND_FACTORIES: dict[str, CommandFactory] = {
    "ls": lambda vfs: LsCommand(vfs),
    "cd": lambda vfs: CdCommand(vfs),
    "exit": lambda vfs: ExitCommand(),
}


def get_command(name: str, vfs: VFS) -> Command | None:
    """Получить команду по имени.

    Args:
        name: имя команды.
        vfs: виртуальная файловая система.

    Returns:
        Экземпляр команды или None, если не найдена.
    """
    factory = _COMMAND_FACTORIES.get(name)
    if factory is None:
        return None
    return factory(vfs)
