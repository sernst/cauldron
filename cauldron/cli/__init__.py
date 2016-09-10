from textwrap import dedent
import webbrowser
import sys

def open_in_browser(project):
    if sys.platform == 'win32':
        webbrowser.open(project.baked_url)
    else:
        webbrowser.open(project.url)


def reformat(source: str) -> str:
    """
    Formats the source string to strip newlines on both ends and dedents the
    the entire string

    :param source:
        The string to reformat
    """

    return dedent(source.strip('\n')).strip()
