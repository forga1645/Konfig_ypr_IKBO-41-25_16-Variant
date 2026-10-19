"""Реестр всех команд эмулятора."""

from collections.abc import Callable
from datetime import datetime

from ..vfs import VFS
from .base import Command
from .cd import CdCommand
from .cp import CpCommand
from .du import DuCommand
from .exit import ExitCommand
from .ls import LsCommand
from .touch import TouchCommand
from .uptime import UptimeCommand
from .vfs_load import VfsLoadCommand
from .wc import WcCommand


CommandFactory = Callable[[VFS, datetime], Command]


_COMMAND_FACTORIES: dict[str, CommandFactory] = {
    "ls": lambda vfs, started: LsCommand(vfs),
    "cd": lambda vfs, started: CdCommand(vfs),
    "exit": lambda vfs, started: ExitCommand(),
    "uptime": lambda vfs, started: UptimeCommand(started),
    "wc": lambda vfs, started: WcCommand(vfs),
    "du": lambda vfs, started: DuCommand(vfs),
    "cp": lambda vfs, started: CpCommand(vfs),
    "touch": lambda vfs, started: TouchCommand(vfs),
    "vfs-load": lambda vfs, started: VfsLoadCommand(vfs),
}


def get_command(
    name: str,
    vfs: VFS,
    started_at: datetime,
) -> Command | None:
    """Получить команду по имени.

    Args:
        name: имя команды.
        vfs: виртуальная файловая система.
        started_at: время старта эмулятора.

    Returns:
        Экземпляр команды или None, если не найдена.
    """
    factory = _COMMAND_FACTORIES.get(name)
    if factory is None:
        return None
    return factory(vfs, started_at)
