"""Тесты команд этапов 4 и 5."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.commands.du import DuCommand
from src.commands.uptime import UptimeCommand
from src.commands.wc import WcCommand
from src.vfs import VFS, VFSError


@pytest.fixture
def vfs(tmp_path: Path) -> VFS:
    """Создать тестовую VFS."""
    (tmp_path / "hello.txt").write_text("hello world\n", encoding="utf-8")
    (tmp_path / "multi.txt").write_text(
        "line 1\nline 2\nline 3\n", encoding="utf-8"
    )
    sub = tmp_path / "docs"
    sub.mkdir()
    (sub / "readme.md").write_text("readme", encoding="utf-8")
    return VFS.from_directory(tmp_path)


def test_uptime_seconds() -> None:
    """uptime показывает секунды."""
    started = datetime.now() - timedelta(seconds=5)
    cmd = UptimeCommand(started_at=started)
    result = cmd.execute([])
    assert result.startswith("Up ")
    assert "second" in result


def test_uptime_minutes() -> None:
    """uptime показывает минуты."""
    started = datetime.now() - timedelta(minutes=2, seconds=30)
    cmd = UptimeCommand(started_at=started)
    result = cmd.execute([])
    assert "minute" in result


def test_wc_simple_file(vfs: VFS) -> None:
    """wc считает строки, слова, символы.

    Файл содержит 'hello world\\n' (1 строка, 2 слова, 12 символов).
    """
    cmd = WcCommand(vfs=vfs)
    result = cmd.execute(["hello.txt"])
    assert result == "1 2 12 hello.txt"


def test_wc_multiline(vfs: VFS) -> None:
    """wc на многострочном файле.

    Файл содержит 'line 1\\nline 2\\nline 3\\n' (3 строки, 6 слов, 21 символ).
    """
    cmd = WcCommand(vfs=vfs)
    result = cmd.execute(["multi.txt"])
    assert result == "3 6 21 multi.txt"


def test_wc_missing_arg(vfs: VFS) -> None:
    """wc без аргументов — ошибка."""
    cmd = WcCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute([])


def test_du_file(vfs: VFS) -> None:
    """du на файле — его размер.

    Файл 'hello world\\n' весит 12 байт.
    """
    cmd = DuCommand(vfs=vfs)
    result = cmd.execute(["hello.txt"])
    assert result == "12 hello.txt"


def test_du_directory(vfs: VFS) -> None:
    """du на директории — сумма размеров."""
    cmd = DuCommand(vfs=vfs)
    result = cmd.execute(["docs"])
    assert result == "6 docs"
