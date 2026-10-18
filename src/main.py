"""Точка входа в эмулятор оболочки."""

import sys
from pathlib import Path

from .config import Config, ConfigError, load
from .repl import Repl
from .startup import StartupError, load_script, run_script


def main(argv: list[str] | None = None) -> int:
    """Запустить эмулятор.

    Args:
        argv: аргументы командной строки (по умолчанию — sys.argv[1:]).

    Returns:
        Код возврата (0 — успех, 1 — ошибка конфигурации).
    """
    try:
        cfg = load(argv)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    vfs_name = _vfs_name(cfg.vfs_path)
    repl = Repl(vfs_name=vfs_name)

    if cfg.script_path is not None:
        try:
            commands = load_script(cfg.script_path)
        except StartupError as exc:
            print(f"Startup error: {exc}", file=sys.stderr)
            return 1
        run_script(commands, repl.prompt(), repl.process_line)

    repl.run()
    return 0


def _vfs_name(path: Path | None) -> str:
    """Определить имя VFS для приглашения.

    Args:
        path: путь к VFS (может быть None).

    Returns:
        Имя VFS: имя папки, либо 'my_vfs' по умолчанию.
    """
    if path is None:
        return "my_vfs"
    return path.name


if __name__ == "__main__":
    sys.exit(main())
