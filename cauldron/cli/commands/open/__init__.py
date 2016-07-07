import os
import typing
import webbrowser
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.open import actions
from cauldron.cli.interaction import autocompletion

NAME = 'open'
DESCRIPTION = 'Opens a cauldron project'


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
        'path',
        nargs='?',
        default=None,
        help=cli.reformat(
            """
            A path to the directory containing a cauldron project. Special
            location paths can also be used.
            """
        )
    )

    parser.add_argument(
        '-s', '--show',
        dest='show_in_browser',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            The previously stored state of the project will open in the browser
            for display if this flag is included.
            """
        )
    )

    parser.add_argument(
        '-l', '--last',
        dest='last_opened_project',
        default=False,
        action='store_true',
        help=cli.reformat("""
            The open command will open the most recently opened project if this
            flag is included.
            """)
    )

    parser.add_argument(
        '-r', '--recent',
        dest='a_recent_project',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            Displays a list of recently opened projects for you to select from.
            """
        )
    )

    parser.add_argument(
        '-a', '--available',
        dest='list_available',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            List all known projects.
            """
        )
    )


def execute(
        parser: ArgumentParser,
        path: str = None,
        last_opened_project: bool = False,
        a_recent_project: bool = False,
        show_in_browser: bool = False,
        list_available: bool = False
):
    """

    :return:
    """

    path = path.strip('"') if path else None

    if list_available:
        actions.echo_known_projects()
        return

    if last_opened_project:
        path = actions.fetch_last()
        if not path:
            return
        actions.open_project(path)
    elif a_recent_project:
        path = actions.fetch_recent()
        if not path:
            return
        actions.open_project(path)
    elif not path or not path.strip():
        actions.echo_known_projects()
        return
    else:
        p = actions.fetch_location(path)
        actions.open_project(p if p else path)

    if show_in_browser:
        webbrowser.open(cauldron.project.internal_project.url)


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
            shorts=['s', 'l', 'r', 'a'],
            longs=['show', 'last', 'recent', 'available']
        )

    if len(parts) == 1:
        value = parts[0]

        if value.startswith('@examples:'):
            path_segment = value.split(':', 1)[-1]
            return autocompletion.match_path(
                segment,
                environ.paths.package('resources', 'examples', path_segment),
                include_files=False
            )

        if value.startswith('@home:'):
            path_segment = value.split(':', 1)[-1]
            return autocompletion.match_path(
                segment,
                environ.paths.clean(
                    os.path.join('~', 'cauldron', path_segment)
                ),
                include_files=False
            )

        environ.configs.load()
        aliases = environ.configs.fetch('folder_aliases', {})
        matches = ['@{}:'.format(x) for x in aliases.keys()]

        for m in matches:
            if value.startswith(m):
                return autocompletion.match_path(
                    segment,
                    environ.paths.clean(os.path.join(
                        aliases[m[1:-1]]['path'],
                        value[-1].split(':', 1)[-1]
                    )),
                    include_files=False
                )

        matches.append('@examples:')
        matches.append('@home:')

        if value.startswith('@'):
            return autocompletion.matches(segment, value, matches)

        return autocompletion.match_path(segment, value)

