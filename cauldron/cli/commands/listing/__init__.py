import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.listing import _lister
from cauldron.cli.commands.listing import _remover
from cauldron.cli.commands.listing import discovery
from cauldron.cli.interaction import autocompletion

NAME = 'list'
DESCRIPTION = (
    """
    Displays known Cauldron projects on the local system.
    """
)


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
) -> typing.NoReturn:
    """
    Populates the commend execution argument parser with the arguments
    for the command.

    :param parser:
        ArgumentParser created for the invocation of this command.
    :param raw_args:
        Raw arguments list parsed from the command line input.
    :param assigned_args:
        A dictionary of arguments that can be assigned separately from
        the ArugmentParser. These can be useful for complex command
        situations that a standard ArgumentParser is not adept at
        handling.
    """
    subs = parser.add_subparsers(dest='action')
    subs.add_parser('all')
    subs.add_parser('recent')
    remover = subs.add_parser('erase')
    remover.add_argument('identifier', nargs='?')
    remover.add_argument('-y', '--yes', action='store_true')


def execute(
        context: cli.CommandContext,
        action: str = 'list',
        **kwargs
) -> environ.Response:
    """ """
    environ.configs.load()
    if action in ['erase']:
        return _remover.execute_removal(context, kwargs)
    elif action in ['all']:
        return discovery.echo_known_projects(context.response)

    return _lister.execute_list(context)


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """
    if len(parts) < 2:
        return autocompletion.matches(
            segment,
            parts[-1] if parts else '',
            ['erase', 'all', 'recent']
        )

    return []
