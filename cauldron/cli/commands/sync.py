import os
import glob

from cauldron import cli
from cauldron.cli import sync
from cauldron import environ
from cauldron.environ import Response

NAME = 'sync'
DESCRIPTION = """
    Synchronizes the remote cauldron connection with the most recent versions
    of the locally stored project files.
    """


def synchronize_file(
        context: 'cli.CommandContext',
        file_path: str,
        relative_path: str,
        file_kind: str = ''
) -> Response:
    """ """

    environ.log('[SYNCING]: {}'.format(relative_path))

    for index, chunk in enumerate(sync.io.read_file_chunks(file_path)):
        response = sync.comm.send_request(
            endpoint='/sync-file',
            remote_connection=context.remote_connection,
            data=dict(
                relative_path=relative_path,
                chunk=chunk,
                type=file_kind,
                index=index
            )
        )

        if response.failed:
            return response

    return Response()


def do_synchronize(
        context: 'cli.CommandContext',
        project_directory: str
) -> Response:
    """ """

    glob_path = os.path.join(project_directory, '**', '*')

    for file_path in glob.iglob(glob_path, recursive=True):
        relative_path = file_path[len(project_directory):].lstrip(os.sep)
        response = synchronize_file(
            context=context,
            file_path=file_path,
            relative_path=relative_path,
            file_kind=''
        )

        if response.failed:
            return response

    return Response()


def execute(context: cli.CommandContext) -> Response:
    """ """

    if not context.remote_connection.active:
        return context.response.fail(
            code='NO_REMOTE_CONNECTION',
            message='No active remote connection is available. Nothing to sync.'
        ).console(
            whitespace=1
        ).response

    response = sync.comm.send_request(
        endpoint='/sync-status',
        method='GET',
        remote_connection=context.remote_connection
    )
    source_directory = response.data.get('remote_source_directory')
    source_path = os.path.join(
        source_directory if source_directory else '',
        'cauldron.json'
    )

    if response.failed or not source_directory:
        response.log_notifications()
        return context.response.consume(response)

    directory_exists = os.path.exists(source_directory)
    definition_exists = os.path.exists(source_path)

    if not directory_exists or not definition_exists:
        return context.response.fail(
            code='NO_PROJECT',
            message='No project exists locally at: {}'.format(source_directory)
        ).console(
            whitespace=1
        ).response

    environ.log_header(
        text='SYNCHRONIZING',
        level=3,
        whitespace=1
    )

    response = do_synchronize(context, source_directory)
    return context.response.consume(response)
