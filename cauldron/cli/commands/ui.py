import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import ui
from cauldron.cli.interaction import autocompletion
from cauldron.environ import Response
from cauldron.ui import configs

NAME = 'ui'
DESCRIPTION = (
    """
    Starts the cauldron ui.
    """
)
SYNCHRONOUS = True


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    return ui.create_parser(parser, shell=True)


def execute(
        context: cli.CommandContext,
        port: int = configs.DEFAULT_PORT,
        debug: bool = False,
        host: str = None,
        public: bool = False
) -> Response:
    """ """
    ui.start(
        port=port,
        debug=debug,
        public=public,
        host=host,
        quiet=True
    )

    return context.response.notify(
        kind='SUCCESS',
        code='COMPLETED',
        message='UI session has ended.'
    ).console(
        whitespace_bottom=1
    ).response


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    if parts[-1].startswith('-'):
        return autocompletion.match_flags(
            segment=segment,
            value=parts[-1],
            shorts=['p', 'n'],
            longs=['port', 'name', 'host', 'public']
        )

    return []
