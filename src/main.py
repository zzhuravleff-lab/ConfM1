"""Эмулятор оболочки UNIX-подобной ОС.

Вариант 10.

Этап 1: REPL (парсер, команды-заглушки, exit).
Этап 2: конфигурация (CLI-параметры, стартовый скрипт).
Этап 3: VFS (загрузка из XML, motd).
Этап 4: основные команды (ls, cd, echo, clear, history).
"""

import argparse
import shlex
import sys
from pathlib import Path
from typing import Optional

from src.shell import Shell
from src.vfs import VfsError, VirtualFileSystem, load_vfs

EXIT_CODE_ERROR = 1


def parse_command(line: str):
    """Разобрать строку на имя команды и список аргументов.

    Args:
        line: Строка ввода пользователя.

    Returns:
        Кортеж (имя_команды, список_аргументов).
        Имя команды равно None, если строка пустая.

    Raises:
        ValueError: Если в строке нарушен баланс кавычек.
    """
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        raise ValueError(f"parsing error: {exc}") from exc
    if not parts:
        return None, []
    return parts[0], parts[1:]


def build_arg_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки.

    Returns:
        Настроенный объект ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="vfs-emulator",
        description="Эмулятор оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs",
        metavar="PATH",
        default=None,
        help="Путь к физическому расположению VFS "
             "(файл .xml или папка с ним).",
    )
    parser.add_argument(
        "--script",
        metavar="PATH",
        default=None,
        help="Путь к стартовому скрипту.",
    )
    return parser


def print_debug(args) -> None:
    """Вывести все заданные параметры эмулятора.

    Args:
        args: Результат разбора argparse.
    """
    print(f"VFS path    = {args.vfs!r}")
    print(f"Script path = {args.script!r}")
    print("\n")


def print_vfs_info(vfs_obj: Optional[VirtualFileSystem]) -> None:
    """Вывести информацию о загруженной VFS.

    Args:
        vfs_obj: Загруженная VFS или None.
    """
    if vfs_obj is None:
        print("VFS: not loaded (empty VFS will be used)")
        return
    entries = vfs_obj.root.list_children()
    print(f"VFS: name={vfs_obj.name}, root entries={entries}")


def print_motd(vfs_obj: Optional[VirtualFileSystem]) -> None:
    """Вывести сообщение motd, если оно есть.

    Args:
        vfs_obj: Загруженная VFS или None.
    """
    if vfs_obj is None:
        return
    motd = vfs_obj.motd
    if motd:
        print(f"motd: {motd.strip()}")


def _find_xml_in_dir(directory: Path) -> Optional[Path]:
    """Найти XML-файл в директории.

    Args:
        directory: Путь к директории.

    Returns:
        Путь к XML-файлу или None.
    """
    preferred = directory / "vfs.xml"
    if preferred.is_file():
        return preferred
    xml_files = sorted(directory.glob("*.xml"))
    if xml_files:
        return xml_files[0]
    return None


def load_vfs_from_path(path: str) -> Optional[VirtualFileSystem]:
    """Загрузить VFS из указанного пути.

    Args:
        path: Путь к файлу или папке VFS.

    Returns:
        Объект VirtualFileSystem или None при ошибке.
    """
    p = Path(path)

    if p.is_dir():
        candidate = _find_xml_in_dir(p)
        if candidate is None:
            print(f"Error: no XML files found in {path}")
            return None
        p = candidate

    if not p.is_file():
        print(f"Error: VFS path not found: {path}")
        return None

    try:
        return load_vfs(str(p))
    except VfsError as exc:
        print(f"Error: {exc}")
        return None


def main() -> None:
    """Точка входа программы."""
    parser = build_arg_parser()
    args = parser.parse_args()

    print_debug(args)

    vfs_obj: Optional[VirtualFileSystem] = None
    if args.vfs:
        vfs_obj = load_vfs_from_path(args.vfs)
        if vfs_obj is None:
            sys.exit(EXIT_CODE_ERROR)

    print_vfs_info(vfs_obj)
    print_motd(vfs_obj)

    shell = Shell(vfs=vfs_obj)
    if args.script:
        shell.run_script(args.script)
    else:
        shell.repl()


if __name__ == "__main__":
    main()