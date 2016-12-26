import typing
from collections import namedtuple
from datetime import datetime
from datetime import timedelta

from cauldron.environ import paths
from cauldron.environ import systems
from cauldron.cli import threads
from cauldron.environ.configuration import Configuration
from cauldron.environ.logger import blanks as log_blanks
from cauldron.environ.logger import header as log_header
from cauldron.environ import modes
from cauldron.environ.logger import log
from cauldron.environ.logger import raw as log_raw
from cauldron.environ.response import Response

VersionInfo = namedtuple('VersionInfo', ['major', 'minor', 'micro'])

start_time = datetime.utcnow()

configs = Configuration()

package_settings = systems.get_package_data()

version = package_settings.get('version', '0.0.0')

version_info = VersionInfo(*[int(x) for x in version.split('.')])

abort_thread = threads.abort_thread


def run_time() -> typing.Union[None, timedelta]:
    """

    :return:
    """

    if not start_time:
        return None

    return datetime.utcnow() - start_time



