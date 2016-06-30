import json as json_internal
import os
import random
from datetime import datetime

import pandas as pd

from cauldron import environ
from cauldron import templating
from cauldron.render import inspection
from cauldron.render import syntax_highlighting
from cauldron.render import utils as render_utils

try:
    import plotly as plotly_lib
except ImportError:
    plotly_lib = None



def listing(source: list, ordered: bool = False) -> str:
    """

    :param source:
    :param ordered:
    :return:
    """

    return templating.render_template(
        'listing.html',
        type='ol' if ordered else 'ul',
        items=['{}'.format(x) for x in source]
    )


def inspect(source: dict) -> str:
    """

    :param source:
    :return:
    """

    out = inspection.inspect_data(source=source)
    return inspection.render_tree(out)


def code_file(
        path: str,
        language: str = None,
        mime_type: str = None
) -> str:
    """

    :param path:
    :param language:
    :param mime_type:
    :return:
    """

    path = environ.paths.clean(path)

    if not os.path.exists(path):
        return 'File does not exist: {}'.format(path)

    with open(path, 'r+') as f:
        source = f.read()

    return code(
        source=source,
        language=language,
        filename=path,
        mime_type=mime_type
    )


def code(
        source: str,
        language: str = None,
        filename: str = None,
        mime_type: str = None
) -> str:
    """

    :param source:
    :param language:
    :param filename:
    :param mime_type:
    :return:
    """

    if not source:
        return ''

    return syntax_highlighting.as_html(
        source=source,
        language=language,
        filename=filename,
        mime_type=mime_type
    )


def header(contents: str, level: int = 1) -> str:
    """

    :param level:
    :param contents:
    :return:
    """

    return templating.render(
        """
        <h{{ level }}>{{ contents }}</h{{ level }}>
        """,
        level=level,
        contents=contents
    )


def json(window_key: str, data) -> str:
    """

    :param window_key:
    :param data:
    :return:
    """

    return templating.render(
        """
        <script>
            window.{{ key }} = {{ data }};
        </script>
        """,
        key=window_key,
        data=json_internal.dumps(data)
    )


def html(content) -> str:
    """

    :param content:
    :return:
    """

    return templating.render(
        '<div class="box">{{content}}</div>',
        content=content
    )


def plotly(data: dict, layout: dict, scale: float = 0.5) -> str:
    """

    :param data:
    :param layout:
    :param scale:
    :return:
    """

    if plotly_lib is None:
        raise ImportError('Unable to import Plotly library')

    dom = plotly_lib.offline.plot(
        {'data': data, 'layout': layout},
        output_type='div',
        include_plotlyjs=False
    )

    return '<div class="cd-plotly-box" style="min-height:{}vh">{}</div>'.format(
        round(100.0 * scale), dom
    )


def table(data_frame: pd.DataFrame, scale: float = 0.7) -> str:
    """

    :param data_frame:
    :param scale:
    :return:
    """

    table_id = 'table-{}-{}'.format(
        datetime.utcnow().strftime('%H-%M-%S-%f'),
        random.randint(0, 1e8)
    )

    column_headers = data_frame.columns.tolist()
    column_headers = ['"{}"'.format(x) for x in column_headers]

    data = []

    for index, row in data_frame.iterrows():
        data.append(row.tolist())

    return templating.render_template(
        'table.html.template',
        id=table_id,
        scale=min(0.95, max(0.05, scale)),
        data=json_internal.dumps(data),
        column_headers=', '.join(column_headers)
    )


def whitespace(lines: float = 1.0) -> str:
    """

    :param lines:
    :return:
    """

    pixels = round(12 * lines)
    return '<div style="height:{}px"> </div>'.format(pixels)


def jinja(path: str, **kwargs) -> str:
    """

    :param path:
    :param kwargs:
    :return:
    """

    return templating.render_file(path, **kwargs)


def svg(svg_data: str) -> str:
    """

    :param svg_data:
    :return:
    """

    return templating.render(
        '<div class="svg-box">{{ svg }}</div>',
        svg=svg
    )


def status(
        data: dict,
        values: bool = True,
        types: bool = True
) -> str:
    """

    :param data:
    :param values:
    :param types:
    :return:
    """

    out = []
    keys = list(data.keys())
    keys.sort()

    for key in keys:
        value = data[key]
        value_type = None
        try:
            value_type = value.__class__.__name__
        except Exception:
            pass

        try:
            if value_type is None:
                value_type = value.__name__
        except Exception:
            pass

        try:
            value_type = type(value).__name__
        except Exception:
            pass

        if hasattr(value, 'head'):
            try:
                value = value.head(5)
            except Exception:
                pass
        elif isinstance(value, dict):
            temp_value = []
            for k, v in value.items():
                temp_value.append('{}: {}'.format(k, v))
            value = '\n'.join(temp_value)
        elif isinstance(value, (list, tuple)):
            value = '\n'.join(['{}'.format(v) for v in value])

        value = '<pre>{}</pre>'.format(
            render_utils.html_escape('{}'.format(value))[:600]
        )

        out.append(templating.render_template(
            'status-variable.template.html',
            name=key,
            type=value_type,
            value=value
        ))

    return ''.join(out)
