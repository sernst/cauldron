import os
import shutil
import typing
from collections import namedtuple

from cauldron import environ

FILE_WRITE_ENTRY = namedtuple('FILE_WRITE_ENTRY', ['path', 'contents'])
FILE_COPY_ENTRY = namedtuple('FILE_COY_ENTRY', ['source', 'destination'])


def entry_from_dict(
        data: dict
) -> typing.Union[FILE_WRITE_ENTRY, FILE_COPY_ENTRY]:
    if 'contents' in data:
        return FILE_WRITE_ENTRY(**data)
    return FILE_COPY_ENTRY(**data)


def deploy(files_list: typing.List[tuple]):
    """
    Iterates through the specified files_list and copies or writes each entry depending
    on whether its a file copy entry or a file write entry

    :param files_list:
    :return:
    """

    def deploy_entry(entry):
        if not entry:
            return

        if hasattr(entry, 'source') and hasattr(entry, 'destination'):
            return copy(entry)

        if hasattr(entry, 'path') and hasattr(entry, 'contents'):
            return write(entry)

        raise ValueError('Unrecognized deployment entry {}'.format(entry))

    return [deploy_entry(f) for f in files_list]


def make_output_directory(output_path: str) -> str:
    """
    Creates the parent directory or directories for the specified output path if they
    do not already exist to prevent incomplete directory path errors during copying/writing
    operations

    :param output_path:
        The path of the destination file or directory that will be written
    :return:
        The absolute path to the output directory that was created if missing or already
        existed
    """

    output_directory = os.path.dirname(environ.paths.clean(output_path))

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    return output_directory


def copy(copy_entry: FILE_COPY_ENTRY):
    """
    Copies the specified file from its source location to its destination location

    :param copy_entry:
    :return:
    """

    source_path = environ.paths.clean(copy_entry.source)
    output_path = environ.paths.clean(copy_entry.destination)

    copier = shutil.copy2 if os.path.isfile(source_path) else shutil.copytree

    make_output_directory(output_path)
    copier(source_path, output_path)


def write(write_entry: FILE_WRITE_ENTRY):
    """
    Writes the contents of the specified file entry to its destination path

    :param write_entry:
    :return:
    """

    output_path = environ.paths.clean(write_entry.path)
    make_output_directory(output_path)

    with open(output_path, 'w+') as f:
        f.write(write_entry.contents)
