from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers import get_lexer_for_filename
from pygments.lexers import get_lexer_for_mimetype
from pygments.lexers import guess_lexer
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound


def as_html(
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

    lexer = fetch_lexer(source, language, filename, mime_type)
    if not lexer:
        return '<div>Unrecognized code</div>'

    return highlight(source, lexer, HtmlFormatter(linenos=True))


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
