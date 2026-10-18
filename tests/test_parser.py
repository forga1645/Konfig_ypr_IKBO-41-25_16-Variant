"""Тесты парсера команд."""

from src.parser import ParsedCommand, parse


def test_parse_simple_command() -> None:
    """Команда без аргументов."""
    result = parse("ls")
    assert result == ParsedCommand(name="ls", args=[])


def test_parse_command_with_args() -> None:
    """Команда с несколькими аргументами."""
    result = parse("ls -la /home")
    assert result is not None
    assert result.name == "ls"
    assert result.args == ["-la", "/home"]


def test_parse_empty_line() -> None:
    """Пустая строка — None."""
    assert parse("") is None
    assert parse("   ") is None
    assert parse("\t\n") is None


def test_parse_extra_spaces() -> None:
    """Лишние пробелы игнорируются."""
    result = parse("  cd    /home  ")
    assert result is not None
    assert result.name == "cd"
    assert result.args == ["/home"]
