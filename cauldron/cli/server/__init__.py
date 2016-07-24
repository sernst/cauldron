import flask
from cauldron.cli import commander
from cauldron.cli.server import run as server_run
from cauldron.cli.server.routes import display
from cauldron.cli.server.routes import status
from cauldron.environ import logger
from cauldron.environ.response import Response
from flask import request


@server_run.APPLICATION.route('/', methods=['GET', 'POST'])
def execute():
    """

    :return:
    """

    r = Response()
    r.update(__server__=server_run.get_server_data())

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

