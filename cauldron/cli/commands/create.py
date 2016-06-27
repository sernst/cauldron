import json
import os
import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.open import actions as open_actions
from cauldron.cli.interaction import autocompletion

NAME = 'create'
DESCRIPTION = """
    Create a new Cauldron project
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

    parser.add_argument(
        '-t', '--title',
        dest='title',
        type=str,
        default='',
        help=cli.reformat('The title for the new project')
    )

    parser.add_argument(
        '-s', '--summary',
        dest='summary',
        type=str,
        default='',
        help=cli.reformat('A short summary description of the new project')
    )

    parser.add_argument(
        '-a', '--author',
        dest='author',
        type=str,
        default='',
        help=cli.reformat('Names of the author or authors of the project')
    )


def execute(
        parser: ArgumentParser,
        project_name: str,
        directory: str,
        title: str = '',
        summary: str = '',
        author: str = ''
):
    """

    :return:
    """

    project_name = project_name.strip('" \t')
    directory = directory.strip('" \t')
    summary = summary.strip('" \t')
    title = title.strip('" \t')
    author = author.strip('" \t')

    if not title:
        title = project_name.replace('_', ' ').replace('-', ' ').capitalize()

    location = open_actions.fetch_location(directory)
    if location:
        directory = location

    directory = environ.paths.clean(directory).rstrip(os.sep)
    if not directory.endswith(project_name):
        directory = os.path.join(directory, project_name)

    if os.path.exists(directory):
        if os.path.exists(os.path.join(directory, 'cauldron.json')):
            environ.output.fail().notify(
                kind='ABORTED',
                code='ALREADY_EXISTS',
                message='Cauldron project exists in the specified directory'
            ).kernel(
                directory=directory
            ).console(
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
        title=title,
        summary=summary,
        author=author,
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
