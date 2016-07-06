import logging
import os
import sys

import flask
from flask import Flask
from flask import request

MY_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
sys.path.append(
    os.path.abspath(os.path.join(MY_DIRECTORY, '..'))
)

import cauldron
from cauldron.cli import commander
from cauldron.environ.response import Response
from cauldron.environ import logger
from cauldron import environ

APPLICATION = Flask('Cauldron')
SERVER_VERSION = [0, 0, 1, 1]

server_data = dict(
    version=SERVER_VERSION
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


@APPLICATION.route('/ping', methods=['GET', 'POST'])
def server_status():
    """

    :return:
    """

    r = Response()
    r.update(
        success=True,
        __server__=get_server_data()
    )

    return flask.jsonify(r.serialize())


@APPLICATION.route('/status', methods=['GET', 'POST'])
def project_status():
    """

    :return:
    """

    r = Response()

    try:
        project = cauldron.project.internal_project
        r.update(
            project=project.status()
        )
    except Exception:
        r.fail()

    r.update(__server__=get_server_data())
    return flask.jsonify(r.serialize())


@APPLICATION.route('/project', methods=['GET', 'POST'])
def project_data():
    """

    :return:
    """

    r = Response()

    try:
        project = cauldron.project.internal_project
        r.update(
            project=project.kernel_serialize()
        )
    except Exception:
        r.fail()

    r.update(__server__=get_server_data())
    return flask.jsonify(r.serialize())


@APPLICATION.route('/', methods=['GET', 'POST'])
def execute():
    """

    :return:
    """

    r = Response()
    r.update(__server__=get_server_data())

    cmd = None
    parts = None
    name = None
    args = None
    request_args = None
    try:
        request_args = request.get_json(silent=True)
        if not request_args:
            request_args = request.values

        cmd = request_args.get('command', '')
        parts = [x.strip() for x in cmd.split(' ', 1)]
        name = parts[0].lower()

        args = request_args.get('args', '')
        if not isinstance(args, str):
            args = ' '.join(args)
        args += ' {}'.format(parts[1] if len(parts) > 1 else '').strip()
    except Exception as err:
        r.fail().notify(
            kind='ERROR',
            code='INVALID_COMMAND',
            message='Unable to parse command'
        ).kernel(
            cmd=cmd if cmd else '',
            parts=parts,
            name=name,
            args=args,
            error=str(err),
            mime_type='{}'.format(request.mimetype),
            request_data='{}'.format(request.data),
            request_args=request_args
        )
        return flask.jsonify(r.serialize())

    try:
        commander.execute(name, args, r)
    except Exception as err:
        r.fail().notify(
            kind='ERROR',
            code='KERNEL_EXECUTION_FAILURE',
            message='Unable to execute command'
        ).kernel(
            cmd=cmd,
            parts=parts,
            name=name,
            args=args,
            error=str(err),
            stack=logger.get_error_stack()
        )

    return flask.jsonify(r.serialize())


def run(port: int = 5010, debug: bool = False):
    """

    :param port:
    :param debug:
    :return:
    """

    server_data['port'] = port
    server_data['debug'] = debug
    server_data['id'] = environ.start_time.isoformat()

    if not debug:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    APPLICATION.run(port=port, debug=debug)
