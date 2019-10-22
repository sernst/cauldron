import os

from cauldron import cli
from cauldron.cli import sync
from cauldron.cli.commands.sync.syncer import do_synchronize
from cauldron.environ.response import Response

NAME = 'sync'
DESCRIPTION = """
    Synchronizes the remote cauldron connection with the most recent versions
    of the locally stored project files.
    """


def execute(context: cli.CommandContext) -> Response:
    """ """
    if not context.remote_connection.active:
        return context.response.fail(
            code='NO_REMOTE_CONNECTION',
            message='No active remote connection is available. Nothing to sync.'
        ).console(
            whitespace=1
        ).response

    status_response = sync.comm.send_request(
        endpoint='/sync-status',
        method='GET',
        remote_connection=context.remote_connection
    )
    source_directory = status_response.data.get('remote_source_directory')
    source_path = os.path.join(
        source_directory if source_directory else '',
        'cauldron.json'
    )

    if status_response.failed or not source_directory:
        status_response.log_notifications()
        return context.response.consume(status_response)

    directory_exists = os.path.exists(source_directory)
    definition_exists = os.path.exists(source_path)

    if not directory_exists or not definition_exists:
        return context.response.fail(
            code='NO_PROJECT',
            message='No project exists locally at: {}'.format(source_directory)
        ).console(
            whitespace=1
        ).response

    sync_response = do_synchronize(
        context=context,
        source_directory=source_directory,
        newer_than=status_response.data.get('sync_time', 0)
    )

    return context.response.consume(sync_response)
