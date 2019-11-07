import typing

import flask
from flask import request

from cauldron.cli import commander
from cauldron.environ.response import Response
from cauldron.ui import arguments
from cauldron.ui import configs as ui_configs

ParsedCommand = typing.NamedTuple('COMMAND_CONTEXT', [
    ('response', Response),
    ('command', str),
    ('args', list),
])


def parse_command_args(response: 'Response') -> typing.Tuple[str, str]:
    """

    :param response:
        The response object to modify with status or error data
    :return:
        A tuple where the first element is the name of the command
        to execute, and the second is a string representing the arguments
        to apply to that command.
    """
    cmd = None
    parts = None
    name = None
    args = None
    request_args = arguments.from_request()

    try:
        cmd = request_args.get('command', '')
        parts = [x.strip() for x in cmd.split(' ', 1)]
        name = parts[0].lower()

        args = request_args.get('args', '')
        if not isinstance(args, str):
            args = ' '.join(args)
        args += ' {}'.format(parts[1] if len(parts) > 1 else '').strip()
    except Exception as err:
        response.fail(
            code='INVALID_COMMAND',
            message='Unable to parse command',
            cmd=cmd if cmd else '',
            parts=parts,
            name=name,
            args=args,
            error=err,
            mime_type='{}'.format(request.mimetype),
            request_data='{}'.format(request.data),
            request_args=request_args
        )

    return name, args


def execute(asynchronous: bool = False, parsed: ParsedCommand = None):
    """
    :param asynchronous:
        Whether or not to allow asynchronous command execution that returns
        before the command is complete with a run_uid that can be used to
        track the continued execution of the command until completion.
    """
    if parsed:
        r = parsed.response
        cmd = parsed.command
        args = parsed.args
    else:
        r = Response()
        cmd, args = parse_command_args(r)

    if r.failed:
        return flask.jsonify(r.serialize())

    try:
        commander.execute(cmd, args, r)
        if not r.thread:
            return flask.jsonify(r.serialize())

        if not asynchronous:
            r.thread.join()

        ui_configs.ACTIVE_EXECUTION_RESPONSES = r

        # Watch the thread for a bit to see if the command finishes in
        # that time. If it does the command result will be returned directly
        # to the caller. Otherwise, a waiting command will be issued
        count = 0
        while count < 5:
            count += 1
            r.thread.join(0.25)
            if not r.thread.is_alive():
                break

        if r.thread.is_alive():
            return flask.jsonify(
                Response()
                .update(
                    run_log=r.get_thread_log(),
                    run_status='running',
                    run_uid=r.thread.uid,
                )
                .serialize()
            )

        ui_configs.ACTIVE_EXECUTION_RESPONSES = None
        r.update(
            run_log=r.get_thread_log(),
            run_status='complete',
            run_uid=r.thread.uid
        )
    except Exception as err:
        r.fail(
            code='KERNEL_EXECUTION_FAILURE',
            message='Unable to execute command',
            cmd=cmd,
            args=args,
            error=err
        )

    return r.flask_serialize()
