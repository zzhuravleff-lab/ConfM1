"""Оболочка эмулятора: контекст, команды, REPL.

Этап 4. Основные команды: ls, cd, echo, clear, history.
"""

from __future__ import annotations

import os
import sys
from typing import List, Optional

from src.vfs import VirtualFileSystem, VfsNode, empty_vfs

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
        ...
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
            result = handler(args)
        except SystemExit:
            raise
        except Exception as exc:
            print(f"Execution error: {exc}")
            return False

        if result is False:
            return False
        return True

    def _get_handler(self, cmd: str):
        """Вернуть метод-обработчик по имени команды."""
        return getattr(self, f"cmd_{cmd}", None)

    def cmd_ls(self, args: List[str]) -> bool:
        """Реализация команды ls.

        Args:
            args: Список аргументов.

        Returns:
            True при успехе, False при ошибке.
        """
        if len(args) > 1:
            print("ls: too many arguments")
            return False

        target = args[0] if args else self.cwd
        node = self.vfs.resolve_path(self.cwd, target)
        if node is None:
            print(f"ls: cannot access '{target}': "
                  f"No such file or directory")
            return False

        if not node.is_dir:
            print(node.name)
            return True

        names = node.list_children()
        print(" ".join(names))
        return True

    def cmd_cd(self, args: List[str]) -> bool:
        """Реализация команды cd.

        Args:
            args: Список аргументов.

        Returns:
            True при успехе, False при ошибке.
        """
        if len(args) > 1:
            print("cd: too many arguments")
            return False

        target = args[0] if args else "/"
        node = self.vfs.resolve_path(self.cwd, target)
        if node is None:
            print(f"cd: no such directory: {target}")
            return False
        if not node.is_dir:
            print(f"cd: not a directory: {target}")
            return False

        self.cwd = self._normalize_cwd(target)
        return True

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

    def cmd_touch(self, args: List[str]) -> bool:
        """Создать пустой файл.

        Если файл уже существует — ничего не делает.
        Если путь ведёт в существующую директорию —
        ошибка.

        Args:
            args: Список аргументов.

        Returns:
            True при успехе, False при ошибке.
        """
        if not args:
            print("touch: missing file operand")
            return False
        if len(args) > 1:
            print("touch: too many arguments")
            return False

        target = args[0]
        parent, name = self._split_path(target)
        if parent is None:
            print(f"touch: cannot touch '{target}': Invalid path")
            return False

        parent_node = self.vfs.resolve_path(self.cwd, parent)
        if parent_node is None:
            print(f"touch: cannot touch '{target}': "
                  f"No such file or directory")
            return False
        if not parent_node.is_dir:
            print(f"touch: cannot touch '{target}': "
                  f"Not a directory")
            return False

        existing = parent_node.get_child(name)
        if existing is not None:
            if existing.is_dir:
                print(f"touch: cannot touch '{target}': "
                      f"Is a directory")
                return False
            return True

        parent_node.children[name] = VfsNode(
            name=name, is_dir=False, content=""
        )
        return True

    def cmd_rmdir(self, args: List[str]) -> bool:
        """Удалить пустую директорию.

        Args:
            args: Список аргументов.

        Returns:
            True при успехе, False при ошибке.
        """
        if not args:
            print("rmdir: missing operand")
            return False
        if len(args) > 1:
            print("rmdir: too many arguments")
            return False

        target = args[0]
        parent, name = self._split_path(target)
        if parent is None or not name:
            print(f"rmdir: failed to remove '{target}': "
                  f"Cannot remove root")
            return False

        parent_node = self.vfs.resolve_path(self.cwd, parent)
        if parent_node is None or not parent_node.is_dir:
            print(f"rmdir: failed to remove '{target}': "
                  f"No such file or directory")
            return False

        node = parent_node.get_child(name)
        if node is None:
            print(f"rmdir: failed to remove '{target}': "
                  f"No such file or directory")
            return False
        if not node.is_dir:
            print(f"rmdir: failed to remove '{target}': "
                  f"Not a directory")
            return False
        if node.children:
            print(f"rmdir: failed to remove '{target}': "
                  f"Directory not empty")
            return False

        del parent_node.children[name]
        return True

    def _split_path(self, path: str) -> tuple:
        """Разделить путь на родителя и последний компонент.

        Args:
            path: Путь.

        Returns:
            Кортеж (родительский_путь, имя) или (None, None),
            если путь пустой или невалидный.
        """
        if not path:
            return None, None

        if path.startswith("/"):
            parts = [p for p in path.split("/") if p]
            if not parts:
                return None, None
            normalized: List[str] = []
        else:
            base = [p for p in self.cwd.split("/") if p]
            parts = base + [p for p in path.split("/") if p]
            normalized = base

        resolved: List[str] = []
        for part in parts:
            if part == ".":
                continue
            if part == "..":
                if resolved:
                    resolved.pop()
                continue
            resolved.append(part)

        if not resolved:
            return None, None

        name = resolved[-1]
        parent_parts = resolved[:-1]
        parent = "/" + "/".join(parent_parts) if parent_parts else "/"
        return parent, name

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