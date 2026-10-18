"""Виртуальная файловая система (VFS) в памяти."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


class VFSError(Exception):
    """Ошибка работы с VFS."""


@dataclass
class VFSNode:
    """Узел виртуальной файловой системы: папка или файл."""

    name: str
    is_dir: bool
    content: str = ""
    size: int = 0
    children: dict[str, VFSNode] = field(default_factory=dict)

    def __repr__(self) -> str:
        kind = "dir" if self.is_dir else "file"
        return f"VFSNode({self.name!r}, {kind})"


class VFS:
    """Виртуальная файловая система в памяти.

    Загружается из директории на диске один раз при создании.
    Все дальнейшие операции работают только с деревом в памяти.
    """

    def __init__(self, name: str, root: VFSNode) -> None:
        """Создать VFS из уже построенного дерева.

        Args:
            name: имя VFS (для отображения в приглашении).
            root: корневой узел дерева.
        """
        self.name = name
        self.root = root
        self.cwd = root

    @classmethod
    def from_directory(cls, path: Path) -> "VFS":
        """Загрузить VFS из директории на диске.

        Args:
            path: путь к директории.

        Returns:
            Готовый объект VFS.

        Raises:
            VFSError: если путь не существует или не директория.
        """
        if not path.exists():
            raise VFSError(f"VFS path not found: {path}")
        if not path.is_dir():
            raise VFSError(f"VFS path is not a directory: {path}")

        root = VFSNode(name=path.name, is_dir=True)
        cls._walk(path, root)
        return cls(name=path.name, root=root)

    @classmethod
    def _walk(cls, real_path: Path, node: VFSNode) -> None:
        """Рекурсивно обойти директорию и заполнить дерево.

        Args:
            real_path: реальный путь на диске.
            node: соответствующий узел в VFS.
        """
        try:
            entries = list(real_path.iterdir())
        except PermissionError as exc:
            raise VFSError(f"permission denied: {real_path}") from exc

        for entry in sorted(entries, key=lambda p: p.name):
            try:
                if entry.is_dir():
                    child = VFSNode(name=entry.name, is_dir=True)
                    node.children[entry.name] = child
                    cls._walk(entry, child)
                elif entry.is_file():
                    content = entry.read_text(
                        encoding="utf-8", errors="replace"
                    )
                    node.children[entry.name] = VFSNode(
                        name=entry.name,
                        is_dir=False,
                        content=content,
                        size=len(content.encode("utf-8")),
                    )
            except OSError:
                # Пропускаем файлы, которые не удаётся прочитать.
                continue

    # ---- Навигация ----

    def resolve(self, path: str) -> VFSNode:
        """Найти узел по пути.

        Поддерживает абсолютные и относительные пути, '.', '..'.

        Args:
            path: путь (абсолютный или относительный).

        Returns:
            Узел VFS.

        Raises:
            VFSError: если путь не найден или это не директория (для cwd).
        """
        if not path:
            return self.cwd

        if path.startswith("/"):
            node = self.root
            parts = [p for p in path.split("/") if p]
        else:
            node = self.cwd
            parts = [p for p in path.split("/") if p]

        for part in parts:
            if part == ".":
                continue
            if part == "..":
                node = self._parent_of(node) or self.root
                continue
            if not node.is_dir:
                raise VFSError(f"not a directory: {path}")
            child = node.children.get(part)
            if child is None:
                raise VFSError(f"no such file or directory: {path}")
            node = child
        return node

    def _parent_of(self, target: VFSNode) -> VFSNode | None:
        """Найти родителя узла, обойдя всё дерево.

        Args:
            target: узел, чей родитель ищется.

        Returns:
            Родительский узел или None, если target — корень.
        """
        if target is self.root:
            return None

        def search(node: VFSNode) -> VFSNode | None:
            for child in node.children.values():
                if child is target:
                    return node
                if child.is_dir:
                    found = search(child)
                    if found is not None:
                        return found
            return None

        return search(self.root)

    # ---- Команды ----

    def list_dir(self, path: str = "") -> list[str]:
        """Вернуть список имён в директории.

        Args:
            path: путь к директории. Пусто — текущая.

        Returns:
            Отсортированный список имён.

        Raises:
            VFSError: если путь не найден или это не директория.
        """
        node = self.resolve(path) if path else self.cwd
        if not node.is_dir:
            raise VFSError(f"not a directory: {path or '.'}")
        return sorted(node.children.keys())

    def change_dir(self, path: str) -> None:
        """Сменить текущую директорию.

        Args:
            path: путь к новой директории.

        Raises:
            VFSError: если путь не найден или это не директория.
        """
        node = self.resolve(path)
        if not node.is_dir:
            raise VFSError(f"not a directory: {path}")
        self.cwd = node

    def pwd(self) -> str:
        """Вернуть абсолютный путь текущей директории."""
        if self.cwd is self.root:
            return "/"
        parts: list[str] = []
        node = self.cwd
        while node is not self.root:
            parts.append(node.name)
            parent = self._parent_of(node)
            if parent is None:
                break
            node = parent
        return "/" + "/".join(reversed(parts))
