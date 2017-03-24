import json
import os
import tempfile

from flask import request

import cauldron as cd
from cauldron.cli import sync
from cauldron.cli.commands.open import opener as project_opener
from cauldron.cli.server import arguments
from cauldron.cli.server import run as server_runner
from cauldron.cli.server.routes.synchronize import status
from cauldron.environ.response import Response


@server_runner.APPLICATION.route('/sync-status', methods=['GET', 'POST'])
def fetch_synchronize_status():
    """
    Returns the synchronization status information for the currently opened
    project
    """

    r = Response()
    project = cd.project.internal_project

    if not project:
        r.fail(
            code='NO_PROJECT',
            message='No open project on which to retrieve status'
        )
    else:
        result = status.of_project(project)
        r.update(
            source_directory=project.source_directory,
            remote_source_directory=project.remote_source_directory,
            status=result
        )

    return r.flask_serialize()


@server_runner.APPLICATION.route('/sync-open', methods=['POST'])
def sync_open_project():
    """ """

    r = Response()
    args = arguments.from_request()
    definition = args.get('definition')
    source_directory = args.get('source_directory')

    if None in [definition, source_directory]:
        return r.fail(
            code='INVALID_ARGS',
            message='Invalid arguments. Unable to open project'
        ).response.flask_serialize()

    def remove_value(key: str):
        try:
            del definition[key]
        except KeyError:
            pass

    # Remove these values as libraries will be stored in the default directory
    remove_value('library_folders')
    remove_value('asset_folders')

    project_folder = tempfile.mkdtemp(prefix='cd-remote-project-')
    definition_path = os.path.join(project_folder, 'cauldron.json')
    with open(definition_path, 'w') as f:
        json.dump(definition, f)

    open_response = project_opener.open_project(project_folder)
    project = cd.project.internal_project
    project.remote_source_directory = source_directory

    return r.consume(open_response).update(
        source_directory=project.source_directory
    ).notify(
        kind='SUCCESS',
        code='PROJECT_OPENED',
        message='Project opened'
    ).response.flask_serialize()


@server_runner.APPLICATION.route('/sync-file', methods=['POST'])
def sync_source_file():
    """ """

    r = Response()
    args = request.get_json(silent=True)
    relative_path = args.get('relative_path')
    chunk = args.get('chunk')
    file_type = args.get('type')
    index = args.get('index', 0)

    if None in [relative_path, chunk]:
        return r.fail(
            code='INVALID_ARGS',
            message='Missing or invalid arguments'
        ).response.flask_serialize()

    project = cd.project.internal_project

    parts = relative_path.replace('\\', '/').strip('/').split('/')

    if file_type == 'lib':
        root_directory = project.library_directories[0]
    elif file_type == 'asset':
        root_directory = project.asset_directories[0]
    else:
        root_directory = project.source_directory

    file_path = os.path.join(root_directory, *parts)
    parent_directory = os.path.dirname(file_path)

    if not os.path.exists(parent_directory):
        os.makedirs(parent_directory)

    sync.io.write_file_chunk(file_path, chunk, append=index > 0)

    return r.notify(
        kind='SUCCESS',
        code='SAVED_CHUNK',
        message='Saved file chunk'
    ).response.flask_serialize()
