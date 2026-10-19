"""Команда du — размер файлов и папок."""

from ..vfs import VFS
from .base import Command


class DuCommand(Command):
    """Команда du. Показывает размер в байтах."""

    name = "du"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS.

        Args:
            vfs: виртуальная файловая система.
        """
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить du.

        Args:
            args: если пусто — текущая директория;
                  иначе первый аргумент — путь.

        Returns:
            Строка вида "1024 /docs".

        Raises:
            VFSError: если путь не найден.
        """
        path = args[0] if args else ""
        size = self.vfs.du(path)
        display_path = path if path else self.vfs.pwd()
        return f"{size} {display_path}"
