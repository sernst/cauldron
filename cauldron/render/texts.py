import re
import textwrap
from cauldron import environ

try:
    import markdown as md
except Exception:  # pragma: no cover
    md = None

from cauldron.render import utils as render_utils
from cauldron import templating


def latex(source: str, inline: bool = False) -> str:
    """

    :param source:
    :param inline:
    :return:
    """
    environ.abort_thread()

    return templating.render_template(
        'katex.html',
        source=render_utils.format_latex(source),
        inline=inline
    )


def head(value, count: int = 5) -> str:
    """

    :param value:
    :param count:
    :return:
    """
    environ.abort_thread()

    if count < 1:
        return ''

    try:
        if hasattr(value, 'head'):
            return preformatted_text(
                '\n'.join(['{}'.format(v) for v in value.head(count)])
            )
    except Exception:
        pass

    if isinstance(value, str):
        return preformatted_text('\n'.join(value.split('\n')[:count]))

    if isinstance(value, (list, tuple)):
        out = ['{}'.format(v) for v in value[:count]]
        return preformatted_text('\n'.join(out))

    if isinstance(value, dict):
        out = []
        keys = sorted(list(value.keys()))
        for key in keys[:count]:
            out.append('{}: {}'.format(key, value[key]))
        return preformatted_text('\n'.join(out))

    try:
        value = list(value)
        out = ['{}'.format(v) for v in value[:count]]
        return preformatted_text('\n'.join(out))
    except Exception:
        pass

    out = '{}'.format(value)
    out = out.split('\n')
    return '\n'.join(out[:count])


def tail(value, count: int = 5) -> str:
    """

    :param value:
    :param count:
    :return:
    """
    environ.abort_thread()

    if count < 1:
        return ''

    try:
        if hasattr(value, 'tail'):
            return preformatted_text(
                '\n'.join(['{}'.format(v) for v in value.tail(count)])
            )
    except Exception:
        pass

    if isinstance(value, str):
        return preformatted_text(
            '\n'.join(value.split('\n')[-count:])
        )

    if isinstance(value, (list, tuple)):
        out = ['{}'.format(v) for v in value[-count:]]
        return preformatted_text('\n'.join(out))

    if isinstance(value, dict):
        out = []
        keys = sorted(list(value.keys()), reverse=True)
        for key in keys[:count]:
            out.append('{}: {}'.format(key, value[key]))
            return preformatted_text('\n'.join(out))

    try:
        value = list(value)
        out = ['{}'.format(v) for v in value[-count:]]
        return preformatted_text('\n'.join(out))
    except Exception:
        pass

    out = '{}'.format(value).split('\n')
    return '\n'.join(out[-count:])


def text(value: str) -> str:
    """

    :param value:
    :return:
    """
    environ.abort_thread()

    value = render_utils.html_escape(value)
    lines = str(value).strip().split('\n')
    paragraph_separator = '</p><p class="plaintextbox">'

    # Convert empty lines into paragraph separators
    for index, line in enumerate(lines):
        lines[index] = line.strip() or paragraph_separator

    return '<p class="plaintextbox">{text}</p>'.format(text=' '.join(lines))


def preformatted_text(source: str) -> str:
    """Renders preformatted text box"""
    environ.abort_thread()

    if not source:
        return ''

    source = render_utils.html_escape(source)

    return '<pre class="preformatted-textbox">{text}</pre>'.format(
        text=str(textwrap.dedent(source))
    )


def markdown(
        source: str = None,
        source_path: str = None,
        preserve_lines: bool = False,
        font_size: float = None,
        **kwargs
) -> dict:
    """
    Renders a markdown file with support for Jinja2 templating. Any keyword
    arguments will be passed to Jinja2 for templating prior to rendering the
    markdown to HTML for display within the notebook.

    :param source:
        A string of markdown text that should be rendered to HTML for 
        notebook display.
    :param source_path:
        The path to a markdown file that should be rendered to HTML for
        notebook display.
    :param preserve_lines:
        If True, all line breaks will be treated as hard breaks. Use this
        for pre-formatted markdown text where newlines should be retained
        during rendering.
    :param font_size:
        Specifies a relative font size adjustment. The default value is 1.0,
        which preserves the inherited font size values. Set it to a value
        below 1.0 for smaller font-size rendering and greater than 1.0 for
        larger font size rendering.
    :return:
        The HTML results of rendering the specified markdown string or file.
    """

    environ.abort_thread()

    library_includes = []

    rendered = textwrap.dedent(
        templating.render_file(source_path, **kwargs)
        if source_path else
        templating.render(source or '', **kwargs)
    )

    if md is None:
        raise ImportError('Unable to import the markdown package')

    offset = 0
    while offset < len(rendered):
        bound_chars = '$$'
        start_index = rendered.find(bound_chars, offset)

        if start_index < 0:
            break

        inline = rendered[start_index + 2] != '$'
        bound_chars = '$$' if inline else '$$$'
        end_index = rendered.find(
            bound_chars,
            start_index + len(bound_chars)
        )

        if end_index < 0:
            break
        end_index += len(bound_chars)

        chunk = rendered[start_index: end_index] \
            .strip('$') \
            .strip() \
            .replace('@', '\\')

        if inline:
            chunk = chunk.replace('\\', '\\\\')

        chunk = latex(chunk, inline)
        rendered = '{pre}{gap}{latex}{gap}{post}'.format(
            pre=rendered[:start_index],
            latex=chunk,
            post=rendered[end_index:],
            gap='' if inline else '\n\n'
        )

        if 'katex' not in library_includes:
            library_includes.append('katex')

        offset = end_index

    extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.admonition',
        'markdown.extensions.sane_lists',
        'markdown.extensions.nl2br' if preserve_lines else None
    ]

    body = templating.render_template(
        'markdown-block.html',
        text=md.markdown(rendered, extensions=[
            e for e in extensions if e is not None
        ]),
        font_size=font_size
    )

    pattern = re.compile('src="(?P<url>[^"]+)"')
    body = pattern.sub(r'data-src="\g<url>"', body)
    return dict(
        body=body,
        library_includes=library_includes,
        rendered=rendered
    )
