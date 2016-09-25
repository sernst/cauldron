import threading
import typing
from collections import namedtuple
from datetime import datetime
from datetime import timedelta

from cauldron.cli.threads import CauldronThread
from cauldron.environ import paths
from cauldron.environ import systems
from cauldron.environ.configuration import Configuration
from cauldron.environ.logger import blanks as log_blanks
from cauldron.environ.logger import header as log_header
from cauldron.environ.logger import log
from cauldron.environ.logger import raw as log_raw
from cauldron.environ.response import Response

VersionInfo = namedtuple('VersionInfo', ['major', 'minor', 'micro'])

start_time = datetime.utcnow()

configs = Configuration()

package_settings = systems.get_package_data()

version = package_settings.get('version', '0.0.0')

version_info = VersionInfo(*[int(x) for x in version.split('.')])


def run_time() -> typing.Union[None, timedelta]:
    """

    :return:
    """

    if not start_time:
        return None

    return datetime.utcnow() - start_time


def abort_thread():
    """
    This function checks to see if the user has indicated that they want the
    currently running execution to stop prematurely by marking the running
    thread as aborted. It only applies to operations that are run within
    CauldronThreads and not the main thread.

    :return:
    """

    thread = threading.current_thread()

    if not isinstance(thread, CauldronThread):
        return

    if thread.abort:
        raise RuntimeError('User Aborted Execution')

