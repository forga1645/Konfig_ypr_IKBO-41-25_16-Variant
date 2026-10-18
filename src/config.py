"""Чтение параметров из CLI и TOML-файла."""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


class ConfigError(Exception):
    """Ошибка чтения конфигурации."""


@dataclass
class Config:
    """Параметры запуска эмулятора."""

    vfs_path: Path | None = None
    script_path: Path | None = None
    config_path: Path | None = None


def parse_cli(argv: list[str] | None = None) -> Config:
    """Разобрать аргументы командной строки.

    Args:
        argv: список аргументов (по умолчанию — sys.argv[1:]).

    Returns:
        Config с заполненными полями из CLI.
    """
    parser = argparse.ArgumentParser(
        prog="shell-emulator",
        description="Эмулятор оболочки ОС. Этап 2: конфигурация.",
    )
    parser.add_argument(
        "--vfs",
        type=Path,
        default=None,
        help="Путь к физическому расположению VFS.",
    )
    parser.add_argument(
        "--script",
        type=Path,
        default=None,
        help="Путь к стартовому скрипту.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Путь к конфигурационному файлу TOML.",
    )
    ns = parser.parse_args(argv)
    return Config(
        vfs_path=ns.vfs,
        script_path=ns.script,
        config_path=ns.config,
    )


def read_toml(path: Path) -> Config:
    """Прочитать TOML-файл с параметрами.

    Args:
        path: путь к TOML-файлу.

    Returns:
        Config с параметрами из файла.

    Raises:
        ConfigError: если файл не найден или повреждён.
    """
    if not path.exists():
        raise ConfigError(f"config file not found: {path}")
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid TOML in {path}: {exc}") from exc

    return Config(
        vfs_path=_to_path(data.get("vfs_path")),
        script_path=_to_path(data.get("script_path")),
    )


def merge(cli: Config, file: Config) -> Config:
    """Слить параметры CLI и файла.

    По заданию варианта №16 приоритет у файла: значения из TOML
    перекрывают значения из командной строки.

    Args:
        cli: параметры из командной строки.
        file: параметры из TOML-файла.

    Returns:
        Итоговый Config.
    """
    return Config(
        vfs_path=file.vfs_path or cli.vfs_path,
        script_path=file.script_path or cli.script_path,
        config_path=cli.config_path,
    )


def load(argv: list[str] | None = None) -> Config:
    """Загрузить итоговую конфигурацию.

    Порядок:
    1. Разобрать CLI.
    2. Если указан --config, прочитать TOML.
    3. Слить с приоритетом файла.
    4. Показать отладочный вывод.

    Args:
        argv: аргументы (по умолчанию — sys.argv[1:]).

    Returns:
        Итоговый Config.

    Raises:
        ConfigError: при проблемах с конфигурационным файлом.
    """
    cli = parse_cli(argv)
    file = Config()
    if cli.config_path is not None:
        file = read_toml(cli.config_path)
    merged = merge(cli, file)
    debug_dump(cli, file, merged)
    return merged


def debug_dump(cli: Config, file: Config, merged: Config) -> None:
    """Напечатать отладочный вывод параметров.

    Args:
        cli: параметры из CLI.
        file: параметры из TOML.
        merged: итоговые параметры.
    """
    print("[DEBUG] Configuration", file=sys.stderr)
    print(f"[DEBUG]   cli.vfs_path      = {cli.vfs_path}", file=sys.stderr)
    print(f"[DEBUG]   cli.script_path   = {cli.script_path}", file=sys.stderr)
    print(f"[DEBUG]   cli.config_path   = {cli.config_path}", file=sys.stderr)
    print(f"[DEBUG]   file.vfs_path     = {file.vfs_path}", file=sys.stderr)
    print(f"[DEBUG]   file.script_path  = {file.script_path}", file=sys.stderr)
    print(f"[DEBUG]   merged.vfs_path   = {merged.vfs_path}", file=sys.stderr)
    print(f"[DEBUG]   merged.script_path= {merged.script_path}", file=sys.stderr)


def _to_path(value: object) -> Path | None:
    """Привести значение из TOML к Path или None.

    Args:
        value: значение из TOML (строка или None).

    Returns:
        Path или None.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f"expected string in TOML, got {type(value).__name__}")
    return Path(value)
