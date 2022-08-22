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

from calct.duration import Duration, timedelta


def test_duration_to_timedelta():
    d = Duration(minutes=2)
    td = d.as_timedelta
    assert td == timedelta(minutes=2)
    assert type(td) == timedelta


def test_duration_from_timedelta():
    td = timedelta(hours=3, minutes=32)
    d = Duration.from_timedelta(td)
    assert d == Duration(hours=3, minutes=32)
    assert type(d) == Duration


def test_duration_get_hours():
    assert Duration(hours=2, minutes=60).hours == 3


def test_duration_set_hours():
    d = Duration()
    assert d.hours == 0
    d.hours = 4
    assert d == Duration(hours=4)
