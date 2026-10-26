"""Чтение параметров из CLI и TOML-файла."""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


class ConfigError(Exception):
    """Ошибка чтения конфигурации."""


@dataclass
class Config:
    """Параметры запуска эмулятора."""

    vfs_path: Path | None = None
    script_path: Path | None = None
    config_path: Path | None = None


def parse_cli(argv: list[str] | None = None) -> Config:
    """Разобрать аргументы командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell-emulator", description="Эмулятор оболочки ОС."
    )
    parser.add_argument(
        "--vfs", type=Path, default=None, help="Путь к VFS."
    )
    parser.add_argument(
        "--script", type=Path, default=None, help="Путь к скрипту."
    )
    parser.add_argument(
        "--config", type=Path, default=None, help="Путь к конфигу TOML."
    )
    ns = parser.parse_args(argv)
    return Config(
        vfs_path=ns.vfs,
        script_path=ns.script,
        config_path=ns.config,
    )


def read_toml(path: Path) -> Config:
    """Прочитать TOML-файл с параметрами."""
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
    """Слить параметры CLI и файла."""
    return Config(
        vfs_path=file.vfs_path or cli.vfs_path,
        script_path=file.script_path or cli.script_path,
        config_path=cli.config_path,
    )


def load(argv: list[str] | None = None) -> Config:
    """Загрузить итоговую конфигурацию."""
    cli = parse_cli(argv)
    file = Config()
    if cli.config_path is not None:
        file = read_toml(cli.config_path)
    merged = merge(cli, file)
    debug_dump(cli, file, merged)
    return merged


def debug_dump(cli: Config, file: Config, merged: Config) -> None:
    """Напечатать отладочный вывод параметров."""
    print("[DEBUG] Configuration", file=sys.stderr)
    print(f"[DEBUG]   cli.vfs_path      = {cli.vfs_path}", 
          file=sys.stderr)
    print(f"[DEBUG]   cli.script_path   = {cli.script_path}", 
          file=sys.stderr)
    print(f"[DEBUG]   cli.config_path   = {cli.config_path}", 
          file=sys.stderr)
    print(f"[DEBUG]   file.vfs_path     = {file.vfs_path}", 
          file=sys.stderr)
    print(f"[DEBUG]   file.script_path  = {file.script_path}", 
          file=sys.stderr)
    print(f"[DEBUG]   merged.vfs_path   = {merged.vfs_path}", 
          file=sys.stderr)
    print(f"[DEBUG]   merged.script_path= {merged.script_path}", 
          file=sys.stderr)


def _to_path(value: object) -> Path | None:
    """Привести значение из TOML к Path или None."""
    if value is None:
        return None
    if not isinstance(value, str):
        err = f"expected string in TOML, got {type(value).__name__}"
        raise ConfigError(err)
    return Path(value)
