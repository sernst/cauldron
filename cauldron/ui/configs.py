import os
import typing
from cauldron import environ

DEFAULT_PORT = 8899

LAUNCH_THREAD = None

ACTIVE_EXECUTION_RESPONSE = None  # type: typing.Optional[environ.Response]

#: The root URL prefix for the UI
ROOT_PREFIX = '/v1'

#: UI Version
UI_VERSION = [0, 0, 1, 1]

UI_APP_DATA = dict(
    version=UI_VERSION,
    user=os.environ.get('USER'),
    test=1,
    pid=os.getpid()
)


def is_active_async() -> bool:
    """
    Determines whether or not an async command execution is currently
    underway within the UI execution environment.
    """
    r = ACTIVE_EXECUTION_RESPONSE
    return r is not None and r.thread and r.thread.is_alive()
