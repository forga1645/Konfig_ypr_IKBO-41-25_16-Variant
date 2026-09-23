"""Точка входа в эмулятор оболочки."""

import sys

from .repl import Repl


def main() -> int:
    """Запустить эмулятор."""
    vfs_name = "my_vfs"
    if len(sys.argv) > 1:
        vfs_name = sys.argv[1]

    repl = Repl(vfs_name=vfs_name)
    repl.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
