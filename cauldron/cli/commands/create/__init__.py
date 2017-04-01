import os
import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.create import actions as create_actions
from cauldron.cli.commands.open import opener as project_opener
from cauldron.cli.commands.open import remote as remote_project_opener
from cauldron.cli.interaction import autocompletion

NAME = 'create'
DESCRIPTION = 'Create a new Cauldron project'


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
        help=cli.reformat(
            """
            The name of the project you want to create. A folder with this
            name will be created and the cauldron project will be stored
            within
            """
        )
    )

    parser.add_argument(
        'directory',
        type=str,
        default=None,
        help=cli.reformat(
            """
            The parent directory where the cauldron project directory will be
            created.
            """
        )
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

    parser.add_argument(
        '--no-naming-scheme',
        dest='no_naming_scheme',
        default=False,
        action='store_true',
        help=cli.reformat('Disables the auto naming scheme for the project')
    )

    parser.add_argument(
        '--forget',
        dest='forget',
        default=False,
        action='store_true',
        help=cli.reformat('Forget that this project was opened')
    )

    parser.add_argument(
        '--libs',
        dest='library_folder',
        default=None,
        type=str,
        help=cli.reformat('The name of the internal library root folder')
    )

    parser.add_argument(
        '--assets',
        dest='assets_folder',
        default=None,
        type=str,
        help=cli.reformat('The name of the internal assets folder')
    )


def execute(
        context: cli.CommandContext,
        project_name: str,
        directory: str,
        title: str = '',
        summary: str = '',
        author: str = '',
        forget: bool = False,
        no_naming_scheme: bool = False,
        library_folder: str = None,
        assets_folder: str = None
):
    """

    :return:
    """

    response = context.response

    response.consume(create_actions.create_project_directories(
        project_name,
        directory,
        assets_folder=assets_folder,
        library_folder=library_folder
    ))
    if response.failed:
        return response

    definition = create_actions.create_definition(
        name=project_name,
        title=title,
        summary=summary,
        author=author,
        no_naming_scheme=no_naming_scheme,
        library_folder=library_folder,
        assets_folder=assets_folder
    )

    source_directory = response.data['source_directory']
    response.consume(create_actions.write_project_data(
        source_directory,
        definition
    ))

    response.consume(create_actions.write_project_data(
        source_directory,
        definition
    ))
    if response.failed:
        return response

    if context.remote_connection.active:
        opened = remote_project_opener.sync_open(context, source_directory)
    else:
        opened = project_opener.open_project(
            source_directory,
            forget=forget
        )

    return response.consume(opened)


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
                    value.split(':', 1)[-1]
                )),
                include_files=False
            )

    matches.append('@home:')

    if value.startswith('@'):
        return autocompletion.matches(segment, value, matches)

    return autocompletion.match_path(segment, parts[-1])
