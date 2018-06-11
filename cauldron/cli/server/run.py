import logging
import os
import site
import sys
from argparse import ArgumentParser

import cauldron as cd
from cauldron.session import writing
from cauldron import environ
from cauldron.render.encoding import ComplexFlaskJsonEncoder
from flask import Flask
import typing

APPLICATION = Flask('Cauldron')
APPLICATION.json_encoder = ComplexFlaskJsonEncoder
SERVER_VERSION = [0, 0, 1, 1]


try:
    site_packages = list(site.getsitepackages())
except Exception:
    site_packages = []

active_execution_responses = dict()  # type: typing.Dict[str, environ.Response]


server_data = dict(
    version=SERVER_VERSION,
    user=os.environ.get('USER'),
    test=1,
    pid=os.getpid()
)

authorization = dict(
    code=''
)


def get_server_data() -> dict:
    """

    :return:
    """

    out = dict(
        uptime=environ.run_time().total_seconds(),
        cauldron_settings=environ.package_settings
    )
    out.update(server_data)
    out.update(environ.systems.get_system_data())
    return out


def get_running_step_changes(write: bool = False) -> list:
    """..."""
    project = cd.project.get_internal_project()

    running_steps = list(filter(
        lambda step: step.is_running,
        project.steps
    ))

    def get_changes(step):
        step_data = writing.step_writer.serialize(step)

        if write:
            writing.save(project, step_data.file_writes)

        return dict(
            name=step.definition.name,
            action='updated',
            step=step_data._asdict(),
            written=write
        )

    return [get_changes(step) for step in running_steps]


def parse(
        args: typing.List[str] = None,
        arg_parser: ArgumentParser = None
) -> dict:
    """Parses the arguments for the cauldron server"""

    parser = arg_parser or create_parser()
    return vars(parser.parse_args(args))


def create_parser(arg_parser: ArgumentParser = None) -> ArgumentParser:
    """
    Creates an argument parser populated with the arg formats for the server
    command.
    """

    parser = arg_parser or ArgumentParser()
    parser.description = 'Cauldron kernel server'

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

    parser.add_argument(
        '-c', '--code',
        dest='authentication_code',
        type=str,
        default=''
    )

    parser.add_argument(
        '-n', '--name',
        dest='host',
        type=str,
        default=None
    )

    return parser


def execute(
        port: int = 5010,
        debug: bool = False,
        public: bool = False,
        host=None,
        authentication_code: str = '',
        **kwargs
):
    """

    :param port:
    :param debug:
    :param public:
    :param host:
    :param authentication_code:
    :return:
    """

    if kwargs.get('version'):
        environ.log('VERSION: {}'.format(environ.version))
        sys.exit(0)

    if host is None and public:
        host = '0.0.0.0'

    server_data['host'] = host
    server_data['port'] = port
    server_data['debug'] = debug
    server_data['id'] = environ.start_time.isoformat()

    authorization['code'] = authentication_code if authentication_code else ''

    if not debug:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    environ.modes.add(environ.modes.INTERACTIVE)
    APPLICATION.run(port=port, debug=debug, host=host)
    environ.modes.remove(environ.modes.INTERACTIVE)
