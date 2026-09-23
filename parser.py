"""Простой парсер командной строки."""

from dataclasses import dataclass, field


@dataclass
class ParsedCommand:
    """Результат разбора строки: имя команды и её аргументы."""

    name: str
    args: list[str] = field(default_factory=list)


def parse(line: str) -> ParsedCommand | None:
    """Разобрать строку ввода.

    Args:
        line: сырая строка от пользователя.

    Returns:
        ParsedCommand, если строка не пустая, иначе None.
    """
    tokens = line.strip().split()
    if not tokens:
        return None
    return ParsedCommand(name=tokens[0], args=tokens[1:])
