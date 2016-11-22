import json
import os
import typing
from argparse import ArgumentParser

from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.open import actions as open_actions
from cauldron.cli.commands.open import opener as project_opener
from cauldron.cli.interaction import autocompletion
from cauldron.session import projects
from cauldron.environ import Response

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


def create_project_directory(directory):
    """

    :param directory:
    :return:
    """

    if os.path.exists(directory):
        return True

    try:
        os.makedirs(directory)
        return os.path.exists(directory)
    except Exception as err:
        return False


def write_project_data(project_directory, data):
    """

    :param project_directory:
    :param data:
    :return:
    """

    project_path = os.path.join(project_directory, 'cauldron.json')
    with open(project_path, 'w+') as f:
        json.dump(data, f, indent=2, sort_keys=True)

    return True


def execute(
        parser: ArgumentParser,
        response: Response,
        project_name: str,
        directory: str,
        title: str = '',
        summary: str = '',
        author: str = '',
        forget: bool = False,
        no_naming_scheme: bool = False,
):
    """

    :return:
    """

    if not title:
        title = project_name.replace('_', ' ').replace('-', ' ').capitalize()

    location = open_actions.fetch_location(response, directory)
    if location:
        directory = location

    directory = environ.paths.clean(directory).rstrip(os.sep)
    if not directory.endswith(project_name):
        directory = os.path.join(directory, project_name)

    project_file_path = os.path.join(directory, 'cauldron.json')
    if os.path.exists(project_file_path):
        return response.fail(
            code='ALREADY_EXISTS',
            message='A Cauldron project already exists in this directory'
        ).kernel(
            directory=directory
        ).console(
            """
            [ABORTED]: Directory already exists and contains a cauldron
                project file.

                {}
            """.format(directory),
            whitespace=1
        ).response

    if not create_project_directory(directory):
        return response.fail(
            message=(
                """
                Unable to create project folder in the specified directory.
                Do you have the necessary write permissions for this
                location?
                """
            ),
            code='DIRECTORY_CREATE_FAILED',
            directory=directory
        ).console(
            """
            [ERROR]: Unable to create project folder. Do you have the necessary
                write permissions to the path:

                "{}"
            """.format(directory),
            whitespace=1
        ).response

    response.update(source_directory=directory)

    project_data = dict(
        name=project_name,
        title=title,
        summary=summary,
        author=author,
        steps=[],
        naming_scheme=None if no_naming_scheme else projects.DEFAULT_SCHEME
    )

    if not write_project_data(directory, project_data):
        return response.fail(
            message=(
                """
                Unable to write to the specified project directory.
                Do you have the necessary write permissions for this
                location?
                """
            ),
            code='PROJECT_CREATE_FAILED',
            directory=directory
        ).console(
            """
            [ERROR]: Unable to write project data. Do you have the necessary
                write permissions in the path:

                "{}"
            """.format(directory),
            whitespace=1
        ).response

    response.consume(project_opener.open_project(directory, forget=forget))

    return response


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
