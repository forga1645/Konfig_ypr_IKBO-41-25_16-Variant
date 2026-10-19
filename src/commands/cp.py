"""Команда cp — копирование файлов и папок."""

from ..vfs import VFS
from .base import Command


class CpCommand(Command):
    """Команда cp. Копирует файлы и папки внутри VFS."""

    name = "cp"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS.

        Args:
            vfs: виртуальная файловая система.
        """
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить cp.

        Args:
            args: два аргумента — источник и назначение.

        Returns:
            Пустая строка (cp ничего не печатает).

        Raises:
            VFSError: если аргументов не два.
        """
        if len(args) < 2:
            raise VFSError("cp: missing operand (need source and destination)")
        self.vfs.cp(args[0], args[1])
        return ""
