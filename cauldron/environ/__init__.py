import time
import typing
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


class RemoteConnection:
    """Contains remote execution status information."""

    def __init__(self, active: bool = False, url: str = None):
        self.active = active  # type: bool
        self.url = url  # type: typing.Optional[str]
        self.local_project_directory = None  # type: typing.Optional[str]
        self._sync_timestamp = 0  # type: int
        self._sync_active = False  # type: bool

    @property
    def sync_timestamp(self) -> float:
        """Last time the sync action to the remote source started."""
        return max(0, self._sync_timestamp - 2)

    def serialize(self) -> dict:
        return {
            'active': self.active,
            'url': self.url,
            'sync': {
                'timestamp': self._sync_timestamp,
                'active': self._sync_active,
            }
        }

    def sync_starting(self):
        """..."""
        self._sync_active = True
        self._sync_timestamp = time.time()

    def sync_ending(self):
        """..."""
        self._sync_active = False


remote_connection = RemoteConnection()

start_time = datetime.utcnow()

configs = Configuration().put(
    persists=False,
    directory=paths.INITIAL_DIRECTORY,
)

package_settings = systems.get_package_data()

version = package_settings.get('version', '0.0.0')
notebook_version = package_settings.get('notebookVersion', 'v0')

version_info = VersionInfo(*[int(x) for x in version.split('.')])

abort_thread = threads.abort_thread

#: Holds information about open viewer (reader) files
#: and is None when no such file has been opened for
#: viewing.
view = None  # type: typing.Optional[dict]


def run_time() -> timedelta:
    """..."""
    delta = start_time if start_time else datetime.utcnow()
    return datetime.utcnow() - delta
