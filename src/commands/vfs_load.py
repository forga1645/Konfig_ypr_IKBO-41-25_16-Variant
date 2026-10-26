"""Служебная команда vfs-load — загрузка новой VFS."""

from pathlib import Path

from ..vfs import VFS
from .base import Command


class VfsLoadCommand(Command):
    """Команда vfs-load. Загружает новую VFS с диска в память."""

    name = "vfs-load"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS."""
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить vfs-load."""
        if not args:
            raise VFSError("vfs-load: missing path operand")

        path = Path(args[0])
        new_vfs = VFS.from_directory(path)
        self.vfs.replace_root(new_vfs.root, new_vfs.name)
        return f"VFS loaded: {new_vfs.name}"
