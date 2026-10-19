"""Служебная команда vfs-load — загрузка новой VFS."""

from pathlib import Path

from ..vfs import VFS
from .base import Command


class VfsLoadCommand(Command):
    """Команда vfs-load. Загружает новую VFS с диска в память."""

    name = "vfs-load"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS.

        Args:
            vfs: текущая виртуальная файловая система.
        """
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить vfs-load.

        Загружает новую VFS с указанного пути. Заменяет
        текущую VFS. Старая VFS удаляется из памяти.

        Args:
            args: первым аргументом должен быть путь к директории.

        Returns:
            Строка с подтверждением.

        Raises:
            VFSError: если путь не указан или новая VFS не загружается.
        """
        if not args:
            raise VFSError("vfs-load: missing path operand")

        path = Path(args[0])
        # Загружаем во временный объект — атомарная замена.
        new_vfs = VFS.from_directory(path)
        self.vfs.replace_root(new_vfs.root, new_vfs.name)
        return f"VFS loaded: {new_vfs.name}"
