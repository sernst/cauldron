import subprocess
import sys
import os
import typing
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron.cli import sync
from cauldron.environ import Response

NAME = 'show'
DESCRIPTION = 'Opens the current project display in the default browser'


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
        'target', nargs='?', default='browser',
        help=cli.reformat(
            """
            What to show, which can be one of "browser" or "files".
            """
        )
    )


def open_folder(path: str):
    """Opens the local project folder."""
    if sys.platform == 'darwin':
        subprocess.check_call(['open', '--', path])
    elif sys.platform == 'linux2':
        subprocess.check_call(['xdg-open', '--', path])
    elif sys.platform == 'win32':
        # subprocess.check_call(['explorer', path])
        os.startfile(path)


def execute_remote(
        context: cli.CommandContext,
        target: str = 'browser',
) -> Response:
    """ """
    if target != 'browser':
        status_response = sync.comm.send_request(
            endpoint='/sync-status',
            method='GET',
            remote_connection=context.remote_connection
        )
        source_directory = status_response.data.get('remote_source_directory')
        open_folder(source_directory)
        return context.response

    response = sync.comm.send_request(
        endpoint='/status',
        remote_connection=context.remote_connection
    )

    remote_slug = response.data.get('project', {}).get('remote_slug')
    if response.success:
        url = ''.join([
            context.remote_connection.url.rstrip('/'),
            '/',
            remote_slug.lstrip('/')
        ])

        cli.open_in_browser(url)

    return context.response.consume(response)


def execute(
        context: cli.CommandContext,
        target: str = 'browser',
) -> Response:
    """

    :return:
    """
    response = context.response
    project = cauldron.project.internal_project
    if not project:
        return response.fail(
            code='NO_OPEN_PROJECT',
            message='No project is currently open.'
        ).console(
            """
            [ABORTED]: No project is currently open. Please use the open
                command to load a project.
            """,
            whitespace=1
        ).response

    if target == 'browser':
        cli.open_in_browser(project)
    else:
        open_folder(project.source_directory)

    return response
