from collections import namedtuple
from datetime import datetime
from datetime import timedelta

from cauldron.cli import threads
from cauldron.environ import modes
from cauldron.environ import paths
from cauldron.environ import systems
from cauldron.environ.configuration import Configuration
from cauldron.environ.logger import blanks as log_blanks
from cauldron.environ.logger import header as log_header
from cauldron.environ.logger import log
from cauldron.environ.logger import raw as log_raw
from cauldron.environ.response import Response

VersionInfo = namedtuple('VersionInfo', ['major', 'minor', 'micro'])
RemoteConnection = namedtuple('RemoteConnection', ['active', 'url'])

remote_connection = RemoteConnection(False, None)

start_time = datetime.utcnow()

configs = Configuration()

package_settings = systems.get_package_data()

version = package_settings.get('version', '0.0.0')
notebook_version = package_settings.get('notebookVersion', 'v0')

version_info = VersionInfo(*[int(x) for x in version.split('.')])

abort_thread = threads.abort_thread


def run_time() -> timedelta:
    """

    :return:
    """

    delta = start_time if start_time else datetime.utcnow()
    return datetime.utcnow() - delta
