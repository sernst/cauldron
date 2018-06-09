import json as json_internal
import math
import re
import os
import random
import textwrap
from datetime import datetime
from datetime import timedelta

from cauldron import environ
from cauldron import templating
from cauldron.render import encoding
from cauldron.render import inspection
from cauldron.render import syntax_highlighting
from cauldron.render import utils as render_utils


def elapsed_time(seconds: float) -> str:
    """Displays the elapsed time since the current step started running."""
    environ.abort_thread()
    parts = (
        '{}'.format(timedelta(seconds=seconds))
        .rsplit('.', 1)
    )
    hours, minutes, seconds = parts[0].split(':')
    return templating.render_template(
        'elapsed_time.html',
        hours=hours.zfill(2),
        minutes=minutes.zfill(2),
        seconds=seconds.zfill(2),
        microseconds=parts[-1] if len(parts) > 1 else ''
    )


def list_grid(
        source: list,
        expand_full: bool = False,
        column_count: int = 2,
        row_spacing: float = 1
):
    """

    :param source:
    :param expand_full:
    :param column_count:
    :param row_spacing:
    :return:
    """
    environ.abort_thread()
    max_width = 1400 if expand_full else 900
    column_width = '{}px'.format(
        max(50, int(math.floor(max_width / column_count)))
    )

    return templating.render_template(
        'list_grid.html',
        items=['{}'.format(x) for x in source],
        css_modifier='full' if expand_full else 'limited',
        column_width=column_width,
        row_spacing=row_spacing
    )


def listing(
        source: list,
        ordered: bool = False,
        expand_full: bool = False
) -> str:
    """

    :param source:
    :param ordered:
    :param expand_full:
    :return:
    """
    environ.abort_thread()

    return templating.render_template(
        'listing.html',
        type='ol' if ordered else 'ul',
        items=['{}'.format(x) for x in source],
        css_modifier='full' if expand_full else 'limited'
    )


def inspect(source: dict) -> str:
    """

    :param source:
    :return:
    """
    environ.abort_thread()

    out = inspection.inspect_data(source=source)
    return inspection.render_tree(out)


def code_file(
        path: str,
        language: str = None,
        mime_type: str = None,
        is_code_block: bool = False
) -> str:
    """

    :param path:
    :param language:
    :param mime_type:
    :param is_code_block:
    :return:
    """
    environ.abort_thread()

    path = environ.paths.clean(path)

    if not os.path.exists(path):
        return 'File does not exist: {}'.format(path)

    source = None
    for encoding in ['utf-8', 'mac_roman', 'cp1250']:
        try:
            with open(path, 'r', encoding=encoding) as f:
                source = f.read()
            break
        except Exception:
            pass

    if source is None:
        return ''

    return code(
        source=source,
        language=language,
        filename=path,
        mime_type=mime_type,
        is_code_block=is_code_block
    )


def code(
        source: str,
        language: str = None,
        filename: str = None,
        mime_type: str = None,
        is_code_block: bool = False
) -> str:
    """

    :param source:
    :param language:
    :param filename:
    :param mime_type:
    :param is_code_block:
    :return:
    """
    environ.abort_thread()

    if not source:
        return ''

    cleaned = textwrap.dedent(source.strip('\n'))

    return syntax_highlighting.as_html(
        source=cleaned,
        language=language,
        filename=filename,
        mime_type=mime_type,
        is_code_block=is_code_block
    )


def code_block(
        block: str = None,
        path: str = None,
        language: str = None,
        title: str = None,
        caption: str = None
) -> str:
    """

    :param block:
    :param path:
    :param language:
    :param title:
    :param caption:
    :return:
    """
    environ.abort_thread()

    code_dom = (
        code_file(path, language=language, is_code_block=True)
        if path else
        code(block, language=language, is_code_block=True)
    )

    return templating.render_template(
        'code-block.html',
        code=code_dom,
        title=title,
        caption=caption
    )


