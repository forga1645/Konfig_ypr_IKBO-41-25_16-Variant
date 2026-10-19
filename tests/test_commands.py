"""Тесты команд этапов 4–5."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.commands.cp import CpCommand
from src.commands.du import DuCommand
from src.commands.touch import TouchCommand
from src.commands.uptime import UptimeCommand
from src.commands.vfs_load import VfsLoadCommand
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


# --- uptime ---

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


# --- wc ---

def test_wc_simple_file(vfs: VFS) -> None:
    """wc считает строки, слова, символы."""
    cmd = WcCommand(vfs=vfs)
    result = cmd.execute(["hello.txt"])
    assert result == "1 2 12 hello.txt"


def test_wc_missing_arg(vfs: VFS) -> None:
    """wc без аргументов — ошибка."""
    cmd = WcCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute([])


# --- du ---

def test_du_file(vfs: VFS) -> None:
    """du на файле — его размер."""
    cmd = DuCommand(vfs=vfs)
    result = cmd.execute(["hello.txt"])
    assert result == "12 hello.txt"


def test_du_directory(vfs: VFS) -> None:
    """du на директории — сумма размеров."""
    cmd = DuCommand(vfs=vfs)
    result = cmd.execute(["docs"])
    assert result == "6 docs"


# --- touch ---

def test_touch_creates_file(vfs: VFS) -> None:
    """touch создаёт пустой файл."""
    cmd = TouchCommand(vfs=vfs)
    result = cmd.execute(["newfile.txt"])
    assert result == ""
    node = vfs.resolve("newfile.txt")
    assert not node.is_dir
    assert node.content == ""
    assert node.size == 0


def test_touch_no_arg(vfs: VFS) -> None:
    """touch без аргументов — ошибка."""
    cmd = TouchCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute([])


def test_touch_on_directory(vfs: VFS) -> None:
    """touch на существующей папке — ошибка."""
    cmd = TouchCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute(["docs"])


def test_touch_existing_file(vfs: VFS) -> None:
    """touch на существующем файле — не ошибка."""
    cmd = TouchCommand(vfs=vfs)
    cmd.execute(["hello.txt"])
    node = vfs.resolve("hello.txt")
    assert node.content == "hello world\n"  # содержимое не изменилось


def test_touch_missing_parent(vfs: VFS) -> None:
    """touch в несуществующую папку — ошибка."""
    cmd = TouchCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute(["nonexistent/file.txt"])


# --- cp ---

def test_cp_file(vfs: VFS) -> None:
    """cp копирует файл."""
    cmd = CpCommand(vfs=vfs)
    cmd.execute(["hello.txt", "copy.txt"])
    original = vfs.resolve("hello.txt")
    copy = vfs.resolve("copy.txt")
    assert original.content == copy.content
    assert original is not copy


def test_cp_directory(vfs: VFS) -> None:
    """cp копирует папку рекурсивно."""
    cmd = CpCommand(vfs=vfs)
    cmd.execute(["docs", "docs_copy"])
    copy = vfs.resolve("docs_copy")
    assert copy.is_dir
    assert "readme.md" in copy.children


def test_cp_into_directory(vfs: VFS) -> None:
    """cp в существующую папку — копия внутри."""
    cmd = CpCommand(vfs=vfs)
    cmd.execute(["hello.txt", "docs"])
    copy = vfs.resolve("docs/hello.txt")
    assert not copy.is_dir


def test_cp_missing_args(vfs: VFS) -> None:
    """cp без аргументов — ошибка."""
    cmd = CpCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute(["only_one_arg"])


def test_cp_missing_source(vfs: VFS) -> None:
    """cp несуществующего источника — ошибка."""
    cmd = CpCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute(["nonexistent.txt", "copy.txt"])


def test_cp_into_itself(vfs: VFS) -> None:
    """cp папки в себя — ошибка."""
    cmd = CpCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute(["docs", "docs/inner"])


def test_cp_conflict(vfs: VFS) -> None:
    """cp в существующее имя — ошибка."""
    cmd = CpCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute(["hello.txt", "multi.txt"])


# --- vfs-load ---

def test_vfs_load(tmp_path: Path) -> None:
    """vfs-load заменяет VFS."""
    (tmp_path / "newfile.txt").write_text("data", encoding="utf-8")
    # Сначала загружаем пустую VFS.
    empty = tmp_path / "empty"
    empty.mkdir()
    vfs = VFS.from_directory(empty)
    assert "newfile.txt" not in vfs.list_dir()

    # Теперь загружаем другую.
    cmd = VfsLoadCommand(vfs=vfs)
    result = cmd.execute([str(tmp_path)])
    assert "VFS loaded" in result
    assert "newfile.txt" in vfs.list_dir()


def test_vfs_load_no_arg(vfs: VFS) -> None:
    """vfs-load без аргументов — ошибка."""
    cmd = VfsLoadCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute([])


def test_vfs_load_missing_path(vfs: VFS) -> None:
    """vfs-load несуществующего пути — ошибка."""
    cmd = VfsLoadCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute(["/nonexistent/path"])


def test_vfs_load_keeps_old_on_error(vfs: VFS) -> None:
    """При ошибке загрузки старая VFS сохраняется."""
    original_name = vfs.name
    cmd = VfsLoadCommand(vfs=vfs)
    with pytest.raises(VFSError):
        cmd.execute(["/nonexistent/path"])
    assert vfs.name == original_name
