"""Тесты оболочки Shell."""
"""python -m unittest discover -s tests"""

import unittest
from io import StringIO
from unittest.mock import patch

from src.shell import Shell
from src.vfs import VfsNode, VirtualFileSystem


def _make_vfs() -> VirtualFileSystem:
    """Построить тестовую VFS: /home/readme.txt, /etc/hosts."""
    home = VfsNode(name="home", is_dir=True)
    home.children["readme.txt"] = VfsNode(
        name="readme.txt", is_dir=False, content="hello",
    )
    etc = VfsNode(name="etc", is_dir=True)
    etc.children["hosts"] = VfsNode(
        name="hosts", is_dir=False, content="127.0.0.1",
    )
    root = VfsNode(name="/", is_dir=True)
    root.children["home"] = home
    root.children["etc"] = etc
    return VirtualFileSystem(name="test", root=root)


class TestShellLs(unittest.TestCase):
    """Проверяет команду ls."""

    def setUp(self) -> None:
        self.shell = Shell(vfs=_make_vfs())

    def _run(self, line: str) -> str:
        out = StringIO()
        with patch("sys.stdout", out):
            self.shell.execute(line)
        return out.getvalue().strip()

    def test_ls_root(self) -> None:
        self.assertEqual(self._run("ls"), "etc home")

    def test_ls_dir(self) -> None:
        self.assertEqual(self._run("ls /home"), "readme.txt")

    def test_ls_file(self) -> None:
        self.assertEqual(self._run("ls /home/readme.txt"), "readme.txt")

    def test_ls_missing(self) -> None:
        self.assertIn("No such file", self._run("ls /nope"))

    def test_ls_too_many_args(self) -> None:
        self.assertIn("too many", self._run("ls a b"))


class TestShellCd(unittest.TestCase):
    """Проверяет команду cd."""

    def setUp(self) -> None:
        self.shell = Shell(vfs=_make_vfs())

    def _run(self, line: str) -> str:
        out = StringIO()
        with patch("sys.stdout", out):
            self.shell.execute(line)
        return out.getvalue().strip()

    def test_cd_absolute(self) -> None:
        self._run("cd /home")
        self.assertEqual(self.shell.cwd, "/home")

    def test_cd_parent(self) -> None:
        self._run("cd /home")
        self._run("cd ..")
        self.assertEqual(self.shell.cwd, "/")

    def test_cd_dot(self) -> None:
        self._run("cd /home")
        self._run("cd .")
        self.assertEqual(self.shell.cwd, "/home")

    def test_cd_to_file(self) -> None:
        self._run("cd /home/readme.txt")
        self.assertEqual(self.shell.cwd, "/")
        self.assertIn("not a directory", self._run("cd /home/readme.txt"))

    def test_cd_missing(self) -> None:
        self.assertIn("no such", self._run("cd /nope"))

    def test_cd_no_args(self) -> None:
        self._run("cd /home")
        self._run("cd")
        self.assertEqual(self.shell.cwd, "/")


class TestShellEcho(unittest.TestCase):
    """Проверяет команду echo."""

    def setUp(self) -> None:
        self.shell = Shell(vfs=_make_vfs())

    def _run(self, line: str) -> str:
        out = StringIO()
        with patch("sys.stdout", out):
            self.shell.execute(line)
        return out.getvalue().strip()

    def test_echo_args(self) -> None:
        self.assertEqual(self._run("echo hello world"), "hello world")

    def test_echo_empty(self) -> None:
        self.assertEqual(self._run("echo"), "")

    def test_echo_literal_var(self) -> None:
        self.assertEqual(self._run("echo $HOME"), "$HOME")


class TestShellHistory(unittest.TestCase):
    """Проверяет команду history."""

    def setUp(self) -> None:
        self.shell = Shell(vfs=_make_vfs())

    def _run(self, line: str) -> str:
        out = StringIO()
        with patch("sys.stdout", out):
            self.shell.execute(line)
        return out.getvalue().strip()

    def test_history_empty(self) -> None:
        result = self._run("history")
        self.assertIn("history", result)
        self.assertEqual(len(result.splitlines()), 1)

    def test_history_records(self) -> None:
        self._run("echo a")
        self._run("echo b")
        result = self._run("history")
        self.assertIn("echo a", result)
        self.assertIn("echo b", result)
        self.assertIn("history", result)

    def test_history_too_many_args(self) -> None:
        self.assertIn("too many", self._run("history x"))


class TestShellClear(unittest.TestCase):
    """Проверяет команду clear."""

    def setUp(self) -> None:
        self.shell = Shell(vfs=_make_vfs())

    def test_clear_in_script_is_noop(self) -> None:
        self.shell.in_script = True
        with patch("os.system") as mock_sys:
            self.shell.execute("clear")
            mock_sys.assert_not_called()


if __name__ == "__main__":
    unittest.main()