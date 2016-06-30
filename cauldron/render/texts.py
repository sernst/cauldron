import re
import textwrap

try:
    import markdown as md
except Exception:
    md = None

from cauldron.render import utils as render_utils
from cauldron import templating


def latex(source: str, inline: bool = False) -> str:
    """

    :param source:
    :param inline:
    :return:
    """

    return templating.render_template(
        'katex.html',
        source=render_utils.format_latex(source),
        inline=inline
    )


def text(value: str) -> str:
    """

    :param value:
    :return:
    """

    value = render_utils.html_escape(value)
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

    source = render_utils.html_escape(source)

    return '<pre class="preformatted-textbox">{text}</pre>'.format(
        text=str(textwrap.dedent(source))
    )


def markdown(source: str, **kwargs) -> dict:
    """

    :param source:
    :return:
    """

    library_includes = []
    source = templating.render(source, **kwargs)

    if md is None:
        raise ImportError(textwrap.dedent(
            """
            Unable to import the markdown package. Please check
            """).strip())

    source = textwrap.dedent(source)

    offset = 0
    while offset < len(source):
        bound_chars = '$$'
        start_index = source.find(bound_chars, offset)

        if start_index < 0:
            break

        inline = source[start_index + 2] != '$'
        bound_chars = '$$' if inline else '$$$'
        end_index = source.find(
            bound_chars,
            start_index + len(bound_chars)
        )

        if end_index < 0:
            break
        end_index += len(bound_chars)

        chunk = source[start_index: end_index] \
            .strip('$') \
            .strip() \
            .replace('@', '\\')

        if inline:
            chunk = chunk.replace('\\', '\\\\')

        chunk = latex(chunk, inline)
        source = '{pre}{gap}{latex}{gap}{post}'.format(
            pre=source[:start_index],
            latex=chunk,
            post=source[end_index:],
            gap='' if inline else '\n\n'
        )

        if 'katex' not in library_includes:
            library_includes.append('katex')

        offset = end_index

    body = templating.render(
        """
        <div class="textbox markdown">{{ text }}</div>
        """,
        text=md.markdown(source)
    )

    pattern = re.compile('src="(?P<url>[^"]+)"')
    body = pattern.sub('data-src="\g<url>"', body)
    return dict(
        body=body,
        library_includes=library_includes
    )
