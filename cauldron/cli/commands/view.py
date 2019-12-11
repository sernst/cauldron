import os
import json
import typing
import zipfile
from argparse import ArgumentParser
from datetime import datetime

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands import ui as ui_command
from cauldron.cli.interaction import autocompletion
from cauldron.environ import Response

NAME = 'view'
DESCRIPTION = """
    Serves up a reader file for viewing through a browser or the ui.
    """

#: This command cannot be run in a separate thread. It must be
#: executed as part of the main thread.
SYNCHRONOUS = True


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """..."""
    parser.add_argument('action', choices=['open', 'close'])

    if raw_args[0].lower() == 'open':
        parser.add_argument(
            'path',
            default=None,
        )


def _close_view(context: cli.CommandContext) -> environ.Response:
    """Close the open view file, cleaning up remnants along the way."""
    directory = (environ.view or {}).get('directory')
    if not environ.view or not directory:
        return context.response.notify(
            kind='SKIPPED',
            code='NO_VIEW_OPEN',
            message='No view file is currently open.'
        ).console(whitespace=1).response

    environ.view = None
    environ.systems.remove(directory)

    return context.response.notify(
        kind='CLOSED',
        code='CLOSED_VIEW_FILE',
        message='Viewer has been closed.'
    ).console(whitespace=1).response


def execute(
        context: cli.CommandContext,
        action: str,
        path: str = None,
) -> Response:
    """..."""
    if action.lower() == 'close':
        return _close_view(context)

    now = '{}Z'.format(
        datetime.utcnow()
        .isoformat()
        .replace(':', '-')
        .replace('.', '-')
    )
    directory = environ.paths.user('reader', 'cache', now)
    clean_path = environ.paths.clean(path)
    z = zipfile.ZipFile(clean_path)
    z.extractall(directory)

    configs_path = os.path.join(directory, 'reader_configs.json')
    with open(configs_path) as f:
        configs = json.load(f)

    environ.view = {
        'id': now,
        'directory': directory,
        'configs': configs,
    }

    #: If no UI is running, this will start the UI to display
    #: the viewer file.
    if not environ.modes.has(environ.modes.UI):
        context.response.update(view=environ.view).notify(
            kind='OPENING',
            code='OPENING_VIEW_FILE',
            message='Opening view file: "{}"'.format(clean_path),
        ).console(whitespace=1)
        return ui_command.execute(context)

    return context.response.update(view=environ.view).notify(
        kind='OPENED',
        code='OPENED_VIEW_FILE',
        message='Opened view file: "{}"'.format(clean_path),
    ).console(whitespace=1).response


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """..."""
    if len(parts) < 2:
        return autocompletion.matches(segment, parts[0], [
            'open', 'close'
        ])

    action = parts[0]
    if action == 'close':
        return []

    return autocompletion.match_path(segment, parts[-1])
