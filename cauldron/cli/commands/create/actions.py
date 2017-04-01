import os
import json

from cauldron import environ
from cauldron.environ.response import Response
from cauldron.session import projects
from cauldron.cli.commands.open import actions as open_actions


def create_definition(
        name: str,
        title: str = '',
        summary: str = '',
        author: str = '',
        no_naming_scheme: bool = False,
        library_folder: str = None,
        assets_folder: str = None
) -> dict:
    """ """

    project_title = (
        title
        if title else
        name.replace('_', ' ').replace('-', ' ').capitalize()
    )

    definition = dict(
        name=name,
        title=project_title,
        summary=summary,
        author=author,
        steps=[],
        naming_scheme=None if no_naming_scheme else projects.DEFAULT_SCHEME
    )

    if library_folder:
        definition['library_folders'] = [library_folder]

    if assets_folder:
        definition['asset_folders'] = [assets_folder]

    return definition


def allow_create(project_directory: str) -> Response:
    """ """
    project_source_path = os.path.join(project_directory, 'cauldron.json')
    if os.path.exists(project_source_path):
        return Response().fail(
            code='ALREADY_EXISTS',
            message='A Cauldron project already exists in this directory'
        ).kernel(
            directory=project_directory
        ).console(
            """
            [ABORTED]: Directory already exists and contains a cauldron
                project file.

                {}
            """.format(project_directory),
            whitespace=1
        ).response

    return Response()


def resolve_project_directory(directory: str, project_name: str) -> str:
    """ """

    location = open_actions.fetch_location(Response(), directory)
    project_directory = location if location else directory
    project_directory = environ.paths.clean(project_directory).rstrip(os.sep)

    if not project_directory.endswith(project_name):
        return environ.paths.join(project_directory, project_name)
    return project_directory


def make_directory(directory: str) -> Response:
    """ """

    if os.path.exists(directory):
        return Response()

    try:
        os.makedirs(directory)
        return Response()
    except Exception as error:
        return Response().fail(
            message=(
                """
                Unable to create project folder in the specified directory.
                Do you have the necessary write permissions for this
                location?
                """
            ),
            code='DIRECTORY_CREATE_FAILED',
            error=error,
            directory=directory
        ).console(
            """
            [ERROR]: Unable to create project folder. Do you have the necessary
                write permissions to the path:

                "{}"
            """.format(directory),
            whitespace=1
        ).response


def create_project_directories(
        project_name: str,
        directory: str,
        library_folder: str = None,
        assets_folder: str = None
) -> Response:
    """ """

    project_directory = resolve_project_directory(directory, project_name)
    response = allow_create(project_directory)
    if response.failed:
        return response

    library_directory = (
        environ.paths.join(project_directory, library_folder)
        if library_folder else
        None
    )

    assets_directory = (
        environ.paths.join(project_directory, assets_folder)
        if assets_folder else
        None
    )

    directories = filter(
        lambda x: x is not None,
        [project_directory, library_directory, assets_directory]
    )

    for d in directories:
        response = make_directory(d)
        if response.failed:
            return response

    return Response().update(source_directory=project_directory)


def write_project_data(project_directory: str, definition: dict) -> Response:
    """

    :param project_directory:
    :param definition:
    :return:
    """

    source_path = environ.paths.join(project_directory, 'cauldron.json')

    try:
        with open(source_path, 'w') as f:
            json.dump(definition, f, indent=2, sort_keys=True)
    except Exception as error:
        return Response().fail(
            message=(
                """
                Unable to write to the specified project directory.
                Do you have the necessary write permissions for this
                location?
                """
            ),
            code='PROJECT_CREATE_FAILED',
            error=error,
            directory=project_directory
        ).console(
            """
            [ERROR]: Unable to write project data. Do you have the necessary
                write permissions in the path:

                "{}"
            """.format(project_directory),
            whitespace=1
        ).response

    return Response()
