"""Команда wc — подсчёт строк, слов и символов."""

from ..vfs import VFS, VFSError
from .base import Command


class WcCommand(Command):
    """Команда wc. Считает строки, слова и символы в файле."""

    name = "wc"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS.

        Args:
            vfs: виртуальная файловая система.
        """
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить wc.

        Args:
            args: первым аргументом должен быть путь к файлу.

        Returns:
            Строка вида "12 45 320 file.txt".

        Raises:
            VFSError: если файл не найден.
        """
        if not args:
            raise VFSError("wc: missing file operand")
        path = args[0]
        lines, words, chars = self.vfs.wc(path)
        return f"{lines} {words} {chars} {path}"
