import json
import os
import shutil
import site
import sys
import time
import typing

from cauldron.environ import paths
from cauldron.environ.logger import log


def get_site_packages() -> list:
    try:
        return list(site.getsitepackages())
    except Exception:
        return []


def simplify_path(path: str, path_prefixes: list = None) -> str:
    """
    Simplifies package paths by replacing path prefixes with values specified
    in the replacements list

    :param path:
    :param path_prefixes:
    :return:
    """

    test_path = '{}'.format(path if path else '')
    replacements = (path_prefixes if path_prefixes else []).copy()
    replacements.append(('~', os.path.expanduser('~')))

    for key, value in replacements:
        if test_path.startswith(value):
            return '{}{}'.format(key, test_path[len(value):])

    return test_path


def module_to_package_data(
        name: str,
        entry,
        path_prefixes: list = None
) -> typing.Union[dict, None]:
    """
    Converts a module entry into a package data dictionary with information
    about the module. including version and location on disk

    :param name:
    :param entry:
    :param path_prefixes:
    :return:
    """

    if name.find('.') > -1:
        # Not interested in sub-packages, only root ones
        return None

    version = getattr(entry, '__version__', None)
    version = version if not hasattr(version, 'version') else version.version
    location = getattr(entry, '__file__', sys.exec_prefix)

    if version is None or location.startswith(sys.exec_prefix):
        # Not interested in core packages. They obviously are standard and
        # don't need to be included in an output.
        return None

    return dict(
        name=name,
        version=version,
        location=simplify_path(location, path_prefixes)
    )


def get_system_data() -> typing.Union[None, dict]:
    """
    Returns information about the system in which Cauldron is running.
    If the information cannot be found, None is returned instead.

    :return:
        Dictionary containing information about the Cauldron system, whic
        includes:
         * name
         * location
         * version
    """

    site_packages = get_site_packages()
    path_prefixes = [('[SP]', p) for p in site_packages]
    path_prefixes.append(('[CORE]', sys.exec_prefix))

    packages = [
        module_to_package_data(name, entry, path_prefixes)
        for name, entry in list(sys.modules.items())
    ]

    python_data = dict(
        version=list(sys.version_info),
        executable=simplify_path(sys.executable),
        directory=simplify_path(sys.exec_prefix),
        site_packages=[simplify_path(sp) for sp in site_packages]
    )

    return dict(
        python=python_data,
        packages=[p for p in packages if p is not None]
    )


def get_package_data() -> dict:
    """
    Retrieves the package information for the Cauldron installation

    :return:
        A dictionary with package information such as version
    """

    with open(paths.package('settings.json'), 'r') as f:
        return json.load(f)


def remove(path: str, max_retries: int = 3) -> bool:
    """
    Removes the specified path from the local filesystem if it exists.
    Directories will be removed along with all files and folders within
    them as well as files.

    :param path:
        The location of the file or folder to remove.
    :param max_retries:
        The number of times to retry before giving up.
    :return:
        A boolean indicating whether or not the removal was successful.
    """
    if not path:
        return False

    if not os.path.exists(path):
        return True

    remover = os.remove if os.path.isfile(path) else shutil.rmtree

    for attempt in range(max_retries):
        try:
            remover(path)
            return True
        except Exception:
            # Pause briefly in case there's a race condition on lock
            # for the target.
            time.sleep(0.02)

    return False


def end(code: int):
    """
    Ends the application with the specified error code, adding whitespace to
    the end of the console log output for clarity

    :param code:
        The integer status code to apply on exit. If the value is non-zero,
        indicating an error, a message will be printed to the console to
        inform the user that the application exited in error
    """

    print('\n')
    if code != 0:
        log('Failed with status code: {}'.format(code), whitespace=1)
    sys.exit(code)
