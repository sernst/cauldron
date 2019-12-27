import enum
import typing

from cauldron.plotting import _brewers
from cauldron.plotting import _categoricals
from cauldron.plotting._definitions import ColorPalette


class Palettes(enum.Enum):
    """
    Enumeration of color palettes available for plotting color functions.
    Each enumeration is a ColorPalette data structure that contains a list
    of colors where each entry is a 3-tuple containing RGB channel values
    on a 0-255 scale.
    """

    accent = _brewers.ACCENT
    categorical_10 = _categoricals.CATEGORICAL_10
    categorical_20a = _categoricals.CATEGORICAL_20A
    categorical_20b = _categoricals.CATEGORICAL_20B
    categorical_20c = _categoricals.CATEGORICAL_20C
    colorblind = _categoricals.COLORBLIND
    dark = _brewers.DARK
    paired = _brewers.PAIRED
    pastel_1 = _brewers.PASTEL_1
    pastel_2 = _brewers.PASTEL_2
    plotly_v4 = _categoricals.PLOTLY_V4
    set_1 = _brewers.SET_1
    set_2 = _brewers.SET_2
    set_3 = _brewers.SET_3


def get_gray_color(
        level: int = 128,
        opacity: float = 1.0,
        as_string: bool = True
) -> typing.Union[tuple, str]:
    """
    Generates a grayscale color with the specified level and returns it
    either as a 4-length RGBA tuple or as an "rgba(...)" CSS string.

    :param level:
        The value for each RGB channel as an integer in the range [0, 255].
    :param opacity:
        A floating-point value between 0.0 and 1.0, where 1.0 is fully opaque
        and is the default value.
    :param as_string:
        Whether or not to return the result as a CSS string (the default)
        or as a 4-length RGBA tuple.
    """
    opacity = max(0.0, min(1.0, 1.0 if opacity is None else float(opacity)))

    level = max(0, min(255, level))
    out = (int(level), int(level), int(level), float(opacity))

    if as_string:
        return 'rgba({}, {}, {}, {})'.format(*out)
    return out


def get_color(
        index: int,
        opacity: float = None,
        as_string: bool = True,
        palette: typing.Union[Palettes, ColorPalette] = None,
        adjust_brightness: float = 0.0,
) -> typing.Union[tuple, str]:
    """..."""
    color_palette = getattr(palette, 'value', None)
    colors = getattr(
        color_palette,
        'colors',
        Palettes.categorical_10.value.colors
    )
    out = colors[index % len(colors)]

    opacity = max(0.0, min(1.0, 1.0 if opacity is None else float(opacity)))
    adjust = 1.0 + max(-1.0, min(1.0, adjust_brightness))

    out = tuple([int(adjust * c) for c in out] + [opacity])
    if as_string:
        return 'rgba({}, {}, {}, {})'.format(*out)

    return out
