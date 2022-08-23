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

import logging

from enum import Enum
from operator import add, sub, mul, truediv
from collections import deque

from typing import Any, cast, Callable, Union

from calct.duration import Duration
from calct.common import (
    Number,
    OPS_STR,
    OPS_PAREN_STR,
    DIGITS_STR,
    SIGN_STR,
    FLOAT_EXPONENT_STR,
    FLOAT_CHARS_STR,
    WHITESPACE_STR,
    FLOAT_SEPARATOR_EXPONENT_STR,
)


def lex(input_str: str) -> list[str]:
    tokens: list[str] = []
    buffer: list[str] = []

    logging.debug(input_str)

    def add_token():
        if len(buffer) > 0:
            tokens.append("".join(buffer))
            buffer.clear()

    last_char = None

    for char in input_str:

        logging.debug(f"{char=}, {buffer=}, {tokens=}")
        if char in OPS_PAREN_STR:
            if last_char and last_char in FLOAT_EXPONENT_STR:
                if char in SIGN_STR:
                    buffer.append(char)
                else:
                    raise ValueError(
                        f"`{char}` is following `{FLOAT_EXPONENT_STR}` and is not a digit `{DIGITS_STR}` or a sign `{SIGN_STR}`"
                    )

            else:
                add_token()
                tokens.append(char)
        elif char in WHITESPACE_STR:
            add_token()
        elif char in FLOAT_CHARS_STR:
            buffer.append(char)
        elif char in Duration.get_hour_and_minute_seps():
            buffer.append(char)
        else:
            raise ValueError(
                f"`{char}` is not a digit `{DIGITS_STR}`, an operator or parenthesis `{OPS_PAREN_STR}`, a whitespace, a digit separator or exponent `{FLOAT_SEPARATOR_EXPONENT_STR}`, or a time unit or separator `{''.join(Duration.get_hour_and_minute_seps())}`"
            )
        last_char = char

    add_token()

    return tokens


class Associativity(Enum):
    LEFT = 1
    RIGHT = 2


def op_to(val1: Any, val2: Any) -> Any:
    return val2 - val1


class Operation(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    TO = "@"

    @property
    def op(self) -> Callable[[Any, Any], Any]:
        if self is Operation.ADD:
            return add
        elif self is Operation.SUB:
            return sub
        elif self is Operation.MUL:
            return mul
        elif self is Operation.DIV:
            return truediv
        elif self is Operation.TO:
            return op_to
        else:
            return NotImplemented

    @property
    def precedence(self) -> int:
        if self is Operation.ADD:
            return 2
        elif self is Operation.SUB:
            return 2
        elif self is Operation.MUL:
            return 3
        elif self is Operation.DIV:
            return 3
        elif self is Operation.TO:
            return 4
        else:
            return NotImplemented

    @property
    def associativity(self) -> Associativity:
        if self is Operation.ADD:
            return Associativity.LEFT
        elif self is Operation.SUB:
            return Associativity.LEFT
        elif self is Operation.MUL:
            return Associativity.LEFT
        elif self is Operation.DIV:
            return Associativity.LEFT
        elif self is Operation.TO:
            return Associativity.RIGHT
        else:
            return NotImplemented


def parse(tokens: list[str]) -> deque[str]:
    logging.debug(tokens)

    out_queue: deque[str] = deque()
    op_stack: deque[str] = deque()

    for t in tokens:
        if t not in OPS_PAREN_STR:
            out_queue.append(t)
        elif t in OPS_STR:
            while (len(op_stack) > 0 and op_stack[-1] in OPS_STR) and (
                (Operation(op_stack[-1]).precedence > Operation(t).precedence)
                or (
                    (Operation(op_stack[-1]).precedence == Operation(t).precedence)
                    and Operation(t).associativity == Associativity.LEFT
                )
            ):
                out_queue.append(op_stack.pop())
            op_stack.append(t)
        elif t == "(":
            op_stack.append(t)
        elif t == ")":
            if len(op_stack) == 0:
                raise ValueError("Unmatched closing parenthesis")
            while op_stack[-1] != "(":
                out_queue.append(op_stack.pop())
                if len(op_stack) == 0:
                    raise ValueError("Unmatched closing parenthesis")
            op_stack.pop()

    while len(op_stack) > 0:
        if op_stack[-1] == "(":
            raise ValueError("Unmatched opening parenthesis")
        out_queue.append(op_stack.pop())

    return out_queue


def evaluate_rpn(rpn: deque[str]) -> Union[Number, Duration]:
    eval_stack: deque[Union[str, Number, Duration]] = deque()

    for t in rpn:
        logging.debug(f"{t=}")
        if t in OPS_STR:
            logging.debug(f"op1={eval_stack[-1]!r}, op2={eval_stack[-2]!r}")
            op2 = eval_stack.pop()
            op1 = eval_stack.pop()
            eval_stack.append(Operation(t).op(op1, op2))
            logging.debug(f"t is {t}, {eval_stack=}")
        else:
            if (common := (set(t) & Duration.get_hour_and_minute_seps())) != set():
                eval_stack.append(Duration.parse(t))
                logging.debug(
                    f"t is a time because it contains {common}, {eval_stack=}"
                )
            else:
                try:
                    eval_stack.append(int(t))
                except ValueError:
                    try:
                        eval_stack.append(float(t))
                    except ValueError:
                        raise ValueError(f"`{t}` is not a valid number")
                logging.debug(f"t is a number, {eval_stack=}")

    if not isinstance(eval_stack[-1], Union[Duration, Number]):
        raise ValueError("Invalid expression: the result is not a duration or a number")
    return cast(Union[Number, Duration], eval_stack[-1])
