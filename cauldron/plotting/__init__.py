import typing

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
        y_label: str = None
) -> dict:
    """

    :param layout:
    :param title:
    :param x_label:
    :param y_label:
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
    x['title'] = x_label if x_label else x['title']
    x['titlefont'] = x.get('titlefont', font)
    layout['xaxis'] = x

    y = layout.get('yaxis', {})
    y['title'] = y_label if y_label else y['title']
    y['titlefont'] = y.get('titlefont', font)
    layout['yaxis'] = y

    return layout


def make_line_data(
        x: list,
        y: list,
        y_unc: list,
        name: str = None,
        color: str = None,
        fill_color: str = None
):
    """

    :param x:
    :param y:
    :param y_unc:
    :param name:
    :param color:
    :param fill_color:
    :return:
    """

    lower = []
    upper = []

    if not name:
        name = 'Measurement'

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
        showlegend=False
    )

    middle_trace = dict(
        x=x,
        y=y,
        fill='tonexty',
        fillcolor=fill_color,
        mode='markers',
        marker={'color': color},
        name=name,
        type='scatter',
        showlegend=bool(name is not None)
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
        showlegend=False
    )

    return {
        'data': [lower_trace, middle_trace, upper_trace],
        'layout': {}
    }



