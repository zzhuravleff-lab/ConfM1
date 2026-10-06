"""Эмулятор оболочки UNIX-подобной ОС.

Вариант 10.

Этап 1: REPL (парсер, команды-заглушки, exit).
Этап 2: конфигурация (CLI-параметры, стартовый скрипт).
"""

import argparse
import shlex
import sys

VFS_NAME_DEFAULT = "my_vfs"
EXIT_CODE_OK = 0
PROMPT_TEMPLATE = "{vfs}$ "

def parse_command(line: str):
    """Разобрать строку на имя команды и список аргументов.

    Аргументы в кавычках воспринимаются как один токен.

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

def cmd_ls(args):
    """Заглушка команды `ls`.

    Args:
        args: Список аргументов команды.
    """
    print(f"ls: arguments = {args}")


def cmd_cd(args):
    """Заглушка команды `cd`.

    Args:
        args: Список аргументов команды.
    """
    print(f"cd: arguments = {args}")


def cmd_exit(args):
    """Завершить работу эмулятора.

    Args:
        args: Список аргументов. Команда не принимает аргументов.

    Raises:
        ValueError: Если переданы аргументы.
        SystemExit: Всегда, чтобы выйти из REPL.
    """
    if args:
        raise ValueError("exit: command takes no arguments")
    print("Bye.")
    sys.exit(EXIT_CODE_OK)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}

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
        help="Путь к физическому расположению VFS.",
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
    print("=== Debug: emulator parameters ===")
    print(f"  vfs path    = {args.vfs!r}")
    print(f"  script path = {args.script!r}")
    print("===================================")

def execute_line(line: str, vfs_name: str, echo: bool = False) -> bool:
    """Выполнить одну строку ввода.

    Args:
        line: Строка ввода.
        vfs_name: Имя VFS для эха.
        echo: Если True, печатать строку перед выполнением
            (используется в стартовом скрипте).

    Returns:
        True, если команда выполнена успешно,
        False, если произошла ошибка.
    """
    if echo:
        print(f"{PROMPT_TEMPLATE.format(vfs=vfs_name)}{line}")

    try:
        cmd, cmd_args = parse_command(line)
    except ValueError as exc:
        print(f"Error: {exc}")
        return False

    if cmd is None:
        return True

    if cmd not in COMMANDS:
        print(f"Error: unknown command '{cmd}'")
        return False

    try:
        COMMANDS[cmd](cmd_args)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"Execution error: {exc}")
        return False

    return True

def run_script(path: str, vfs_name: str) -> None:
    """Выполнить стартовый скрипт эмулятора.

    Скрипт — это текстовый файл, в каждой строке — команда.
    Пустые строки игнорируются. При первой ошибке
    выполнение останавливается.

    Args:
        path: Путь к файлу скрипта.
        vfs_name: Имя VFS для эха.

    Raises:
        SystemExit: Если команда exit была выполнена.
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

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        ok = execute_line(line, vfs_name, echo=True)
        if not ok:
            print(f"Script stopped at: {line}")
            return

def repl(vfs_name: str = VFS_NAME_DEFAULT) -> None:
    """Запустить цикл чтения-вычисления-вывода.

    Args:
        vfs_name: Имя VFS для приглашения.
    """
    prompt = PROMPT_TEMPLATE.format(vfs=vfs_name)
    while True:
        try:
            line = input(prompt)
        except EOFError:
            print()
            break
        execute_line(line, vfs_name)

def main() -> None:
    """Точка входа программы."""
    parser = build_arg_parser()
    args = parser.parse_args()

    print_debug(args)

    if args.script:
        run_script(args.script, VFS_NAME_DEFAULT)
    else:
        repl(VFS_NAME_DEFAULT)


if __name__ == "__main__":
    main()