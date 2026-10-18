"""Точка входа в эмулятор оболочки."""

import sys

from .config import ConfigError, load
from .repl import Repl
from .startup import StartupError, load_script, run_script
from .vfs import VFS, VFSError


def main(argv: list[str] | None = None) -> int:
    """Запустить эмулятор.

    Args:
        argv: аргументы командной строки.

    Returns:
        Код возврата (0 — успех, 1 — ошибка).
    """
    try:
        cfg = load(argv)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    vfs_path = cfg.vfs_path
    if vfs_path is None:
        print("VFS path is not specified.", file=sys.stderr)
        return 1

    try:
        vfs = VFS.from_directory(vfs_path)
    except VFSError as exc:
        print(f"VFS error: {exc}", file=sys.stderr)
        return 1

    repl = Repl(vfs=vfs)

    if cfg.script_path is not None:
        try:
            commands = load_script(cfg.script_path)
        except StartupError as exc:
            print(f"Startup error: {exc}", file=sys.stderr)
            return 1
        run_script(commands, repl.prompt(), repl.process_line)

    repl.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
