# Calct
Easily do calculations on hours and minutes using the command line

## TODO
1. Add more tests
2. Custom parsing of durations without using `strptime` to support more formats
 - `25h` (bigger than 23h)
 - `h61`, `61m` (bigger than 60m)
 - `0.1h`(float format for hours)
3. Cleanup `Duration` class using custom decorators:
 - `@classmethod_property{.setter, .deleter}`
 - `@cached_classmethod_property`
4. Add CI
5. Add CD and PyPI
6. Add Python 3.9 support
