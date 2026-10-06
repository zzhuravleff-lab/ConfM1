"""Оболочка эмулятора: контекст, команды, REPL.

Этап 4. Основные команды: ls, cd, echo, clear, history.
"""

from __future__ import annotations

import os
import sys
from typing import List, Optional

from src.vfs import VirtualFileSystem, empty_vfs

EXIT_CODE_OK = 0
PROMPT_TEMPLATE = "{vfs}$ "
HISTORY_WIDTH = 4


class Shell:
    """Контекст эмулятора и реализация команд.

    Attributes:
        vfs: Виртуальная файловая система (может быть пустой).
        vfs_name: Имя VFS для приглашения.
        cwd: Текущая директория (абсолютный путь).
        history: Список выполненных команд.
        in_script: True, если выполняется стартовый скрипт.
    """

    def __init__(
        self,
        vfs: Optional[VirtualFileSystem] = None,
        vfs_name: str = "my_vfs",
    ) -> None:
        """Создать оболочку.

        Args:
            vfs: VFS или None (тогда создаётся пустая).
            vfs_name: Имя VFS.
        """
        self.vfs = vfs if vfs is not None else empty_vfs(vfs_name)
        self.vfs_name = vfs_name
        self.cwd = "/"
        self.history: List[str] = []
        self.in_script = False

    @property
    def prompt(self) -> str:
        """Приглашение к вводу."""
        return PROMPT_TEMPLATE.format(vfs=self.vfs_name)

    def execute(self, line: str, echo: bool = False) -> bool:
        """Выполнить одну строку.

        Args:
            line: Строка ввода.
            echo: Печатать ли строку с приглашением.

        Returns:
            True при успехе, False при ошибке.
        """
        if echo:
            print(f"{self.prompt}{line}")

        from src.main import parse_command

        try:
            cmd, args = parse_command(line)
        except ValueError as exc:
            print(f"Error: {exc}")
            return False

        if cmd is None:
            return True

        handler = self._get_handler(cmd)
        if handler is None:
            print(f"Error: unknown command '{cmd}'")
            return False

        self.history.append(line)

        try:
            handler(args)
        except SystemExit:
            raise
        except Exception as exc:
            print(f"Execution error: {exc}")
            return False

        return True

    def _get_handler(self, cmd: str):
        """Вернуть метод-обработчик по имени команды."""
        return getattr(self, f"cmd_{cmd}", None)

    def cmd_ls(self, args: List[str]) -> None:
        """Реализация команды ls.

        Args:
            args: Список аргументов.
        """
        if len(args) > 1:
            print("ls: too many arguments")
            return

        target = args[0] if args else self.cwd
        node = self.vfs.resolve_path(self.cwd, target)
        if node is None:
            print(f"ls: cannot access '{target}': "
                  f"No such file or directory")
            return

        if not node.is_dir:
            print(node.name)
            return

        names = node.list_children()
        print(" ".join(names))

    def cmd_cd(self, args: List[str]) -> None:
        """Реализация команды cd.

        Args:
            args: Список аргументов.
        """
        if len(args) > 1:
            print("cd: too many arguments")
            return

        target = args[0] if args else "/"
        node = self.vfs.resolve_path(self.cwd, target)
        if node is None:
            print(f"cd: no such directory: {target}")
            return
        if not node.is_dir:
            print(f"cd: not a directory: {target}")
            return

        self.cwd = self._normalize_cwd(target)

    def _normalize_cwd(self, target: str) -> str:
        """Нормализовать путь для сохранения в cwd."""
        if target.startswith("/"):
            parts = [p for p in target.split("/") if p]
        else:
            base = [p for p in self.cwd.split("/") if p]
            parts = base + [p for p in target.split("/") if p]

        normalized: List[str] = []
        for part in parts:
            if part == ".":
                continue
            if part == "..":
                if normalized:
                    normalized.pop()
                continue
            normalized.append(part)

        return "/" + "/".join(normalized)

    def cmd_echo(self, args: List[str]) -> None:
        """Реализация команды echo.

        Args:
            args: Список аргументов.
        """
        print(" ".join(args))

    def cmd_clear(self, args: List[str]) -> None:
        """Реализация команды clear.

        В стартовом скрипте ничего не делает.

        Args:
            args: Список аргументов.
        """
        if self.in_script:
            return
        os.system("cls" if os.name == "nt" else "clear")

    def cmd_history(self, args: List[str]) -> None:
        """Реализация команды history.

        Args:
            args: Список аргументов.
        """
        if args:
            print("history: too many arguments")
            return
        for i, cmd in enumerate(self.history, start=1):
            print(f"{i:>{HISTORY_WIDTH}}  {cmd}")

    def cmd_exit(self, args: List[str]) -> None:
        """Реализация команды exit.

        Args:
            args: Список аргументов.

        Raises:
            ValueError: Если переданы аргументы.
            SystemExit: Всегда для выхода из REPL.
        """
        if args:
            raise ValueError("exit: command takes no arguments")
        print("Bye.")
        sys.exit(EXIT_CODE_OK)

    def repl(self) -> None:
        """Запустить цикл чтения-вычисления-вывода."""
        while True:
            try:
                line = input(self.prompt)
            except EOFError:
                print()
                break
            self.execute(line)

    def run_script(self, path: str) -> None:
        """Выполнить стартовый скрипт.

        Args:
            path: Путь к файлу скрипта.
        """
        try:
            with open(path, "r", encoding="utf-8") as handle:
                lines = handle.readlines()
        except FileNotFoundError:
            print(f"Error: script file not found: {path}")
            return
        except OSError as exc:
            print(f"Error: cannot read script: {exc}")
            return

        self.in_script = True
        try:
            self._run_lines(lines)
        finally:
            self.in_script = False

    def _run_lines(self, lines: List[str]) -> None:
        """Выполнить строки скрипта с остановкой при ошибке."""
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            ok = self.execute(line, echo=True)
            if not ok:
                print(f"Script stopped at: {line}")
                return