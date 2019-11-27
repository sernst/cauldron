import functools
import typing

from cauldron import environ
from cauldron.cli import sync


def _on_progress(
    message: environ.response.ResponseMessage,
    synchronized: typing.List[environ.response.ResponseMessage],
):
    if message.kind == 'SKIP':
        return

    if message.code == 'STARTED':
        synchronized.append(message)

    chunk_count = message.data.get('chunk_count', 0)
    if message.code == 'DONE' and chunk_count < 2:
        return

    message.console()


def do_synchronize(
        source_directory: str,
        newer_than: float,
        library_folders: typing.List[str] = None,
        remote_connection: environ.RemoteConnection = None,
) -> environ.Response:
    """..."""
    response = environ.Response()
    remote_connection = remote_connection or environ.remote_connection
    remote_connection.sync_starting()

    environ.log_header(
        text='SYNCHRONIZING',
        level=2,
        whitespace=1
    )

    synchronized = []
    sync_directory = functools.partial(
        sync.files.send_all_in,
        project_directory=source_directory,
        remote_connection=remote_connection,
        newer_than=newer_than,
        progress_callback=functools.partial(
            _on_progress,
            synchronized=synchronized
        ),
        sync_time=remote_connection.sync_timestamp
    )

    # Sync the project directory and any directories not within
    # the project directory.
    directories_to_sync = (
        [source_directory]
        + [f for f in (library_folders or []) if f.startswith('..')]
    )
    for directory in directories_to_sync:
        environ.log(
            'Synchronizing within {}'.format(directory),
            whitespace_top=1,
        )
        response.consume(sync_directory(relative_directory=directory))

        if response.failed:
            remote_connection.sync_ending()
            return response.update(synchronized_count=len(synchronized))

    if len(synchronized) < 1:
        remote_connection.sync_ending()
        return response.update(synchronized_count=0).notify(
            kind='DONE',
            code='NOTHING_SYNCHRONIZED',
            message='No files needed to be synchronized.'
        ).response

    response.update(synchronized_count=len(synchronized)).notify(
        kind='SENT',
        message='Synchronized {} files.'.format(len(synchronized))
    ).console(whitespace_top=1)

    environ.log('[TOUCH]: Reloading remote changes.')
    touch_response = sync.comm.send_request(
        endpoint='/sync-touch',
        method='GET',
        remote_connection=remote_connection,
    )
    response.consume(touch_response)

    remote_connection.sync_ending()
    return response.notify(
        kind='DONE',
        code='SYNC_COMPLETED',
        message='Synchronization Complete',
    ).console(whitespace=1).response
