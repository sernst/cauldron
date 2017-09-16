import os


def join(*args: str) -> str:
    """ Creates an absolute and cleaned path from the arguments """

    return clean(os.path.join(*args))


def clean(path: str) -> str:
    """
    Cleans the specified path by expanding shorthand elements, redirecting to
    the real path for symbolic links, and removing any relative components to
    return a complete, absolute path to the specified location.

    :param path:
        The source path to be cleaned
    """

    if not path or path == '.':
        path = os.curdir

    if path.startswith('~'):
        path = os.path.expanduser(path)

    return os.path.realpath(os.path.abspath(path))


def package(*args: str) -> str:
    """
    Creates an absolute path to a file or folder within the cauldron package
    using the relative path elements specified by the args.

    :param args:
        Zero or more relative path elements that describe a file or folder
        within the reporting
    """

    return clean(os.path.join(os.path.dirname(__file__), '..', *args))


def resources(*args: str) -> str:
    """
    Creates an absolute path from the specified relative components within the
    package resources directory.

    :param args:
        Relative components of the path relative to the root package
    :return:
        The absolute path
    """

    return package('resources', *args)


def user(*args: str) -> str:
    """
    Creates an absolute path from the specified relative components within the
    user's Cauldron app data folder.

    :param args:
        Relative components of the path relative to the root package
    :return:
        The absolute path
    """

    return clean(os.path.join('~', '.cauldron', *args))


def results(*args: str) -> str:
    """
    Creates an absolute path from the specified relative components within the
    user's Cauldron app data folder.

    :param args:
        Relative components of the path relative to the root package
    :return:
        The absolute path
    """

    return user('results', *args)
