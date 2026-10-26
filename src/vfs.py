"""Виртуальная файловая система (VFS) в памяти."""

from __future__ import annotations

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
    """Виртуальная файловая система в памяти."""

    def __init__(self, name: str, root: VFSNode) -> None:
        """Создать VFS из уже построенного дерева."""
        self.name = name
        self.root = root
        self.cwd = root

    @classmethod
    def from_directory(cls, path: Path) -> "VFS":
        """Загрузить VFS из директории на диске."""
        if not path.exists():
            raise VFSError(f"VFS path not found: {path}")
        if not path.is_dir():
            raise VFSError(f"VFS path is not a directory: {path}")

        root = VFSNode(name=path.name, is_dir=True)
        cls._walk(path, root)
        return cls(name=path.name, root=root)

    @classmethod
    def _walk(cls, real_path: Path, node: VFSNode) -> None:
        """Рекурсивно обойти директорию и заполнить дерево."""
        try:
            entries = list(real_path.iterdir())
        except PermissionError as exc:
            raise VFSError(f"permission denied: {real_path}") from exc

        for entry in sorted(entries, key=lambda p: p.name):
            cls._process_entry(entry, node)

    @classmethod
    def _process_entry(cls, entry: Path, node: VFSNode) -> None:
        """Обработать один файл или папку."""
        try:
            if entry.is_dir():
                child = VFSNode(name=entry.name, is_dir=True)
                node.children[entry.name] = child
                cls._walk(entry, child)
            elif entry.is_file():
                cls._process_file(entry, node)
        except OSError:
            pass

    @classmethod
    def _process_file(cls, entry: Path, node: VFSNode) -> None:
        """Прочитать файл и добавить его в VFS."""
        content = entry.read_text(encoding="utf-8", errors="replace")
        node.children[entry.name] = VFSNode(
            name=entry.name,
            is_dir=False,
            content=content,
            size=len(content.encode("utf-8")),
        )


    def resolve(self, path: str) -> VFSNode:
        """Найти узел по пути."""
        if not path:
            return self.cwd

        node = self.root if path.startswith("/") else self.cwd
        parts = [p for p in path.split("/") if p]

        for part in parts:
            node = self._step_resolve(node, part, path)
        return node

    def _step_resolve(
        self, node: VFSNode, part: str, full_path: str
    ) -> VFSNode:
        """Сделать один шаг навигации по дереву."""
        if part == ".":
            return node
        if part == "..":
            return self._parent_of(node) or self.root

        if not node.is_dir:
            raise VFSError(f"not a directory: {full_path}")

        child = node.children.get(part)
        if child is None:
            raise VFSError(f"no such file or directory: {full_path}")
        return child

    def _parent_of(self, target: VFSNode) -> VFSNode | None:
        """Найти родителя узла."""
        if target is self.root:
            return None
        return self._search_parent(self.root, target)

    def _search_parent(
        self, current: VFSNode, target: VFSNode
    ) -> VFSNode | None:
        """Вспомогательный рекурсивный поиск родителя."""
        for child in current.children.values():
            if child is target:
                return current
            if child.is_dir:
                found = self._search_parent(child, target)
                if found is not None:
                    return found
        return None


    def list_dir(self, path: str = "") -> list[str]:
        """Вернуть список имён в директории."""
        node = self.resolve(path) if path else self.cwd
        if not node.is_dir:
            raise VFSError(f"not a directory: {path or '.'}")
        return sorted(node.children.keys())

    def change_dir(self, path: str) -> None:
        """Сменить текущую директорию."""
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


    def wc(self, path: str) -> tuple[int, int, int]:
        """Подсчитать строки, слова и символы в файле."""
        node = self.resolve(path)
        if node.is_dir:
            raise VFSError(f"is a directory: {path}")

        text = node.content
        lines = text.count("\n")
        if text and not text.endswith("\n"):
            lines += 1
        words = len(text.split())
        chars = len(text)
        return lines, words, chars

    def du(self, path: str = "") -> int:
        """Подсчитать суммарный размер в байтах."""
        node = self.resolve(path) if path else self.cwd
        return self._size_of(node)

    def _size_of(self, node: VFSNode) -> int:
        """Рекурсивно подсчитать размер узла в байтах."""
        if not node.is_dir:
            return node.size
        return sum(self._size_of(child) for child in node.children.values())


    def touch(self, path: str) -> None:
        """Создать пустой файл."""
        try:
            node = self.resolve(path)
        except VFSError:
            node = None

        if node is not None:
            if node.is_dir:
                raise VFSError(f"is a directory: {path}")
            return

        parent, name = self._resolve_parent_and_name(path)
        parent.children[name] = VFSNode(
            name=name, is_dir=False, content="", size=0
        )

    def cp(self, src: str, dst: str) -> None:
        """Копировать файл или папку внутри VFS."""
        src_node = self.resolve(src)
        if src_node is self.root:
            raise VFSError("cannot copy root directory")

        if src_node.is_dir and self._is_inside(src_node, dst):
            raise VFSError(f"cannot copy directory into itself: {dst}")

        try:
            dst_node = self.resolve(dst)
        except VFSError:
            dst_node = None

        if dst_node is not None and dst_node.is_dir:
            target_parent = dst_node
            target_name = src_node.name
        else:
            parent, name = self._resolve_parent_and_name(dst)
            target_parent = parent
            target_name = name

        if target_name in target_parent.children:
            raise VFSError(f"already exists: {dst}")

        copy = self._deep_copy(src_node, target_name)
        target_parent.children[target_name] = copy

    def _deep_copy(
        self, node: VFSNode, new_name: str | None = None
    ) -> VFSNode:
        """Создать глубокую копию узла."""
        name = new_name if new_name is not None else node.name
        if node.is_dir:
            copy = VFSNode(name=name, is_dir=True)
            for child in node.children.values():
                copy.children[child.name] = self._deep_copy(child)
            return copy
        return VFSNode(
            name=name,
            is_dir=False,
            content=node.content,
            size=node.size,
        )

    def _is_inside(self, parent: VFSNode, dst_path: str) -> bool:
        """Проверить, находится ли dst_path внутри parent."""
        try:
            dst_node = self.resolve(dst_path)
        except VFSError:
            try:
                parent_node, _ = self._resolve_parent_and_name(dst_path)
            except VFSError:
                return False
            dst_node = parent_node

        return self._contains_node(parent, dst_node)

    def _contains_node(self, root: VFSNode, target: VFSNode) -> bool:
        """Рекурсивно проверить, есть ли target внутри root."""
        if root is target:
            return True
        if not root.is_dir:
            return False
        return any(
            self._contains_node(c, target) for c in root.children.values()
        )

    def _resolve_parent_and_name(self, path: str) -> tuple[VFSNode, str]:
        """Найти родителя и имя последнего элемента пути."""
        if path.startswith("/"):
            base = self.root
            parts = [p for p in path.split("/") if p]
        else:
            base = self.cwd
            parts = [p for p in path.split("/") if p]

        if not parts:
            raise VFSError(f"invalid path: {path}")

        name = parts[-1]
        parent = base
        for part in parts[:-1]:
            parent = self._step_parent_resolve(parent, part, path)

        if not parent.is_dir:
            raise VFSError(f"not a directory: {path}")
        return parent, name

    def _step_parent_resolve(
        self, parent: VFSNode, part: str, full_path: str
    ) -> VFSNode:
        """Шаг навигации при поиске родителя."""
        if part == ".":
            return parent
        if part == "..":
            return self._parent_of(parent) or self.root
        if not parent.is_dir:
            raise VFSError(f"not a directory: {full_path}")
        child = parent.children.get(part)
        if child is None:
            raise VFSError(f"no such file or directory: {full_path}")
        return child

    def replace_root(self, new_root: VFSNode, new_name: str) -> None:
        """Заменить корень VFS целиком."""
        self.root = new_root
        self.cwd = new_root
        self.name = new_name
