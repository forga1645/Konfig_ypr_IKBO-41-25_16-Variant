"""Тесты конфигурации."""

from pathlib import Path

import pytest

from src.config import (
    Config,
    ConfigError,
    merge,
    parse_cli,
    read_toml,
)


def test_parse_cli_empty() -> None:
    """Пустой CLI даёт Config с None-полями."""
    cfg = parse_cli([])
    assert cfg.vfs_path is None
    assert cfg.script_path is None
    assert cfg.config_path is None


def test_parse_cli_all_args(tmp_path: Path) -> None:
    """Разбор всех флагов."""
    vfs = tmp_path / "vfs"
    script = tmp_path / "start.txt"
    config = tmp_path / "cfg.toml"
    cfg = parse_cli([
        "--vfs", str(vfs),
        "--script", str(script),
        "--config", str(config),
    ])
    assert cfg.vfs_path == vfs
    assert cfg.script_path == script
    assert cfg.config_path == config


def test_read_toml(tmp_path: Path) -> None:
    """Чтение TOML-файла."""
    toml_file = tmp_path / "cfg.toml"
    toml_file.write_text(
        'vfs_path = "vfs"\nscript_path = "start.txt"\n',
        encoding="utf-8",
    )
    cfg = read_toml(toml_file)
    assert cfg.vfs_path == Path("vfs")
    assert cfg.script_path == Path("start.txt")


def test_read_toml_missing() -> None:
    """Отсутствующий TOML — ConfigError."""
    with pytest.raises(ConfigError):
        read_toml(Path("/nonexistent/file.toml"))


def test_read_toml_invalid(tmp_path: Path) -> None:
    """Повреждённый TOML — ConfigError."""
    bad = tmp_path / "bad.toml"
    bad.write_text("this is = not valid = toml", encoding="utf-8")
    with pytest.raises(ConfigError):
        read_toml(bad)


def test_merge_file_overrides_cli() -> None:
    """Приоритет у файла над CLI (вариант №16)."""
    cli = Config(
        vfs_path=Path("cli_vfs"),
        script_path=Path("cli_script.txt"),
    )
    file = Config(
        vfs_path=Path("file_vfs"),
        script_path=Path("file_script.txt"),
    )
    merged = merge(cli, file)
    assert merged.vfs_path == Path("file_vfs")
    assert merged.script_path == Path("file_script.txt")


def test_merge_fills_missing() -> None:
    """Поля, отсутствующие в файле, берутся из CLI."""
    cli = Config(
        vfs_path=Path("cli_vfs"),
        script_path=Path("cli_script.txt"),
    )
    file = Config(vfs_path=None, script_path=None)
    merged = merge(cli, file)
    assert merged.vfs_path == Path("cli_vfs")
    assert merged.script_path == Path("cli_script.txt")
