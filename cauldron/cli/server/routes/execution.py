import typing

import cauldron as cd
import flask
from cauldron.cli import commander
from cauldron.cli.server import run as server_runner
from cauldron.environ.response import Response
from flask import request


@server_runner.APPLICATION.route('/', methods=['GET', 'POST'])
def execute_deprecated_route():
    """
    This exists for backward compatibility. It has been replaced
    by explicit async and sync routes for more flexibility and
    control.

    :return:
    """

    return execute(True)


@server_runner.APPLICATION.route('/command-sync', methods=['POST'])
def execute_sync():
    """
    Execution method for synchronous commands. Command thread
    blocks until it is complete to prevent returning any
    intermediately running states

    :return:
    """

    return execute(False)


@server_runner.APPLICATION.route('/command-async', methods=['POST'])
def execute_async():
    """
    Execution method for synchronous commands. Command threads
    are added to the background stack with a unique run uid
    so that they can be polled later for status changes. The
    async method returns a response containing that uid if the
    command execution doesn't end quickly.

    :return:
    """

    return execute(True)


def parse_command_args(response: 'Response') -> typing.Tuple[str, str]:
    """

    :param response:
        The response object to modify with status or error data
    :return:
        A tuple where the first element if the name of the command
        to execute, and the second is a string representing the arguments
        to apply to that command.
    """

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


def execute(async: bool = False):
    """
    :param async:
        Whether or not to allow asynchronous command execution that returns
        before the command is complete with a run_uid that can be used to
        track the continued execution of the command until completion.
    :return:
    """

    r = Response()
    r.update(server=server_runner.get_server_data())

    cmd, args = parse_command_args(r)
    if r.failed:
        return flask.jsonify(r.serialize())

    try:
        commander.execute(cmd, args, r)
        if not r.thread:
            return flask.jsonify(r.serialize())

        if not async:
            r.thread.join()

        server_runner.active_execution_responses[r.thread.uid] = r

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
                    run_status='running',
                    run_uid=r.thread.uid,
                    step_changes=server_runner.get_running_step_changes(True),
                    server=server_runner.get_server_data()
                )
                .serialize()
            )

        del server_runner.active_execution_responses[r.thread.uid]
        r.update(
            run_status='complete',
            run_multiple_updates=False,
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

    return flask.jsonify(r.serialize())


@server_runner.APPLICATION.route('/abort', methods=['GET', 'POST'])
def abort():
    """

    :return:
    """

    uid_list = list(server_runner.active_execution_responses.keys())

    while len(uid_list) > 0:
        uid = uid_list.pop()

        response = server_runner.active_execution_responses.get(uid)
        if not response:
            continue

        try:
            del server_runner.active_execution_responses[uid]
        except Exception:
            pass

        if not response.thread or not response.thread.is_alive():
            continue

        # Try to stop the thread gracefully
        response.thread.abort = True
        response.thread.join(2)

        try:
            # Force stop the thread explicitly
            if response.thread.is_alive():
                response.thread._Thread_stop()
        except Exception:
            pass

    project = cd.project.internal_project
    project_data = project.kernel_serialize() if project else None

    return flask.jsonify(
        Response()
        .update(project=project_data)
        .serialize()
    )


@server_runner.APPLICATION.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    """

    :return:
    """

    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return flask.jsonify(
            Response().fail(
                code='NOT_RUNNING_ERROR',
                message='Unable to shutdown server'
            )
        )

    try:
        func()
    except Exception as err:
        return flask.jsonify(
            Response().fail(
                code='SHUTDOWN_ERROR',
                message='Unable to shutdown server',
                error=err
            )
        )

    return flask.jsonify(Response())
