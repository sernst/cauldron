import glob
import json
import os
import typing
import zipfile
from argparse import ArgumentParser
from datetime import datetime

import cauldron
from cauldron import cli
from cauldron.cli import sync
from cauldron import environ
from cauldron.environ import Response
from cauldron.session import projects

NAME = 'save'
DESCRIPTION = """
    Saves the current project's notebook as a Cauldron Display File (CAULDRON)
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
        nargs='?',
        help=cli.reformat("""
            The file path to the Cauldron file to be saved. If the file
            extension is missing it will be appended to the end of the path's
            filename. If a directory is specified instead of a file, the 
            Cauldron file will saved into that directory using the name of the 
            project as the filename.
            """)
    )


def get_default_path() -> str:
    """ """

    project = cauldron.project.internal_project

    if not project or not project.remote_source_directory:
        return os.path.abspath(os.path.expanduser('~'))

    downloads_directory = os.path.realpath(os.path.join(
        project.source_directory,
        '..',
        '__cauldron_downloads'
    ))

    count = len(os.listdir(downloads_directory))
    return os.path.join(downloads_directory, '{}.cauldron'.format(count))


def clean_path(project_title: str, path: str) -> str:
    cleaned = environ.paths.clean(path)

    if os.path.isdir(cleaned):
        return os.path.join(cleaned, '{}.cauldron'.format(project_title))

    if not cleaned.endswith('.cauldron'):
        return '{}.cauldron'.format(cleaned)

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


def make_directory(path: str):
    """ """

    save_directory = os.path.dirname(path)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)


def write_file(project: 'projects.Project', path: str) -> str:
    """

    :param project:
    :param path:
    :return:
    """

    save_path = path if path else get_default_path()
    save_path = clean_path(project.title, save_path)
    make_directory(save_path)

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


def execute_remote(context: cli.CommandContext, path: str = None) -> Response:
    """ """

    thread = sync.send_remote_command(
        command='save',
        remote_connection=context.remote_connection,
        show_logs=False,
        asynchronous=False
    )
    thread.join()
    save_response = thread.responses[-1]

    if save_response.failed:
        save_response.log_notifications()
        return context.response.consume(save_response)

    filename = os.path.basename(save_response.data.get('path'))
    project_title = save_response.data.get('project_title', 'Project')

    save_path = clean_path(
        project_title,
        path if path else get_default_path()
    )
    make_directory(save_path)

    download_response = sync.comm.download_file(
        filename=filename,
        save_path=save_path,
        remote_connection=context.remote_connection
    )

    if download_response.success:
        download_response.notify(
            kind='SAVED',
            code='DOWNLOAD_SAVED',
            message='Project has been saved to: {}'.format(save_path)
        )

    return context.response.consume(download_response)


def execute(context: cli.CommandContext, path: str = None) -> Response:
    response = context.response
    project = cauldron.project.internal_project

    if not project:
        return response.fail(
            code='NO_PROJECT',
            message='No project is open. Nothing to save'
        ).console(
            whitespace=1
        ).response

    try:
        saved_path = write_file(project, path)
    except Exception as error:
        return response.fail(
            code='WRITE_SAVE_ERROR',
            message='Unable to write the Cauldron file output',
            error=error
        ).console(
            whitespace=1
        ).response

    return response.update(
        path=saved_path,
        project_title=project.title
    ).notify(
        kind='SUCCESS',
        code='SAVED',
        message='The project has been saved to: {}'.format(saved_path)
    ).console(
        whitespace=1
    ).response
