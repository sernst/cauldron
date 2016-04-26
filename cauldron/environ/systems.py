import os
import shutil
import sys

from cauldron.environ.logger import log


def remove(path: str):
    """

    :param path:
    :return:
    """

    if not os.path.exists(path):
        return True

    if os.path.isfile(path):
        try:
            os.remove(path)
        except Exception:
            try:
                os.remove(path)
            except Exception:
                return False
        return True

    try:
        shutil.rmtree(path)
    except Exception:
        try:
            shutil.rmtree(path)
        except Exception:
            return False
    return True


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
