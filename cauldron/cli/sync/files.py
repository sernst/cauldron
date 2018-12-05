import glob
import os
import time
import typing

from cauldron import environ
from cauldron.cli import sync
from cauldron.environ.response import Response


def send_chunk(
        chunk: str,
        index: int,
        offset: int,
        relative_path: str,
        file_kind: str = '',
        remote_connection: 'environ.RemoteConnection' = None,
        sync_time: float = -1
):
    """ """
    return sync.comm.send_request(
        endpoint='/sync-file',
        method='POST',
        remote_connection=remote_connection,
        data=dict(
            relative_path=relative_path,
            chunk=chunk,
            offset=offset,
            type=file_kind,
            index=index,
            sync_time=time.time() if sync_time < 0 else sync_time
        )
    )


def send(
        file_path: str,
        relative_path: str,
        file_kind: str = '',
        chunk_size: int = sync.io.DEFAULT_CHUNK_SIZE,
        remote_connection: 'environ.RemoteConnection' = None,
        newer_than: float = 0,
        progress_callback=None,
        sync_time: float = -1
) -> Response:
    """ """
    response = Response()
    sync_time = time.time() if sync_time < 0 else sync_time
    callback = (
        progress_callback
        if progress_callback else
        (lambda x: x)
    )

    modified_time = os.path.getmtime(file_path)
    if modified_time < newer_than:
        callback(response.notify(
            kind='SKIP',
            code='NOT_MODIFIED',
            message='No changes detected to "{}"'.format(relative_path),
            data=dict(
                file_path=file_path,
                relative_path=relative_path
            )
        ))
        return response

    chunk_count = sync.io.get_file_chunk_count(file_path, chunk_size)
    chunks = sync.io.read_file_chunks(file_path, chunk_size)

    def get_progress(complete_count: int = 0) -> typing.Tuple[int, str]:
        """ """

        if chunk_count < 2:
            return 0, ''

        progress_value = int(100 * complete_count / chunk_count)
        display = '({}%)'.format('{}'.format(progress_value).zfill(3))
        return progress_value, display

    progress_display = get_progress(0)[-1]
    callback(response.notify(
        kind='SYNC',
        code='STARTED',
        message='{} "{}"'.format(progress_display, relative_path),
        data=dict(
            progress=0,
            file_path=file_path,
            relative_path=relative_path
        )
    ))

    offset = 0
    for index, chunk in enumerate(chunks):
        response = send_chunk(
            chunk=chunk,
            index=index,
            offset=offset,
            relative_path=relative_path,
            file_kind=file_kind,
            remote_connection=remote_connection,
            sync_time=sync_time
        )
        offset += len(chunk)

        if response.failed:
            return response

        progress, progress_display = get_progress(index + 1)
        if chunk_count > 1 and (index + 1) < chunk_count:
            callback(response.notify(
                kind='SYNC',
                code='PROGRESS',
                message='{} "{}"'.format(progress_display, relative_path),
                data=dict(
                    progress=0.01 * progress,
                    chunk_count=chunk_count,
                    file_path=file_path,
                    relative_path=relative_path
                )
            ))

    progress, progress_display = get_progress(chunk_count)
    callback(response.notify(
        kind='SYNC',
        code='DONE',
        message='{} "{}"'.format(progress_display, relative_path),
        data=dict(
            chunk_count=chunk_count,
            progress=progress,
            file_path=file_path,
            relative_path=relative_path
        )
    ))

    return response


def send_all_in(
        directory: str,
        relative_root_path: str = None,
        files_kind: str = '',
        chunk_size: int = sync.io.DEFAULT_CHUNK_SIZE,
        recursive: bool = True,
        remote_connection: 'environ.RemoteConnection' = None,
        newer_than: float = 0,
        progress_callback=None,
        sync_time: float = -1
) -> Response:
    """ """
    sync_time = time.time() if sync_time < 0 else sync_time

    glob_end = ('**', '*') if recursive else ('*',)
    glob_path = os.path.join(directory, *glob_end)

    root_path = (
        relative_root_path
        if relative_root_path else
        directory
    ).rstrip(os.path.sep)

    for file_path in glob.iglob(glob_path, recursive=True):
        relative_path = file_path[len(root_path):].lstrip(os.path.sep)

        response = send(
            file_path=file_path,
            relative_path=relative_path,
            file_kind=files_kind,
            chunk_size=chunk_size,
            remote_connection=remote_connection,
            newer_than=newer_than,
            progress_callback=progress_callback,
            sync_time=sync_time
        )

        if response.failed:
            return response

    return Response()
