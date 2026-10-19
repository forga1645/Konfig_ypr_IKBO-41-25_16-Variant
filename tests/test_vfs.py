# Добавь в конец tests/test_vfs.py


def test_vfs_touch(vfs: VFS) -> None:
    """VFS.touch создаёт файл."""
    vfs.touch("newfile.txt")
    node = vfs.resolve("newfile.txt")
    assert not node.is_dir
    assert node.content == ""


def test_vfs_cp_file(vfs: VFS) -> None:
    """VFS.cp копирует файл."""
    vfs.cp("file1.txt", "copy.txt")
    assert vfs.resolve("copy.txt").content == "hello"


def test_vfs_cp_dir(vfs: VFS) -> None:
    """VFS.cp копирует директорию."""
    vfs.cp("docs", "docs_copy")
    assert vfs.resolve("docs_copy").is_dir


def test_vfs_cp_into_itself(vfs: VFS) -> None:
    """VFS.cp папки в себя — VFSError."""
    with pytest.raises(VFSError):
        vfs.cp("docs", "docs/inner")


def test_vfs_replace_root(vfs: VFS) -> None:
    """VFS.replace_root заменяет корень."""
    from src.vfs import VFSNode
    new_root = VFSNode(name="new", is_dir=True)
    vfs.replace_root(new_root, "new")
    assert vfs.name == "new"
    assert vfs.root is new_root
    assert vfs.cwd is new_root
