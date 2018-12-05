import json
import mimetypes
import os
import tempfile

import flask

import cauldron as cd
from cauldron import cli
from cauldron import writer
from cauldron.cli import sync
from cauldron.cli.commands import create as create_command
from cauldron.cli.commands.open import opener as project_opener
from cauldron.cli.server import arguments
from cauldron.cli.server import authorization
from cauldron.cli.server import run as server_runner
from cauldron.cli.server.routes.synchronize import status
from cauldron.environ.response import Response

sync_status = dict(
    time=-1,
    project=None
)


@server_runner.APPLICATION.route('/sync-touch', methods=['GET', 'POST'])
@authorization.gatekeeper
def touch_project():
    """
    Touches the project to trigger refreshing its cauldron.json state.
    """
    r = Response()
    project = cd.project.get_internal_project()

    if project:
        project.refresh()
    else:
        r.fail(
            code='NO_PROJECT',
            message='No open project to refresh'
        )

    return r.update(
        sync_time=sync_status.get('time', 0)
    ).flask_serialize()


@server_runner.APPLICATION.route('/sync-status', methods=['GET', 'POST'])
@authorization.gatekeeper
def fetch_synchronize_status():
    """
    Returns the synchronization status information for the currently opened
    project
    """
    r = Response()
    project = cd.project.get_internal_project()

    if not project:
        r.fail(
            code='NO_PROJECT',
            message='No open project on which to retrieve status'
        )
    else:
        with open(project.source_path, 'r') as f:
            definition = json.load(f)

        result = status.of_project(project)
        r.update(
            sync_time=sync_status.get('time', 0),
            source_directory=project.source_directory,
            remote_source_directory=project.remote_source_directory,
            status=result,
            definition=definition
        )

    return r.flask_serialize()


@server_runner.APPLICATION.route('/sync-open', methods=['POST'])
@authorization.gatekeeper
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

    # Remove any shared library folders from the library list. These will be
    # stored using the single shared library folder instead
    definition['library_folders'] = [
        lf
        for lf in definition.get('library_folders', ['libs'])
        if lf and not lf.startswith('..')
    ]
    definition['library_folders'] += ['../__cauldron_shared_libs']

    container_folder = tempfile.mkdtemp(prefix='cd-remote-project-')
    os.makedirs(os.path.join(container_folder, '__cauldron_shared_libs'))
    os.makedirs(os.path.join(container_folder, '__cauldron_downloads'))

    project_folder = os.path.join(container_folder, definition['name'])
    os.makedirs(project_folder)

    definition_path = os.path.join(project_folder, 'cauldron.json')
    writer.write_json_file(definition_path, definition)

    sync_status.update({}, time=-1, project=None)

    open_response = project_opener.open_project(project_folder, forget=True)
    open_response.join()
    project = cd.project.get_internal_project()
    project.remote_source_directory = source_directory

    sync_status.update({}, time=-1, project=project)

    return r.consume(open_response).update(
        source_directory=project.source_directory,
        project=project.kernel_serialize()
    ).notify(
        kind='OPENED',
        code='PROJECT_OPENED',
        message='Project opened'
    ).response.flask_serialize()


@server_runner.APPLICATION.route('/sync-file', methods=['POST'])
@authorization.gatekeeper
def sync_source_file():
    """ """

    r = Response()
    args = arguments.from_request()
    relative_path = args.get('relative_path')
    chunk = args.get('chunk')
    index = args.get('index', 0)
    sync_time = args.get('sync_time', -1)
    location = args.get('location', 'project')
    offset = args.get('offset', 0)

    if None in [relative_path, chunk]:
        return r.fail(
            code='INVALID_ARGS',
            message='Missing or invalid arguments'
        ).response.flask_serialize()

    project = cd.project.get_internal_project()

    if not project:
        return r.fail(
            code='NO_OPEN_PROJECT',
            message='No project is open. Unable to sync'
        ).response.flask_serialize()

    parts = relative_path.replace('\\', '/').strip('/').split('/')

    root_directory = project.source_directory
    if location == 'shared':
        root_directory = os.path.realpath(os.path.join(
            root_directory,
            '..',
            '__cauldron_shared_libs'
        ))

    file_path = os.path.join(root_directory, *parts)
    parent_directory = os.path.dirname(file_path)

    if not os.path.exists(parent_directory):
        os.makedirs(parent_directory)

    sync.io.write_file_chunk(
        file_path=file_path,
        packed_chunk=chunk,
        append=index > 0,
        offset=offset
    )

    sync_status.update({}, time=sync_time)

    return r.notify(
        kind='SYNCED',
        code='SAVED_CHUNK',
        message='File chunk {} {}'.format(offset, file_path)
    ).console().response.flask_serialize()


@server_runner.APPLICATION.route(
    '/download/<filename>',
    methods=['GET', 'POST']
)
@authorization.gatekeeper
def download_file(filename: str):
    """ downloads the specified project file if it exists """

    project = cd.project.get_internal_project()
    source_directory = project.source_directory if project else None

    if not filename or not project or not source_directory:
        return '', 204

    path = os.path.realpath(os.path.join(
        source_directory,
        '..',
        '__cauldron_downloads',
        filename
    ))

    if not os.path.exists(path):
        return '', 204

    return flask.send_file(path, mimetype=mimetypes.guess_type(path)[0])


@server_runner.APPLICATION.route(
    '/project-download/<path:filename>',
    methods=['GET', 'POST']
)
@authorization.gatekeeper
def download_project_file(filename: str):
    """ downloads the specified project file if it exists """

    project = cd.project.get_internal_project()
    source_directory = project.source_directory if project else None

    if not filename or not project or not source_directory:
        return '', 204

    path = os.path.realpath(os.path.join(
        source_directory,
        filename
    ))

    if not os.path.exists(path):
        return '', 204

    return flask.send_file(path, mimetype=mimetypes.guess_type(path)[0])


@server_runner.APPLICATION.route('/sync-create', methods=['POST'])
@authorization.gatekeeper
def sync_create_project():
    """ """

    r = Response()
    args = arguments.from_request()

    name = args.get('name')
    remote_source_directory = args.get('source_directory')
    optional_args = args.get('args', {})

    if None in [name, remote_source_directory]:
        return r.fail(
            code='INVALID_ARGS',
            message='Invalid arguments. Unable to create project'
        ).response.flask_serialize()

    container_folder = tempfile.mkdtemp(prefix='cd-remote-project-')
    os.makedirs(os.path.join(container_folder, '__cauldron_shared_libs'))
    os.makedirs(os.path.join(container_folder, '__cauldron_downloads'))

    r.consume(create_command.execute(
        cli.make_command_context('create'),
        project_name=name,
        directory=container_folder,
        forget=True,
        **optional_args
    ))
    if r.failed:
        return r.flask_serialize()

    sync_status.update({}, time=-1, project=None)

    project = cd.project.get_internal_project()
    project.remote_source_directory = remote_source_directory

    with open(project.source_path, 'r') as f:
        definition = json.load(f)

    sync_status.update({}, time=-1, project=project)

    return r.update(
        source_directory=project.source_directory,
        remote_source_directory=remote_source_directory,
        definition=definition,
        project=project.kernel_serialize()
    ).notify(
        kind='SUCCESS',
        code='PROJECT_CREATED',
        message='Project created'
    ).response.flask_serialize()
