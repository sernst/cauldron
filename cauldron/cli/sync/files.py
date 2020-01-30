import glob
import os
import time
import typing
import pathlib

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
        sync_time: float = -1,
        location: str = 'project'
):
    """
    Sends a chunk of the specified file to the remote kernel specified
    by the remote_connection argument. The remote kernel that receives
    these responses appends the data to the remote file location as
    successive calls to this function effectively stream the contents
    of the file to the remote system. For small files there will be only
    a single chunk.
    """
    return sync.comm.send_request(
        endpoint='/sync-file',
        method='POST',
        remote_connection=remote_connection,
        timeout=4,
        data=dict(
            relative_path=relative_path,
            chunk=chunk,
            offset=offset,
            type=file_kind,
            index=index,
            sync_time=time.time() if sync_time < 0 else sync_time,
            location=location,
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
        sync_time: float = -1,
        location: str = 'project'
) -> Response:
    """Sends the local file contents to the remote kernel."""
    response = Response()
    sync_time = time.time() if sync_time < 0 else sync_time
    callback = progress_callback or (lambda x: x)

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
        """..."""
        if chunk_count < 2:
            return 0, ''

        progress_value = int(100 * complete_count / chunk_count)
        display = '({}%)'.format('{}'.format(progress_value).ljust(3))
        return progress_value, display

    progress_display = get_progress(0)[-1]
    callback(response.notify(
        kind='SYNC',
        code='STARTED',
        message='{} "{}"'.format(progress_display, relative_path),
        progress=0,
        file_path=file_path,
        relative_path=relative_path,
    ))

    offset = 0
    for index, (chunk, length) in enumerate(chunks):
        response = send_chunk(
            chunk=chunk,
            index=index,
            offset=offset,
            relative_path=relative_path,
            file_kind=file_kind,
            remote_connection=remote_connection,
            sync_time=sync_time,
            location=location,
        )
        offset += length

        if response.failed:
            return response

        progress, progress_display = get_progress(index + 1)
        if chunk_count > 1:
            callback(response.notify(
                kind='SYNC',
                code='PROGRESS' if (index + 1) < chunk_count else 'DONE',
                message='{} -> {} {} "{}"'.format(
                    '+{:,.0f}B'.format(length),
                    '{:,.0f}B'.format(offset),
                    progress_display,
                    relative_path
                ),
                progress=0.01 * progress,
                chunk_count=chunk_count,
                file_path=file_path,
                relative_path=relative_path
            ))

    return response


def send_all_in(
        project_directory: str,
        relative_directory: str = '.',
        files_kind: str = '',
        chunk_size: int = sync.io.DEFAULT_CHUNK_SIZE,
        recursive: bool = True,
        remote_connection: 'environ.RemoteConnection' = None,
        newer_than: float = 0,
        progress_callback=None,
        sync_time: float = -1
) -> Response:
    """..."""
    sync_time = time.time() if sync_time < 0 else sync_time

    project_directory = environ.paths.clean(project_directory)
    root_directory = os.path.realpath(os.path.join(
        project_directory,
        relative_directory
    )).rstrip(os.path.sep)

    glob_end = ('**', '*') if recursive else ('*',)
    glob_path = os.path.join(root_directory, *glob_end)

    # Only send files that have non-zero size that are not cauldron
    # reader files and wheels and ignore hidden files that start with a
    # dot. Also, ignore __pycache__ folders.
    file_paths = (
        p
        for p in glob.iglob(glob_path, recursive=True)
        if os.path.isfile(p)
        and os.path.getsize(p) > 0
        and not p.endswith(('.cauldron', '.whl'))
        and not p.startswith('.')
        and '__pycache__' not in p
    )

    for file_path in file_paths:
        relative_path = file_path[len(root_directory):].strip(os.path.sep)
        within_project = root_directory.startswith(project_directory)
        response = send(
            file_path=file_path,
            relative_path=relative_path,
            file_kind=files_kind,
            chunk_size=chunk_size,
            remote_connection=remote_connection,
            newer_than=newer_than,
            progress_callback=progress_callback,
            sync_time=sync_time,
            location='project' if within_project else 'shared'
        )

        if response.failed:
            return response

    return Response()
