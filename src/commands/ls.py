"""Команда ls — вывод содержимого директории."""

from ..vfs import VFS, human_size
from .base import Command


class LsCommand(Command):
    """Команда ls. Выводит содержимое директории в VFS.

    Поддерживает флаги:
        -l — подробный вывод (имя, тип, размер)
        -h — человекочитаемые размеры (K, M, G)
        -a — показывать все файлы, включая скрытые
    """

    name = "ls"

    def __init__(self, vfs: VFS) -> None:
        """Создать команду с доступом к VFS."""
        self.vfs = vfs

    def execute(self, args: list[str]) -> str:
        """Выполнить ls.

        Args:
            args: флаги и путь.

        Returns:
            Строка с именами файлов (или подробностями).

        Raises:
            VFSError: если путь не найден или это не директория.
        """
        flags, paths = self._parse_args(args)
        path = paths[0] if paths else ""

        items = self.vfs.list_dir_detailed(
            path=path, show_all="a" in flags
        )
        if not items:
            return ""

        if "l" in flags:
            return self._format_long(items, human="h" in flags)
        return self._format_short(items, show_all="a" in flags)

    @staticmethod
    def _parse_args(args: list[str]) -> tuple[set[str], list[str]]:
        """Разделить аргументы на флаги и пути.

        Поддерживает комбинированные флаги: -la = -l -a.

        Args:
            args: список аргументов.

        Returns:
            Кортеж (множество флагов, список путей).
        """
        flags: set[str] = set()
        paths: list[str] = []
        for arg in args:
            if arg.startswith("-") and not arg.startswith("--"):
                flags.update(arg[1:])
            else:
                paths.append(arg)
        return flags, paths

    @staticmethod
    def _format_short(
        items: list[tuple[str, object]], show_all: bool = False
    ) -> str:
        """Короткий вывод: только имена.

        Args:
            items: список пар (имя, узел).
            show_all: если True — добавить '.' и '..' в начало.

        Returns:
            Строка с именами через два пробела.
        """
        names = [name for name, _ in items]
        if show_all:
            names = [".", ".."] + names
        return "  ".join(names)

    @staticmethod
    def _format_long(
        items: list[tuple[str, object]], human: bool
    ) -> str:
        """Подробный вывод: имя, тип, размер.

        Args:
            items: список пар (имя, узел).
            human: если True — размеры в K/M/G.

        Returns:
            Многострочная строка.
        """
        lines: list[str] = []
        for name, node in items:
            kind = "d" if node.is_dir else "-"
            if node.is_dir:
                size_str = "-"
            else:
                size_str = human_size(node.size) if human else str(node.size)
            lines.append(f"{kind}  {size_str:>8}  {name}")
        return "\n".join(lines)
