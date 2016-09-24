import cauldron as cd
import flask
from cauldron.cli import commander
from cauldron.cli.server import run as server_run
from cauldron.cli.server.routes import display
from cauldron.cli.server.routes import status
from cauldron.environ import logger
from cauldron.environ.response import Response
from cauldron.session import writing
from flask import request

active_execution_responses = dict()


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
        r.fail(
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
        if not r.thread:
            return flask.jsonify(r.serialize())

        active_execution_responses[r.thread.uid] = r

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
                    step_changes=get_running_step_changes(),
                    __server__=server_run.get_server_data()
                )
                .serialize()
            )

        del active_execution_responses[r.thread.uid]
        r.update(
            run_status='complete',
            run_uid=r.thread.uid
        )
    except Exception as err:
        r.fail(
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


@server_run.APPLICATION.route(
    '/run-status/<uid>',
    methods=['GET', 'POST']
)
def run_status(uid: str):
    """

    :param uid:
    :return:
    """

    try:
        r = active_execution_responses.get(uid)

        if not r:
            return flask.jsonify(
                Response()
                .update(
                    run_active_uids=list(active_execution_responses.keys()),
                    run_status='unknown',
                    run_uid=uid,
                    __server__=server_run.get_server_data()
                )
                .serialize()
            )

        if r.thread.is_alive():
            return flask.jsonify(
                Response()
                .update(
                    run_status='running',
                    run_uid=uid,
                    step_changes=get_running_step_changes(),
                    __server__=server_run.get_server_data()
                )
                .serialize()
            )

        del active_execution_responses[uid]
        r.update(
            run_status='complete',
            run_uid=r.thread.uid
        )
        return flask.jsonify(r.serialize())

    except Exception as err:
        return flask.jsonify(
            Response()
            .fail(
                code='COMMAND_STATUS_FAILURE',
                message='Unable to check command execution status'
            )
            .kernel(
                uid=uid,
                error=str(err),
                stack=logger.get_error_stack()
            )
            .serialize()
        )


@server_run.APPLICATION.route('/abort', methods=['GET', 'POST'])
def abort():

    uids = list(active_execution_responses.keys())

    while len(uids) > 0:
        uid = uids.pop()

        response = active_execution_responses.get(uid)
        if not response:
            continue

        try:
            del active_execution_responses[uid]
        except Exception:
            pass

        if not response.thread or not response.thread.is_alive():
            continue

        # Try to stop the thread gracefully
        response.thread.abort = True
        response.thread.join(1)

        try:
            # Force stop the thread explicitly
            if response.thread.is_alive():
                response.thread._Thread_stop()
        except Exception:
            pass

    project = cd.project.internal_project

    return flask.jsonify(
        Response()
        .update(
            project=project.kernel_serialize()
        )
        .serialize()
    )


def get_running_step_changes() -> list:
    """

    :return:
    """

    project = cd.project.internal_project

    step_changes = []
    for ps in project.steps:
        if ps.is_running:
            step_changes.append(dict(
                name=ps.definition.name,
                action='updated',
                step=writing.write_step(ps)
            ))

    return step_changes
