"""Команда cd — смена текущей директории."""

from ..vfs import VFS
from .base import Command


class CdCommand(Command):
    """Команда cd. Меняет текущую директорию в VFS."""

    name = "cd"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS.

        Args:
            vfs: виртуальная файловая система.
        """
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить cd.

        Args:
            args: если пусто — перейти в корень;
                  иначе первый аргумент — путь.

        Returns:
            Пустая строка (cd ничего не печатает).

        Raises:
            VFSError: если путь не найден или это не директория.
        """
        path = args[0] if args else "/"
        self.vfs.change_dir(path)
        return ""
