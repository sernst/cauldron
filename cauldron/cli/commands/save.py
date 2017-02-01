import glob
import json
import os
import typing
import zipfile
from argparse import ArgumentParser
from datetime import datetime

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.environ import Response
from cauldron.session import projects

NAME = 'save'
DESCRIPTION = """
    Saves the current project's notebook as a Cauldron Document File (CDF)
    for viewing in the Cauldron reader application.
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
        'path',
        default=None,
        help=cli.reformat("""
            The file path to the cdf file to be saved. If the cdf file
            extension is missing it will be appended to the end of the path's
            filename. If a directory is specified instead of a file, the cdf
            file will saved into that directory using the name of the project
            as the filename.
            """)
    )


def clean_path(project: 'projects.Project', path: str) -> str:
    cleaned = environ.paths.clean(path)

    if os.path.isdir(cleaned):
        return os.path.join(cleaned, '{}.cdf'.format(project.title))

    if not cleaned.endswith('.cdf'):
        return '{}.cdf'.format(cleaned)

    return cleaned


def create_settings(project: 'projects.Project') -> dict:
    """

    :param project:
    :return:
    """

    return dict(
        title=project.title,
        version=environ.notebook_version,
        timestamp=datetime.now().isoformat()
    )


def write_file(project: 'projects.Project', path: str) -> str:
    """

    :param project:
    :param path:
    :return:
    """

    save_path = clean_path(project, path)
    save_directory = os.path.dirname(save_path)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    z = zipfile.ZipFile(save_path, 'w', allowZip64=True)
    root_folder = project.output_directory

    globber = glob.iglob('{}/**/*.*'.format(root_folder), recursive=True)

    def add(file_path: str) -> str:
        slug = file_path[len(root_folder):].strip(os.sep)
        z.write(file_path, slug)
        return slug

    slugs = [add(match) for match in globber]
    settings = create_settings(project)
    settings['files'] = slugs

    z.writestr('reader_configs.json', json.dumps(settings))
    z.close()

    return save_path


def execute(parser: ArgumentParser, response: Response, path: str) -> Response:

    project = cauldron.project.internal_project

    if not project:
        return (
            response
            .fail(
                code='NO_PROJECT',
                message='No project is open. Nothing to save'
            )
            .console(whitespace=1)
            .response
        )

    try:
        saved_path = write_file(project, path)
    except Exception as err:
        print(err)
        return (
            response
            .fail(
                code='WRITE_SAVE_ERROR',
                message='Unable to write the cdf file output',
                error=err
            )
            .console(whitespace=1)
            .response
        )

    return (
        response
        .update(path=saved_path)
        .notify(
            kind='SUCCESS',
            code='SAVED',
            message='The project has been saved to: {}'.format(saved_path)
        )
        .console(whitespace=1)
        .response
    )
