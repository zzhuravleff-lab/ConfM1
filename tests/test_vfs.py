"""Тесты загрузки виртуальной файловой системы."""

import os
import tempfile
import unittest

from src.vfs import VfsError, load_vfs


VALID_XML = """<?xml version="1.0" encoding="UTF-8"?>
<vfs name="test">
  <file name="motd">Hello!</file>
  <dir name="home">
    <file name="readme.txt">Read me</file>
  </dir>
</vfs>
"""

INVALID_ROOT = '<not_vfs/>'

BROKEN_XML = "<vfs name='x'><dir name='a'>"

NO_MOTD_XML = '<?xml version="1.0"?><vfs name="x"/>'

DUPLICATE_XML = """<?xml version="1.0"?>
<vfs name="x">
  <file name="a">1</file>
  <file name="a">2</file>
</vfs>
"""


class TestLoadVfs(unittest.TestCase):
    """Проверяет загрузку VFS из XML."""

    def _write_temp(self, content: str) -> str:
        """Записать XML во временный файл и вернуть путь."""
        fd, path = tempfile.mkstemp(suffix=".xml")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def test_load_valid(self) -> None:
        path = self._write_temp(VALID_XML)
        try:
            vfs = load_vfs(path)
            self.assertEqual(vfs.name, "test")
            self.assertIn("home", vfs.root.children)
            self.assertIn("motd", vfs.root.children)
            self.assertEqual(vfs.motd, "Hello!")
        finally:
            os.unlink(path)

    def test_missing_file(self) -> None:
        with self.assertRaises(VfsError):
            load_vfs("/nonexistent/path/vfs.xml")

    def test_invalid_root_tag(self) -> None:
        path = self._write_temp(INVALID_ROOT)
        try:
            with self.assertRaises(VfsError):
                load_vfs(path)
        finally:
            os.unlink(path)

    def test_broken_xml(self) -> None:
        path = self._write_temp(BROKEN_XML)
        try:
            with self.assertRaises(VfsError):
                load_vfs(path)
        finally:
            os.unlink(path)

    def test_no_motd(self) -> None:
        path = self._write_temp(NO_MOTD_XML)
        try:
            vfs = load_vfs(path)
            self.assertIsNone(vfs.motd)
        finally:
            os.unlink(path)

    def test_duplicate_names(self) -> None:
        path = self._write_temp(DUPLICATE_XML)
        try:
            with self.assertRaises(VfsError):
                load_vfs(path)
        finally:
            os.unlink(path)

    def test_resolve_path(self) -> None:
        path = self._write_temp(VALID_XML)
        try:
            vfs = load_vfs(path)
            node = vfs.resolve("/home/readme.txt")
            self.assertIsNotNone(node)
            self.assertEqual(node.content, "Read me")
            self.assertIsNone(vfs.resolve("/nonexistent"))
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()