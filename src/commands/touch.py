"""Команда touch — создание пустого файла."""

from ..vfs import VFS
from .base import Command


class TouchCommand(Command):
    """Команда touch. Создаёт пустой файл в VFS."""

    name = "touch"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS.

        Args:
            vfs: виртуальная файловая система.
        """
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить touch.

        Args:
            args: первым аргументом должен быть путь к файлу.

        Returns:
            Пустая строка (touch ничего не печатает).

        Raises:
            VFSError: если путь не указан или родитель не найден.
        """
        if not args:
            raise VFSError("touch: missing file operand")
        self.vfs.touch(args[0])
        return ""
