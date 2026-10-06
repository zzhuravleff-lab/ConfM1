"""Тесты парсера команд эмулятора VFS."""

import unittest

from src.main import parse_command


class TestParseCommand(unittest.TestCase):
    """Проверяет корректность разбора строки ввода."""

    def test_empty_line(self) -> None:
        self.assertEqual(parse_command(""), (None, []))

    def test_only_spaces(self) -> None:
        self.assertEqual(parse_command("    "), (None, []))

    def test_simple_command(self) -> None:
        self.assertEqual(parse_command("ls"), ("ls", []))

    def test_command_with_args(self) -> None:
        self.assertEqual(
            parse_command("ls -la /home"),
            ("ls", ["-la", "/home"]),
        )

    def test_double_quotes(self) -> None:
        self.assertEqual(
            parse_command('cd "my folder"'),
            ("cd", ["my folder"]),
        )

    def test_single_quotes(self) -> None:
        self.assertEqual(
            parse_command("cd 'another folder'"),
            ("cd", ["another folder"]),
        )

    def test_mixed_quotes(self) -> None:
        self.assertEqual(
            parse_command("ls 'a b' \"c d\""),
            ("ls", ["a b", "c d"]),
        )

    def test_unclosed_quote(self) -> None:
        with self.assertRaises(ValueError):
            parse_command('cd "unclosed')


if __name__ == "__main__":
    unittest.main()