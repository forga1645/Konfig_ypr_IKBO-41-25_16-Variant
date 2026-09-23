"""REPL — Read-Eval-Print Loop эмулятора."""

from .commands import get_command
from .commands.exit import ExitRequested
from .errors import ShellError, UnknownCommandError
from .parser import parse


class Repl:
    """Интерактивный цикл эмулятора оболочки."""

    def __init__(self, vfs_name: str = "my_vfs") -> None:
        self.vfs_name = vfs_name

    def prompt(self) -> str:
        """Сформировать строку приглашения."""
        return f"{self.vfs_name}> "

    def run(self) -> None:
        """Запустить цикл REPL до команды exit или Ctrl+D."""
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
            except Exception as exc:  # noqa: BLE001
                print(f"Unexpected error: {exc}")

    def handle(self, line: str) -> None:
        """Обработать одну строку ввода."""
        parsed = parse(line)
        if parsed is None:
            return

        command = get_command(parsed.name)
        if command is None:
            raise UnknownCommandError(parsed.name)

        result = command.execute(parsed.args)
        if result:
            print(result)
