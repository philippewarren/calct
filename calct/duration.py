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

from datetime import timedelta
from time import strptime
from functools import total_ordering
from itertools import chain

from calct.common import (
    Number,
    CANT_BE_CUSTOM_SEPARATOR,
    DEFAULT_HOUR_SEPARATOR,
    DEFAULT_MINUTE_SEPARATOR,
)


@total_ordering
class Duration:
    str_hour_sep: str = DEFAULT_HOUR_SEPARATOR[0]
    str_minute_sep = DEFAULT_MINUTE_SEPARATOR[0]

    @classmethod
    def get_string_hour_minute_separator(cls) -> str:
        return cls.str_hour_sep

    @classmethod
    def set_string_hour_minute_separator(cls, sep: str) -> None:
        if not isinstance(sep, str) or not len(sep) == 1:  # type:ignore
            raise TypeError("Separator needs to be a one-character string")
        if set(sep) & set(CANT_BE_CUSTOM_SEPARATOR + DEFAULT_MINUTE_SEPARATOR) != set():
            raise ValueError(
                f"Separator can't contain a character from `{''.join(set(CANT_BE_CUSTOM_SEPARATOR + DEFAULT_MINUTE_SEPARATOR))}` or it would break the parser"
            )
        cls.str_hour_sep = sep

    @classmethod
    def del_string_hour_minute_separator(cls) -> None:
        cls.str_hour_sep = DEFAULT_HOUR_SEPARATOR[0]

    def __init__(self, hours: Number = 0, minutes: Number = 0) -> None:
        self.minutes = hours * 60 + minutes

    @property
    def hours(self) -> Number:
        return divmod(self.minutes, 60)[0]

    @hours.setter
    def hours(self, new_hours: Number) -> None:
        self.minutes = new_hours * 60

    @staticmethod
    def from_timedelta(td: timedelta) -> Duration:
        return Duration(minutes=td.total_seconds() / 60)

    @classmethod
    def get_hour_seps(cls) -> set[str]:
        return set(DEFAULT_HOUR_SEPARATOR) | {cls.str_hour_sep}

    @classmethod
    def get_minute_seps(cls) -> set[str]:
        return set(DEFAULT_MINUTE_SEPARATOR) | {cls.str_minute_sep}

    @classmethod
    def get_hour_and_minute_seps(cls) -> set[str]:
        return cls.get_hour_seps() | cls.get_minute_seps()

    @classmethod
    def get_matchers(cls) -> set[str]:
        matchers_hours = chain.from_iterable(
            (f"%H{sep}%M", f"%H{sep}", f"{sep}%M") for sep in cls.get_hour_seps()
        )
        matchers_minutes = chain.from_iterable(
            (f"%M{sep}",) for sep in cls.get_minute_seps()
        )

        return set(matchers_hours) | set(matchers_minutes)

    @classmethod
    def parse(cls, time_str: str) -> Duration:
        for matcher in cls.get_matchers():
            try:
                t = strptime(time_str, matcher)
                return Duration(hours=t.tm_hour, minutes=t.tm_min)
            except ValueError:
                pass
        raise ValueError(f"Invalid time: {time_str}")

    @property
    def hours_minutes(self) -> tuple[float, float]:
        return divmod(self.minutes, 60)

    def __str__(self) -> str:
        hours, minutes = self.hours_minutes
        return f"{hours:.0f}{self.str_hour_sep}{minutes:02.0f}"

    def __repr__(self) -> str:
        hours, minutes = self.hours_minutes
        return f"Duration(hours={hours}, minutes={minutes})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Duration):  # type: ignore
            raise TypeError(
                f"unsupported operand type(s) for ==: '{type(self)}' and '{type(other)}'"
            )
        return self.minutes == other.minutes

    def __lt__(self, other: Duration) -> bool:
        if not isinstance(other, Duration):  # type: ignore
            raise TypeError(
                f"unsupported operand type(s) for <: '{type(self)}' and '{type(other)}'"
            )
        return self.minutes < other.minutes

    def __add__(self, other: Duration) -> Duration:
        if not isinstance(other, Duration):  # type: ignore
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'"
            )
        return Duration(minutes=self.minutes + other.minutes)

    def __sub__(self, other: Duration) -> Duration:
        if not isinstance(other, Duration):  # type: ignore
            raise TypeError(
                f"unsupported operand type(s) for -: '{type(self)}' and '{type(other)}'"
            )
        return Duration(minutes=self.minutes - other.minutes)

    def __mul__(self, other: Number) -> Duration:
        if not isinstance(other, (int, float)):  # type: ignore
            raise TypeError(
                f"unsupported operand type(s) for *: '{type(self)}' and '{type(other)}'"
            )
        return Duration(minutes=self.minutes * other)

    def __rmul__(self, other: Number) -> Duration:
        return self.__mul__(other)

    def __truediv__(self, other: Number) -> Duration:
        if not isinstance(other, (int, float)):  # type: ignore
            raise TypeError(
                f"unsupported operand type(s) for /: '{type(self)}' and '{type(other)}'"
            )
        return Duration(minutes=self.minutes / other)

    @property
    def as_timedelta(self) -> timedelta:
        return timedelta(minutes=self.minutes)
