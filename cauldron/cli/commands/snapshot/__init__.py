import typing
from argparse import ArgumentParser

import cauldron
from cauldron import environ
from cauldron.cli import autocompletion
from cauldron.cli.commands.snapshot import actions

DESCRIPTION = """
    Stores the current results as a snapshot with the specified snapshot
    name for reference
    """


def populate(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    parser.add_argument(
        'action',
        default=None,
        help="""
            The snapshot action to be executed
            """
    )

    parser.add_argument(
        'arguments',
        nargs='*',
        default=None,
        help="""
            The snapshot action to be executed
            """
    )


def execute(parser: ArgumentParser, action: str, arguments: list):
    """

    :param parser:
    :param action:
    :param arguments:
    :return:
    """

    if not action:
        environ.log(
            """
            [ERROR]: An action is required for the snapshot command
            """
        )
        return

    action = action.strip().lower()
    project = cauldron.project.internal_project

    if not project:
        environ.log(
            """
            [ERROR]: No project has been opened. Use the "open" command to
            open a project.
            """
        )
        return

    if action == 'add':
        return actions.create_snapshot(project, *arguments)

    if action == 'list':
        return actions.list_snapshots(project)


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    # print('{e}[9999D{e}[KAUTO "{prefix}" {parts}\n>>> {line}'.format(
    #     prefix=segment,
    #     parts=parts,
    #     line=line,
    #     e=chr(27)
    # ), end='')

    if len(parts) == 1:
        return autocompletion.matches(
            segment,
            'add',
            'remove',
            'list',
            'show'
        )
