import os
import typing
import webbrowser
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.cli import autocompletion
from cauldron.cli.commands.open import actions

DESCRIPTION = """
    Opens a cauldron project.
    """


def populate(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    parser.add_argument(
        'path',
        nargs='?',
        default=None,
        help=cli.reformat("""
            A path to the directory containing a cauldron project. Special
            location paths can also be used.
            """)
    )

    parser.add_argument(
        '-s', '--show',
        dest='show_in_browser',
        default=False,
        action='store_true',
        help=cli.reformat("""
            When set the previously stored state of the project will open in
            the browser for display.
            """)
    )

    parser.add_argument(
        '-l', '--last',
        dest='last_opened_project',
        default=False,
        action='store_true',
        help=cli.reformat("""
            When set, the open command will open the most recently opened
            project.
            """)
    )

    parser.add_argument(
        '-r', '--recent',
        dest='a_recent_project',
        default=False,
        action='store_true',
        help=cli.reformat("""
            When set, the open command will display a list of recently opened
            projects for you to select from.
            """)
    )


def execute(
        parser: ArgumentParser,
        path: str = None,
        last_opened_project: bool = False,
        a_recent_project: bool = False,
        show_in_browser: bool = False
):
    """

    :return:
    """

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
        parser.print_help()
        environ.log("""
            [ABORTED]: There was not enough information in that command to
                open a project. See information above for how to use this
                command.
            """)
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
            shorts=['s', 'l'],
            longs=['show', 'last', 'recent']
        )

    if len(parts) == 1:
        value = parts[0]

        if value.startswith('@examples:'):
            segment = value.split(':', 1)[-1]
            return autocompletion.match_path(
                segment,
                environ.paths.package('resources', 'examples', segment),
                include_files=False
            )

        if value.startswith('@home:'):
            segment = value.split(':', 1)[-1]
            return autocompletion.match_path(
                segment,
                environ.paths.clean(os.path.join('~', 'cauldron', segment)),
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

