"""Тесты виртуальной файловой системы."""

from pathlib import Path

import pytest

from src.vfs import VFS, VFSError


@pytest.fixture
def vfs(tmp_path: Path) -> VFS:
    """Создать тестовую VFS со структурой.

    tmp_path — фикстура pytest, даёт временную папку.
    """
    (tmp_path / "file1.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "file2.txt").write_text("world!", encoding="utf-8")
    sub = tmp_path / "docs"
    sub.mkdir()
    (sub / "readme.md").write_text("# Readme", encoding="utf-8")
    deep = sub / "a" / "b"
    deep.mkdir(parents=True)
    (deep / "deep.txt").write_text("deep content", encoding="utf-8")
    return VFS.from_directory(tmp_path)


def test_load_vfs(vfs: VFS) -> None:
    """VFS загружается из директории."""
    assert vfs.root.is_dir
    assert "file1.txt" in vfs.root.children
    assert "docs" in vfs.root.children


def test_load_vfs_missing() -> None:
    """Несуществующий путь — VFSError."""
    with pytest.raises(VFSError):
        VFS.from_directory(Path("/nonexistent/path"))


def test_load_vfs_not_directory(tmp_path: Path) -> None:
    """Файл вместо директории — VFSError."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(VFSError):
        VFS.from_directory(file_path)


def test_list_dir_root(vfs: VFS) -> None:
    """ls в корне показывает файлы и папки."""
    names = vfs.list_dir()
    assert "file1.txt" in names
    assert "file2.txt" in names
    assert "docs" in names


def test_change_dir(vfs: VFS) -> None:
    """cd меняет текущую директорию."""
    vfs.change_dir("docs")
    assert vfs.cwd.name == "docs"
    names = vfs.list_dir()
    assert "readme.md" in names


def test_change_dir_missing(vfs: VFS) -> None:
    """cd в несуществующую папку — VFSError."""
    with pytest.raises(VFSError):
        vfs.change_dir("nonexistent")


def test_change_dir_to_file(vfs: VFS) -> None:
    """cd в файл — VFSError."""
    with pytest.raises(VFSError):
        vfs.change_dir("file1.txt")


def test_pwd(vfs: VFS) -> None:
    """pwd возвращает абсолютный путь."""
    assert vfs.pwd() == "/"
    vfs.change_dir("docs")
    assert vfs.pwd() == "/docs"


def test_deep_navigation(vfs: VFS) -> None:
    """Работа с глубокой вложенностью."""
    vfs.change_dir("docs")
    vfs.change_dir("a")
    vfs.change_dir("b")
    assert vfs.cwd.name == "b"
    names = vfs.list_dir()
    assert "deep.txt" in names


def test_parent_navigation(vfs: VFS) -> None:
    """Переход через .. работает."""
    vfs.change_dir("docs")
    vfs.change_dir("a")
    vfs.change_dir("..")
    assert vfs.cwd.name == "docs"


def test_absolute_path(vfs: VFS) -> None:
    """Абсолютный путь работает."""
    vfs.change_dir("/docs/a/b")
    assert vfs.cwd.name == "b"


def test_file_content(vfs: VFS) -> None:
    """Содержимое файла читается."""
    node = vfs.resolve("file1.txt")
    assert node.content == "hello"
    assert node.size == 5

# Добавь в конец tests/test_vfs.py


def test_vfs_wc(vfs: VFS) -> None:
    """VFS.wc считает строки, слова, символы."""
    lines, words, chars = vfs.wc("file1.txt")
    # "hello" — 1 строка, 1 слово, 5 символов
    assert lines == 1
    assert words == 1
    assert chars == 5


def test_vfs_wc_directory(vfs: VFS) -> None:
    """VFS.wc на директории — VFSError."""
    with pytest.raises(VFSError):
        vfs.wc("docs")


def test_vfs_du_file(vfs: VFS) -> None:
    """VFS.du на файле — размер."""
    size = vfs.du("file1.txt")
    assert size == 5


def test_vfs_du_directory(vfs: VFS) -> None:
    """VFS.du на директории — сумма."""
    size = vfs.du("docs")
    assert size > 0
