from textwrap import dedent
import webbrowser
import sys


def open_in_browser(project):
    webbrowser.open(project.baked_url)


def reformat(source: str) -> str:
    """
    Formats the source string to strip newlines on both ends and dedents the
    the entire string

    :param source:
        The string to reformat
    """

    return dedent(source.strip('\n')).strip()


def as_single_line(source: str) -> str:
    """

    :param source:
    :return:
    """
    return reformat(source).replace('\n', ' ').replace('  ', ' ')
