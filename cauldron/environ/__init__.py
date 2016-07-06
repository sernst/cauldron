import typing
from datetime import datetime
from datetime import timedelta

from cauldron.environ import paths
from cauldron.environ import systems
from cauldron.environ.configuration import Configuration
from cauldron.environ.logger import header as log_header
from cauldron.environ.logger import blanks as log_blanks
from cauldron.environ.logger import raw as log_raw
from cauldron.environ.logger import log
from cauldron.environ.response import Response


start_time = datetime.utcnow()

output = Response()  # type: Response

configs = Configuration()


def run_time() -> typing.Union[None, timedelta]:
    """

    :return:
    """

    if not start_time:
        return None

    return datetime.utcnow() - start_time


