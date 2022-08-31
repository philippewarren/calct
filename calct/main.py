#   calct: Easily do calculations on hours and minutes using the command line
#   Copyright (C) 2022  Philippe Warren
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import argparse
import cmd
import logging
import os
import sys
from dataclasses import dataclass
from typing import cast

import calct
from calct.duration import Duration
from calct.parser import evaluate_rpn, lex, parse


def log_level_from_name(name: str) -> int:
    if name == "DEBUG":
        return logging.DEBUG
    elif name == "INFO":
        return logging.INFO
    elif name == "WARNING":
        return logging.WARNING
    elif name == "ERROR":
        return logging.ERROR
    elif name == "CRITICAL":
        return logging.CRITICAL
    else:
        raise ValueError(f"Invalid log level: {name}")


def get_help_str() -> str:
    return f"""calct v{calct.__version__}:
Easily do calculations on hours and minutes using the command line

Copyright (C) {calct.__year__} {calct.__author__}
Released under the GNU General Public License v3.0
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
To show the full license, run: `calct --license`
In interactive mode, run: `licence`

Supports parentheses to control precedence.
Supports operators + and - between two durations.
Supports operators * and / between a duration and a number.
Supports operator @ to create a time range: (a @ b) is the same as (b - a)

Separate hours and minutes using (:) or (h).
Minutes can also be specified as (m) or decimal hours.

Exemple:
    ::      3h23 @ 5h24 + 2 * (1h - 30m)
        =>  5h24 - 3h23 + 2 * (1h - 30m)
        =>  5h24 - 3h23 + 2 * (30m)
        =>  5h24 - 3h23 + 60m
        =>  2h01 + 60m
        =>  3h01
"""


def get_licence_str() -> str:
    raise NotImplementedError()


def run_once(time_expr_list: list[str]) -> None:

    arg_string = " ".join(time_expr_list)

    try:
        tokens = lex(arg_string)
    except ValueError as e:
        logging.error(e)
        return

    try:
        rpn = parse(tokens)
    except ValueError as e:
        logging.error(e)
        return
    except TypeError as e:
        print("TypeError IN PARSING")
        logging.error(e)
        return

    try:
        val = evaluate_rpn(rpn)
    except ValueError as e:
        print("ValueError IN RPN EVALUATION")
        logging.error(e)
        return
    except TypeError as e:
        print("TypeError IN RPN EVALUATION")
        logging.error(e)
        return

    print(val)


class repl(cmd.Cmd):
    intro = f"calct v{calct.__version__}: Easily do calculations on hours and minutes using the command line\nType `help` or `?` to show help.\n"
    prompt = "(calct) > "

    def default(self, line: str) -> None:
        run_once([line])

    def emptyline(self) -> bool:
        return False

    def do_shell(self, arg: str):
        """Run a shell command, also usable using the ! prefix"""
        os.system(arg)

    def do_clear(self, _):
        """Clear the terminal"""
        os.system("cls") if os.name == "nt" else os.system("clear")

    def do_exit(self, _):
        """Exit the program"""
        sys.exit()

    def do_help(self, arg: str) -> None:
        """Show this help message"""
        if len(arg) == 0:
            print(get_help_str())
        super().do_help(arg)

    def do_licence(self, _) -> None:
        """Show the full license"""
        print(get_licence_str())

    def do_sep(self, arg: str) -> None:
        """Show or set the separator for hours and minutes used in display, and usable in parsing"""
        if len(arg) == 0:
            sep = Duration.get_string_hour_minute_separator()
            print(f"`{sep}` => {Duration(hours=22, minutes=22)}")
        else:
            try:
                Duration.set_string_hour_minute_separator(arg)
            except TypeError as e:
                logging.error(e)
            except ValueError as e:
                logging.error(e)


def run_loop():
    try:
        repl().cmdloop()
    except KeyboardInterrupt:
        print("^C")
        sys.exit()


@dataclass
class Args(argparse.Namespace):
    log_level: str = "WARNING"
    interactive: bool = False
    help: bool = False
    licence: bool = False
    separator: str = "h"


def main():

    FORMAT = "%(levelname)s: %(message)s"
    logging.basicConfig(format=FORMAT)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        help="Set the log level",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode",
        default=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        help="Show this help message and exit",
        default=False,
    )
    parser.add_argument(
        "--license",
        action="store_true",
        help="Show the license and exit",
        default=False,
    )
    parser.add_argument(
        "-s",
        "--separator",
        help="Set the separator for hours and minutes used in display, and usable in parsing",
        default="h",
    )
    args, remaining_args = parser.parse_known_args(namespace=Args())
    args = cast(Args, args)

    logging.getLogger().setLevel(log_level_from_name(args.log_level))

    logging.debug(f"{args = }")
    logging.debug(f"{remaining_args = }")

    if args.separator is not parser.get_default("separator"):
        try:
            Duration.set_string_hour_minute_separator(args.separator)
        except ValueError as e:
            logging.error(e)

    if args.help:
        print(get_help_str())
        parser.print_help()
        sys.exit()
    elif args.licence:
        print(get_licence_str())
        sys.exit()
    elif args.interactive:
        run_loop()
    elif len(remaining_args) > 0:
        run_once(remaining_args)
    else:
        logging.error("No time expression in command arguments")
        sys.exit(-1)


if __name__ == "__main__":
    main()
