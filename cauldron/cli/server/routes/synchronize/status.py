import os
import glob

from cauldron.session import projects


def of_project(project: 'projects.Project') -> dict:
    """
    Returns the file status information for every file within the project
    source directory and its shared library folders.

    :param project:
        The project for which the status information should be generated
    :return:
        A dictionary containing:
            - project: the status information for all files within
                the projects source directory
            - libraries: a list of status information dictionaries for all
                files within each of the project's library directories. If a
                library resides within the project source directory, the entry
                will be an empty dictionary to prevent duplication.
    """
    source_directory = project.source_directory

    libraries_status = [
        {} if d.startswith(source_directory) else of_directory(d)
        for d in project.library_directories
    ]

    return dict(
        project=of_directory(source_directory),
        libraries=libraries_status
    )


def of_file(path: str, root_directory: str = None) -> dict:
    """
    Returns a dictionary containing status information for the specified file
    including when its name relative to the root directory, when it was last
    modified and its size.

    :param path:
        The absolute path to the file for which the status information should
        be generated
    :param root_directory:
        The directory to use for creating relative path names for the returned
        status. If this argument is None the path in the status will be the
        absolute path argument.
    :return:
        A dictionary containing the status information for the file at the
        specified path. If no such file exists, then the dictionary will
        contain -1 values for both the file size and the last modified time.
    """

    slug = (
        path
        if root_directory is None
        else path[len(root_directory):].lstrip(os.sep)
    )

    if not os.path.exists(path) or os.path.isdir(path):
        return dict(
            size=-1,
            modified=-1,
            path=slug
        )

    size = os.path.getsize(path)
    modified = max(os.path.getmtime(path), os.path.getctime(path))

    return dict(
        modified=modified,
        path=slug,
        size=size
    )


def of_directory(directory: str, root_directory: str = None) -> dict:
    """
    Returns a dictionary containing status entries recursively for all files
    within the specified directory and its descendant directories.

    :param directory:
        The directory in which to retrieve status information
    :param root_directory:
        Directory relative to which all file status paths are related. If this
        argument is None then the directory argument itself will be used.
    :return:
        A dictionary containing status information for each file within the
        specified directory and its descendants. The keys of the dictionary
        are the relative path names for each of the files.
    """

    glob_path = os.path.join(directory, '**/*')
    root = root_directory if root_directory else directory
    results = filter(
        lambda result: (result['modified'] != -1),
        [of_file(path, root) for path in glob.iglob(glob_path, recursive=True)]
    )
    return dict([(result['path'], result) for result in results])
