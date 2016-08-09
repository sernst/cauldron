import logging
import os
import sys
import site
from argparse import ArgumentParser

from cauldron import environ
from cauldron.cli.commands import version
from flask import Flask

APPLICATION = Flask('Cauldron')
SERVER_VERSION = [0, 0, 1, 1]


try:
    site_packages = list(site.getsitepackages())
except Exception:
    site_packages = []

server_data = dict(
    version=SERVER_VERSION,
    user=os.environ.get('USER'),
    python=dict(
        version=list(sys.version_info),
        executable=sys.executable,
        directory=sys.exec_prefix,
        site_packages=[]
    )
)


def get_server_data() -> dict:
    """

    :return:
    """

    out = dict(
        test=1,
        pid=os.getpid(),
        uptime=environ.run_time().total_seconds()
    )
    out.update(server_data)
    return out


def parse(args = None):
    parser = ArgumentParser(
        description='Cauldron server'
    )

    parser.add_argument(
        '-p', '--port',
        dest='port',
        type=int,
        default=5010
    )

    parser.add_argument(
        '-d', '--debug',
        dest='debug',
        default=False,
        action='store_true'
    )

    parser.add_argument(
        '-v', '--version',
        dest='version',
        default=False,
        action='store_true'
    )

    return vars(parser.parse_args(args=args))


def execute(port: int = 5010, debug: bool = False, **kwargs):
    """

    :param port:
    :param debug:
    :return:
    """

    if kwargs.get('version'):
        data = version.get_package_data()
        print('VERSION: {}'.format(data['version']))
        sys.exit(0)

    server_data['port'] = port
    server_data['debug'] = debug
    server_data['id'] = environ.start_time.isoformat()

    if not debug:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    APPLICATION.run(port=port, debug=debug)

