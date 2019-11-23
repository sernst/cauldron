from cauldron import cli
from cauldron.cli import sync
from cauldron.cli.commands.sync.syncer import do_synchronize
from cauldron.environ.response import Response
from cauldron.session.projects import specio

NAME = 'sync'
DESCRIPTION = """
    Synchronizes the remote cauldron connection with the most recent versions
    of the locally stored project files.
    """


def _on_failure(
        context: cli.CommandContext,
        code: str,
        message: str
) -> Response:
    """Convenience function for handling failures."""
    return (
        context.response
        .fail(code=code, message=message)
        .console(whitespace=1)
        .response
    )


def execute(context: cli.CommandContext) -> Response:
    """Runs the sync command."""
    if not context.remote_connection.active:
        return _on_failure(
            context,
            code='NO_REMOTE_CONNECTION',
            message='No active remote connection. Nothing to sync.'
        )

    status_response = sync.comm.send_request(
        endpoint='/sync-status',
        method='GET',
        remote_connection=context.remote_connection
    )
    source_directory = status_response.data.get('remote_source_directory')

    if status_response.failed or not source_directory:
        status_response.log_notifications()
        return context.response.consume(status_response)

    project_spec = specio.get_project_info(source_directory)
    if project_spec is None:
        return _on_failure(
            context,
            code='NO_PROJECT',
            message='No project exists locally at: {}'.format(source_directory)
        )

    return context.response.consume(do_synchronize(
        context=context,
        source_directory=source_directory,
        newer_than=context.remote_connection.sync_timestamp,
        library_folders=project_spec.get('library_folders', ['libs'])
    ))
