"""Эмулятор оболочки UNIX-подобной ОС (Вариант 10, Этап 1: REPL)."""

import shlex
import sys

VFS_NAME = "my_vfs"
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


def repl():
    """Запустить цикл чтения-вычисления-вывода до `exit` или EOF."""
    prompt = PROMPT_TEMPLATE.format(vfs=VFS_NAME)
    while True:
        try:
            line = input(prompt)
        except EOFError:
            break
        try:
            cmd, args = parse_command(line)
            if cmd is None:
                continue
            if cmd not in COMMANDS:
                print(f"Error: unknown command '{cmd}'")
                continue
            COMMANDS[cmd](args)
        except ValueError as exc:
            print(f"Error: {exc}")
        except Exception as exc:
            print(f"Execution error: {exc}")


if __name__ == "__main__":
    repl()