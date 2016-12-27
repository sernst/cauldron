from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers import get_lexer_for_filename
from pygments.lexers import get_lexer_for_mimetype
from pygments.lexers import guess_lexer
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers.templates import DjangoLexer
from pygments.util import ClassNotFound
from cauldron import environ


class CodeBlockHtmlFormatter(HtmlFormatter):

    def wrap(self, source, outfile):
        return source


def as_html(
        source: str,
        language: str = None,
        filename: str = None,
        mime_type: str = None,
        is_code_block: bool = False
):
    """

    :param source:
    :param language:
    :param filename:
    :param mime_type:
    :param is_code_block:
    :return:
    """

    environ.abort_thread()

    lexer = fetch_lexer(source, language, filename, mime_type)
    Formatter = CodeBlockHtmlFormatter if is_code_block else HtmlFormatter

    dom = highlight(
        code=source,
        lexer=lexer if lexer else DjangoLexer(),
        formatter=Formatter(linenos=True)
    )

    if not is_code_block:
        return dom

    return (
        dom
        .replace('<pre>', '')
        .replace('</pre>', '')
        .replace('<table', '<div')
        .replace('</table>', '</div>')
        .replace('<tr>', '')
        .replace('</tr>', '')
        .replace('<td', '<div')
        .replace('</td>', '</div>')
    )


def fetch_lexer(
        source: str,
        language: str = None,
        filename: str = None,
        mime_type: str = None
):
    """

    :param source:
    :param language:
    :param filename:
    :param mime_type:
    :return:
    """

    environ.abort_thread()

    try:
        if language:
            return get_lexer_by_name(language, stripall=True)
    except ClassNotFound:
        pass

    if filename:
        try:
            return get_lexer_for_filename(filename, stripall=True)
        except ClassNotFound:
            pass

        try:
            return guess_lexer_for_filename(filename, source, stripall=True)
        except ClassNotFound:
            pass

    try:
        if mime_type:
            return get_lexer_for_mimetype(mime_type, stripall=True)
    except ClassNotFound:
        pass

    try:
        return guess_lexer(source, stripall=True)
    except ClassNotFound:
        return None
