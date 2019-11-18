import functools
import typing

from cauldron import cli
from cauldron import environ
from cauldron.cli import sync
from cauldron.environ.response import Response
from cauldron.environ.response import ResponseMessage


def _on_progress(
    message: ResponseMessage,
    synchronized: typing.List[environ.response.ResponseMessage],
):
    if message.kind == 'SKIP':
        return

    if len(synchronized) < 1:
        environ.log_header(
            text='SYNCHRONIZING',
            level=2,
            whitespace=1
        )

    if message.code == 'STARTED':
        synchronized.append(message)

    chunk_count = message.data.get('chunk_count', 0)
    if message.code == 'DONE' and chunk_count < 2:
        return

    message.console()


def do_synchronize(
        context: cli.CommandContext,
        source_directory: str,
        newer_than: float,
        library_folders: typing.List[str] = None,
) -> Response:
    """..."""
    context.remote_connection.sync_starting()

    synchronized = []
    sync_directory = functools.partial(
        sync.files.send_all_in,
        project_directory=source_directory,
        remote_connection=context.remote_connection,
        newer_than=newer_than,
        progress_callback=functools.partial(
            _on_progress,
            synchronized=synchronized
        ),
        sync_time=context.remote_connection.sync_timestamp
    )

    directories_to_sync = ['.'] + (library_folders or [])
    for directory in directories_to_sync:
        context.response.consume(sync_directory(
            relative_directory=directory
        ))
        if context.response.failed:
            break

    context.response.update(synchronized_count=len(synchronized))

    if context.response.failed or len(synchronized) < 1:
        context.remote_connection.sync_ending()
        return context.response

    touch_response = sync.comm.send_request(
        endpoint='/sync-touch',
        method='GET',
        remote_connection=context.remote_connection,
    )
    context.response.consume(touch_response)

    if not context.response.failed:
        environ.log('Synchronization Complete', whitespace=1)

    context.remote_connection.sync_ending()
    return context.response
