import typing

import flask
from flask import request

import cauldron
from cauldron import environ
from cauldron.cli import commander
from cauldron.environ.response import Response
from cauldron.runner import redirection
from cauldron.ui import arguments
from cauldron.ui import configs as ui_configs

ParsedCommand = typing.NamedTuple('COMMAND_CONTEXT', [
    ('response', Response),
    ('command', str),
    ('args', list),
])


def parse_command_args() -> environ.Response:
    """
    Parse arguments for command executions.

    :param response:
        The response object to modify with status or error data
    :return:
        A tuple where the first element is the name of the command
        to execute, and the second is a string representing the arguments
        to apply to that command.
    """
    response = environ.Response()
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
        return response.fail(
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
        ).response

    return response.returns(name, args)


def execute(asynchronous: bool = False) -> environ.Response:
    """
    :param asynchronous:
        Whether or not to allow asynchronous command execution that returns
        before the command is complete with a run_uid that can be used to
        track the continued execution of the command until completion.
    """
    r = parse_command_args()
    if r.failed:
        return r

    cmd, args = r.returned

    try:
        r = commander.execute(cmd, args, r)
        if not r.thread:
            return r

        if not asynchronous:
            r.thread.join()

        ui_configs.ACTIVE_EXECUTION_RESPONSE = r

        # Watch the thread for a bit to see if the command finishes in
        # that time. If it does the command result will be returned directly
        # to the caller. Otherwise, a waiting command will be issued
        for _ in range(5):
            r.thread.join(0.25)
            if not r.thread.is_alive():
                break

        if r.thread.is_alive():
            return Response().update(
                run_log=r.get_thread_log(),
                run_status='running',
                run_uid=r.thread.uid,
            )

        ui_configs.ACTIVE_EXECUTION_RESPONSE = None
        return r.update(
            run_log=r.get_thread_log(),
            run_status='complete',
            run_uid=r.thread.uid
        )
    except Exception as error:
        return r.fail(
            code='KERNEL_EXECUTION_FAILURE',
            message='Unable to execute command.',
            cmd=cmd,
            args=args,
            error=error
        ).response


def abort() -> environ.Response:
    response = ui_configs.ACTIVE_EXECUTION_RESPONSE
    ui_configs.ACTIVE_EXECUTION_RESPONSE = None

    should_abort = (
        response is not None
        and response.thread
        and response.thread.is_alive()
    )

    if should_abort:
        # Try to stop the thread gracefully first.
        response.thread.abort = True
        response.thread.join(2)

        try:
            # Force stop the thread explicitly
            if response.thread.is_alive():
                response.thread.abort_running()
        except Exception:
            pass

    project = cauldron.project.get_internal_project()
    if project and project.current_step:
        step = project.current_step
        if step.is_running:
            step.mark_dirty(True)
            step.progress = 0
            step.progress_message = None
            step.dumps(False)
            step.is_running = False

        # Make sure this is called prior to printing response information to
        # the console or that will come along for the ride
        redirection.disable(step)

    # Make sure no print redirection will survive the abort process regardless
    # of whether an active step was found or not (prevents race conditions)
    redirection.restore_default_configuration()

    return environ.Response()
