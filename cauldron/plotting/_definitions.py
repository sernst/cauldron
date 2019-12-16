import typing

ColorPalette = typing.NamedTuple('ColorPalette', [
    ('name', str),
    ('colors', typing.Tuple[typing.Tuple[int, ...], ...])
])
