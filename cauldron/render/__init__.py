import textwrap
import random
import json as json_internal
import pandas as pd
from datetime import datetime

from cauldron import templating

try:
    import markdown as md
except Exception:
    md = None

try:
    import plotly as plotly_lib
except ImportError:
    plotly_lib = None


def header(level: int, contents: str) -> str:
    """

    :param level:
    :param text:
    :return:
    """

    return templating.render(
        """
        <h{{ level }}>{{ contents }}</h{{ level }}>
        """,
        level=level,
        contents=contents
    )


def text(value: str) -> str:
    """

    :param value:
    :return:
    """

    lines = str(value).strip().split('\n')

    for index in range(len(lines)):
        l = lines[index].strip()
        if len(l) < 1:
            l = '</p><p class="plaintextbox">'
        lines[index] = l

    return '<p class="plaintextbox">{text}</p>'.format(text=' '.join(lines))


def preformatted_text(source: str) -> str:
    """

    :param source:
    :return:
    """

    return '<pre class="preformatted-textbox">{text}</pre>'.format(
        text=str(textwrap.dedent(source))
    )


def markdown(source: str) -> str:
    """

    :param source:
    :return:
    """

    if md is None:
        raise ImportError(textwrap.dedent(
            """
            Unable to import the markdown package. Please check
            """).strip())

    return templating.render(
        """
        <div class="textbox markdown">{{ text }}</div>
        """,
        text=md.markdown(textwrap.dedent(source))
    )


def json(window_key:str, data) -> str:
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


def plotly(data: dict, layout: dict) -> str:
    """

    :param data:
    :param layout:
    :return:
    """

    if plotly_lib is None:
        raise ImportError('Unable to import Plotly library')

    return plotly_lib.offline.plot(
        {'data': data, 'layout': layout},
        output_type='div',
        include_plotlyjs=False
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
