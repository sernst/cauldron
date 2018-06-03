import typing
import random

PLOT_COLOR_PALETTE = (
    (31, 119, 180),
    (255, 127, 14),
    (44, 160, 44),
    (214, 39, 40),
    (148, 103, 189),
    (140, 86, 75),
    (227, 119, 194),
    (127, 127, 127),
    (188, 189, 34),
    (23, 190, 207)
)


def get_gray_color(
        level: int = 128,
        opacity: float = None,
        as_string: bool = True
) -> typing.Union[tuple, str]:
    """

    :param level:
    :param opacity:
    :param as_string:
    :return:
    """

    if opacity is None:
        opacity = 1

    level = max(0, min(255, level))
    out = (int(level), int(level), int(level), opacity)

    if as_string:
        return 'rgba({}, {}, {}, {})'.format(*out)
    return out


def get_color(
        index: int,
        opacity: float = None,
        as_string: bool = True
) -> typing.Union[tuple, str]:
    """

    :param index:
    :param opacity:
    :param as_string:
    :return:
    """

    out = PLOT_COLOR_PALETTE[index % len(PLOT_COLOR_PALETTE)]

    if opacity is None:
        opacity = 1.0

    out = tuple(list(out) + [opacity])
    if as_string:
        return 'rgba({}, {}, {}, {})'.format(*out)

    return out


def create_layout(
        layout: dict = None,
        title: str = None,
        x_label: str = None,
        y_label: str = None,
        x_bounds: typing.List[float] = None,
        y_bounds: typing.List[float] = None
) -> dict:
    """

    :param layout:
    :param title:
    :param x_label:
    :param y_label:
    :param x_bounds:
    :param y_bounds:
    :return:
    """
    if layout is None:
        layout = dict()

    layout['title'] = title if title else layout.get('title')

    font = {
        'family': 'Courier New, monospace',
        'size': 18,
        'color': '#7f7f7f'
    }

    x = layout.get('xaxis', {})
    x['title'] = x_label if x_label else x.get('title')
    x['titlefont'] = x.get('titlefont', font)
    if x_bounds:
        x['range'] = x_bounds
    layout['xaxis'] = x

    y = layout.get('yaxis', {})
    y['title'] = y_label if y_label else y.get('title')
    y['titlefont'] = y.get('titlefont', font)
    if y_bounds:
        y['range'] = y_bounds
    layout['yaxis'] = y

    return layout


def make_line_data(
        x,
        y,
        y_unc,
        name: str = None,
        color: str = None,
        fill_color: str = None,
        line_properties: typing.Union[dict, int] = 0,
        marker_properties: typing.Union[dict, int] = 6
):
    """

    :param x:
    :param y:
    :param y_unc:
    :param name:
    :param color:
    :param fill_color:
    :param line_properties:
    :param marker_properties:
    :return:
    """

    lower = []
    upper = []

    if not name:
        name = 'Measurement'
        legend_group = '{}_{}'.format(name, random.randint(0, 1e6))
    else:
        legend_group = name

    if not fill_color:
        fill_color = 'rgba(68, 68, 68, 0.1)'

    if not color:
        color = get_color(0, as_string=True)

    for y_value, y_unc_value in zip(y, y_unc):
        lower.append(y_value - y_unc_value)
        upper.append(y_value + y_unc_value)

    lower_trace = dict(
        x=x,
        y=lower,
        line={'width': 0, 'color': color},
        mode='lines',
        name='- {}'.format(name),
        type='scatter',
        showlegend=False,
        legendgroup=legend_group
    )

    mode = ''

    if isinstance(line_properties, dict):
        mode += 'lines'
    elif isinstance(line_properties, int) and line_properties > 0:
        mode += 'lines'
        line_properties = {'width': line_properties}
    else:
        line_properties = {'width': 0}

    if 'color' not in line_properties:
        line_properties['color'] = color

    if isinstance(marker_properties, dict):
        mode += '+markers' if len(mode) > 0 else 'markers'
    elif isinstance(marker_properties, int) and marker_properties > 0:
        mode += '+markers' if len(mode) > 0 else 'markers'
        marker_properties = {'size': marker_properties}
    else:
        marker_properties = {'size': 0}

    if 'color' not in marker_properties:
        marker_properties['color'] = color

    middle_trace = dict(
        x=x,
        y=y,
        fill='tonexty',
        fillcolor=fill_color,
        mode=mode,
        marker=marker_properties,
        line=line_properties,
        name=name,
        type='scatter',
        showlegend=bool(name is not None),
        legendgroup=legend_group
    )

    upper_trace = dict(
        x=x,
        y=upper,
        fill='tonexty',
        fillcolor=fill_color,
        line={'width': 0, 'color': color},
        mode='lines',
        name='+ {}'.format(name),
        type='scatter',
        showlegend=False,
        legendgroup=legend_group
    )

    return {
        'data': [lower_trace, middle_trace, upper_trace],
        'layout': {'hovermode': 'closest'}
    }



