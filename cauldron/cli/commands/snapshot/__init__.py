import typing
import webbrowser
from argparse import ArgumentParser
from datetime import datetime

import cauldron
from cauldron import environ
from cauldron.cli.commands.snapshot import actions
from cauldron.cli.interaction import autocompletion

NAME = 'snapshot'
DESCRIPTION = """
    Stores the current results as a snapshot with the specified snapshot
    name for reference
    """


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """

    :param parser:
    :param raw_args:
    :param assigned_args:
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
        return environ.output.fail().notify(
            kind='ERROR',
            code='NO_ACTION_ARG',
            message='An action is required for the snapshot command'
        ).console(whitespace=1)

    action = action.strip().lower()
    project = cauldron.project.internal_project

    if not project:
        return environ.output.fail().notify(
            kind='ERROR',
            code='NO_OPEN_PROJECT',
            message='No open project'
        ).console(
            '[ERROR]: No open project. Use the "open" command to open one.'
        )

    if action == 'remove':
        return actions.remove_snapshot(project, *arguments)

    if action == 'add':
        return actions.create_snapshot(project, *arguments)

    if action == 'list':
        return actions.list_snapshots(project)

    if action == 'open':
        name = arguments[0]
        result = actions.open_snapshot(project, name)
        if result is None:
            environ.log('[ERROR]: No snapshot found named "{}"'.format(name))
            return

        environ.log_header('SNAPSHOT: {}'.format(name))
        environ.log(
            """
            URL: {url}
            LAST MODIFIED: {modified}
            """.format(
                url=result['url'],
                modified=datetime.fromtimestamp(
                    result['last_modified']
                ).strftime('%H:%M %b %d, %Y')
            ),
            whitespace=1
        )

        webbrowser.open(result['url'])


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
            parts[0] if len(parts) else '',
            ['add', 'remove', 'list', 'show', 'open']
        )

    project = cauldron.project.internal_project

    if parts[0] in ['open', 'remove', 'show'] and len(parts) < 3:
        names = [x['name'] for x in actions.get_snapshot_listing(project)]
        out = autocompletion.matches(segment, parts[-1], names)
        return out

    return []
