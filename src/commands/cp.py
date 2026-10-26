"""Команда cp — копирование файлов и папок."""

from ..vfs import VFS
from .base import Command

CP_REQUIRED_ARGS = 2


class CpCommand(Command):
    """Команда cp. Копирует файлы и папки внутри VFS."""

    name = "cp"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS."""
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить cp."""
        if len(args) < CP_REQUIRED_ARGS:
            raise VFSError("cp: missing operand")
        self.vfs.cp(args[0], args[1])
        return ""