def header(contents: str, level: int = 1, expand_full: bool = False) -> str:
    """

    :param level:
    :param contents:
    :param expand_full:
    :return:
    """
    environ.abort_thread()

    classes = [
        'cd-Header',
        'cd-Header--{}'.format('full' if expand_full else 'limited')
    ]

    return templating.render(
        """
        <h{{ level }} class="{{ classes }}">{{ contents }}</h{{ level }}>
        """,
        level=level,
        contents=contents,
        classes=' '.join(classes)
    )


def json(**kwargs) -> str:
    """

    :param kwargs:
    :return:
    """
    environ.abort_thread()

    return templating.render_template(
        'json_include.html',
        data=json_internal.dumps(kwargs, cls=encoding.ComplexJsonEncoder)
    )


def html(content) -> str:
    """

    :param content:
    :return:
    """
    environ.abort_thread()

    return templating.render(
        '<div class="box">{{content}}</div>',
        content=content
    )


def plotly(
        data: list = None,
        layout: dict = None,
        scale: float = 0.5,
        figure: dict = None,
        static: bool = False
) -> str:
    """

    :param data:
    :param layout:
    :param scale:
    :param figure:
    :param static:
    :return:
    """
    environ.abort_thread()

    try:
        import plotly as plotly_lib
    except ImportError:
        plotly_lib = None

    if plotly_lib is None:
        return templating.render_template(
            template_name='import-error.html',
            library_name='Plotly'
        )

    source = figure if figure else {'data': data, 'layout': layout}

    dom = plotly_lib.offline.plot(
        figure_or_data=source,
        output_type='div',
        include_plotlyjs=False
    )

    found = re.search(r'id="(?P<id>[^"]+)"', dom)
    dom_id = found.group('id')

    insert_index = dom.index('"showLink":')
    dom = ''.join([
        dom[:insert_index],
        '"staticPlot": {}, '.format('true' if static else 'false'),
        dom[insert_index:]
    ])

    return templating.render_template(
        'plotly-component.html',
        dom=dom,
        scale=scale,
        min_height=round(100.0 * scale),
        id=dom_id
    )


def table(
        data_frame,
        scale: float = 0.7,
        include_index: bool = False,
        max_rows: int = 500
) -> str:
    """

    :param data_frame:
    :param scale:
    :param include_index:
    :param max_rows:
    :return:
    """
    environ.abort_thread()

    table_id = 'table-{}-{}'.format(
        datetime.utcnow().strftime('%H-%M-%S-%f'),
        random.randint(0, 1e8)
    )

    df_source = (
        data_frame.head(max_rows)
        if len(data_frame) > max_rows else
        data_frame
    )

    if include_index:
        df_source = df_source.reset_index()

    try:
        column_headers = ['"{}"'.format(x) for x in df_source.columns.tolist()]
        data = df_source.values.tolist()
    except AttributeError:
        # If no columns are found assume that it is a Series instead of a
        # DataFrame and reformat the data to match the expected structure.
        column_headers = ['"{}"'.format(df_source.name)]
        data = df_source.values.reshape([len(df_source), 1]).tolist()

    json_data = json_internal.dumps(data, cls=encoding.ComplexJsonEncoder)

    return templating.render_template(
        'table.html',
        id=table_id,
        scale=min(0.95, max(0.05, scale)),
        data=json_data,
        column_headers=', '.join(column_headers)
    )


def whitespace(lines: float = 1.0) -> str:
    """

    :param lines:
    :return:
    """
    environ.abort_thread()
    pixels = round(12 * lines)
    return '<div style="height:{}px"> </div>'.format(pixels)


def jinja(path: str, **kwargs) -> str:
    """

    :param path:
    :param kwargs:
    :return:
    """
    environ.abort_thread()
    return templating.render_file(path, **kwargs)


def svg(svg_data: str) -> str:
    """

    :param svg_data:
    :return:
    """
    environ.abort_thread()

    return templating.render(
        '<div class="svg-box">{{ svg }}</div>',
        svg=svg_data
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
    environ.abort_thread()

    out = []
    keys = list(data.keys())
    keys.sort()

    for key in keys:
        value = data[key]
        value_type = getattr(
            value,
            '__class__',
            {'__name__': 'Unknown'}
        ).__name__

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
            values=values,
            types=types,
            type=value_type,
            value=value
        ))

    return ''.join(out)
