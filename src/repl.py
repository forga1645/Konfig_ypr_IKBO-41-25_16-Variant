"""REPL — Read-Eval-Print Loop эмулятора."""

from .commands import get_command
from .commands.exit import ExitRequested
from .errors import ShellError, UnknownCommandError
from .parser import parse
from .vfs import VFS


class Repl:
    """Интерактивный цикл эмулятора оболочки."""

    def __init__(self, vfs: VFS) -> None:
        """Создать REPL с заданной VFS.

        Args:
            vfs: виртуальная файловая система.
        """
        self.vfs = vfs

    def prompt(self) -> str:
        """Сформировать строку приглашения.

        Имя VFS + текущий путь.
        """
        return f"{self.vfs.name}:{self.vfs.pwd()}> "

    def process_line(self, line: str) -> None:
        """Обработать строку без прерывания на ошибках.

        Args:
            line: сырая строка.
        """
        try:
            self.handle(line)
        except ShellError as exc:
            print(f"Error: {exc}")
        except ExitRequested:
            raise

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
        """Обработать одну строку ввода.

        Args:
            line: сырая строка.

        Raises:
            ShellError: при ошибках выполнения команды.
            ExitRequested: при команде exit.
        """
        parsed = parse(line)
        if parsed is None:
            return

        command = get_command(parsed.name, self.vfs)
        if command is None:
            raise UnknownCommandError(parsed.name)

        try:
            result = command.execute(parsed.args)
        except Exception as exc:
            # VFSError тоже превращаем в понятное сообщение.
            from .vfs import VFSError
            if isinstance(exc, VFSError):
                print(f"Error: {exc}")
                return
            raise

        if result:
            print(result)
