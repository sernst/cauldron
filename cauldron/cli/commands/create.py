import os
import json
import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron.cli import autocompletion
from cauldron import environ
from cauldron.cli.commands.open import actions as open_actions

DESCRIPTION = """
    Create a new Cauldron project
    """


def populate(parser: ArgumentParser):
    """

    :param parser:
    :return:
    """

    parser.add_argument(
        'project_name',
        type=str,
        default=None,
        help=cli.reformat("""
            The name of the project you want to create. A folder with this
            name will be created and the cauldron project will be stored
            within
            """)
    )

    parser.add_argument(
        'directory',
        type=str,
        default=None,
        help=cli.reformat("""
            The parent directory where the cauldron project directory will be
            created.
            """)
    )


def execute(parser: ArgumentParser, project_name: str, directory: str):
    """

    :return:
    """

    location = open_actions.fetch_location(directory)
    if location:
        directory = location

    directory = environ.paths.clean(directory).rstrip(os.sep)
    if not directory.endswith(project_name):
        directory = os.path.join(directory, project_name)

    if os.path.exists(directory):
        if os.path.exists(os.path.join(directory, 'cauldron.json')):
            environ.log(
                """
                [ABORTED]: Directory already exists and contains a cauldron
                    project file.

                    {}
                """.format(directory),
                whitespace=1
            )
            return
    else:
        os.makedirs(directory)

    project_data = dict(
        name=project_name,
        title=project_name.replace('_', ' ').replace('-', ' ').capitalize(),
        summary='',
        steps=[]
    )

    with open(os.path.join(directory, 'cauldron.json'), 'w+') as f:
        json.dump(project_data, f, indent=2, sort_keys=True)

    open_actions.open_project(directory)


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    if len(parts) < 2:
        return []

    value = parts[-1]

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

    matches.append('@home:')

    if value.startswith('@'):
        return autocompletion.matches(segment, value, matches)

    return autocompletion.match_path(segment, parts[-1])
