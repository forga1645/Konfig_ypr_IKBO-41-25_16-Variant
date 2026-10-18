"""Команда ls — вывод содержимого директории."""

from ..vfs import VFS, VFSError
from .base import Command


class LsCommand(Command):
    """Команда ls. Выводит содержимое директории в VFS."""

    name = "ls"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS.

        Args:
            vfs: виртуальная файловая система.
        """
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить ls.

        Args:
            args: если пусто — текущая директория;
                  иначе первый аргумент — путь.

        Returns:
            Строка с именами файлов через пробел.

        Raises:
            VFSError: если путь не найден или это не директория.
        """
        path = args[0] if args else ""
        names = self.vfs.list_dir(path)
        if not names:
            return ""
        return "  ".join(names)
