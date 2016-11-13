import os
import shutil
import sys
import json
import site
import threading

from cauldron.environ.logger import log
from cauldron.environ import paths
from cauldron.cli.threads import CauldronThread

try:
    site_packages = list(site.getsitepackages())
except Exception:
    site_packages = []


def get_system_data() -> dict:
    """

    :return:
    """

    home_directory = os.path.expanduser('~')
    path_prefixes = [('[SP]', p) for p in site_packages]
    path_prefixes.append(('[CORE]', sys.exec_prefix))

    def simplify(path: str, replacements: list = None) -> str:
        reps = (replacements if replacements else []).copy()
        reps.append(('~', home_directory))

        if not path or not path.startswith(home_directory):
            return path

        for key, value in reps:
            if path.startswith(value):
                return '{}{}'.format(key, path[len(value):])

        return path

    def module_entry(entry):
        if entry[0].find('.') > -1:
            return None

        mod = entry[-1]
        version = getattr(mod, '__version__', None)

        try:
            version = version.version
        except Exception:
            pass

        location = getattr(mod, '__file__', None)

        if version is None or location is None:
            return None

        location = simplify(location, path_prefixes)

        if location.startswith('[CORE]'):
            return None

        return dict(
            name=entry[0],
            version=version,
            location=location
        )

    packages = [
        x for x in map(module_entry, list(sys.modules.items()))
        if x is not None
    ]

    python_data = dict(
        version=list(sys.version_info),
        executable=simplify(sys.executable),
        directory=simplify(sys.exec_prefix),
        site_packages=[simplify(sp) for sp in site_packages]
    )

    return dict(
        python=python_data,
        packages=packages
    )


def get_package_data() -> dict:
    """
    Retrieves the package information for the Cauldron installation

    :return:
        A dictionary with package information such as version
    """

    with open(paths.package('settings.json'), 'r') as f:
        return json.load(f)


def remove(path: str):
    """

    :param path:
    :return:
    """

    if not path:
        return False

    if not os.path.exists(path):
        return True

    if os.path.isfile(path):
        for attempt in range(3):
            try:
                os.remove(path)
                return True
            except Exception as err:
                pass

        return False

    for attempt in range(3):
        try:
            shutil.rmtree(path)
            return True
        except Exception as err:
            pass

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
