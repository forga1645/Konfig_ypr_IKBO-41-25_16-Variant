"""REPL — Read-Eval-Print Loop эмулятора."""

from datetime import datetime

from .commands import get_command
from .commands.exit import ExitRequested
from .errors import ShellError, UnknownCommandError
from .parser import parse
from .vfs import VFS, VFSError


class Repl:
    """Интерактивный цикл эмулятора оболочки."""

    def __init__(self, vfs: VFS, started_at: datetime | None = None) -> None:
        """Создать REPL.

        Args:
            vfs: виртуальная файловая система.
            started_at: время старта (по умолчанию — сейчас).
        """
        self.vfs = vfs
        self.started_at = started_at or datetime.now()

    def prompt(self) -> str:
        """Сформировать строку приглашения."""
        return f"{self.vfs.name}:{self.vfs.pwd()}> "

    def process_line(self, line: str) -> None:
        """Обработать строку без прерывания на ошибках."""
        try:
            self.handle(line)
        except ShellError as exc:
            print(f"Error: {exc}")
        except VFSError as exc:
            print(f"Error: {exc}")
        except ExitRequested:
            raise

    def run(self) -> None:
        """Запустить цикл REPL до exit или Ctrl+D."""
        while True:
            try:
                line = input(self.prompt())
            except EOFError:
                print()
                break

            try:
                self.handle(line)
            except ExitRequested:
                print("Bye!")
                break
            except ShellError as exc:
                print(f"Error: {exc}")
            except VFSError as exc:
                print(f"Error: {exc}")
            except Exception as exc:  # noqa: BLE001
                print(f"Unexpected error: {exc}")

    def handle(self, line: str) -> None:
        """Обработать одну строку ввода."""
        parsed = parse(line)
        if parsed is None:
            return

        command = get_command(parsed.name, self.vfs, self.started_at)
        if command is None:
            raise UnknownCommandError(parsed.name)

        result = command.execute(parsed.args)
        if result:
            print(result)
