import webbrowser
from argparse import ArgumentParser
from textwrap import dedent
from typing import NamedTuple

from cauldron import environ
from cauldron.environ.response import Response


CommandContext = NamedTuple('COMMAND_CONTEXT', [
    ('name', str),
    ('raw_args', str),
    ('args', list),
    ('parser', ArgumentParser),
    ('response', Response),
    ('remote_connection', 'environ.RemoteConnection')
])


def make_command_context(
        name: str = None,
        raw_args: str = None,
        args: list = None,
        parser: ArgumentParser = None,
        response: Response = None,
        remote_connection: 'environ.RemoteConnection' = None
) -> CommandContext:
    """ """

    remote = (
        remote_connection
        if remote_connection else
        environ.remote_connection
    )

    return CommandContext(
        name=name,
        raw_args=raw_args,
        args=args if args is not None else [],
        parser=parser if parser else ArgumentParser(),
        response=response if response else Response(),
        remote_connection=remote
    )


def open_in_browser(project_or_url):
    """ """

    url = getattr(project_or_url, 'baked_url', project_or_url)
    webbrowser.open(url)


def reformat(source: str) -> str:
    """
    Formats the source string to strip newlines on both ends and dedents the
    the entire string

    :param source:
        The string to reformat
    """

    value = source if source else ''
    return dedent(value.strip('\n')).strip()


def as_single_line(source: str) -> str:
    """

    :param source:
    :return:
    """
    return reformat(source).replace('\n', ' ').replace('  ', ' ')
