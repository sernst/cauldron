import cauldron as cd
import flask
from cauldron.cli import commander
from cauldron.cli.server import run as server_runner
from cauldron.environ.response import Response
from flask import request


@server_runner.APPLICATION.route('/', methods=['GET', 'POST'])
def execute():
    """

    :return:
    """

    r = Response()
    r.update(server=server_runner.get_server_data())

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
        return flask.jsonify(r.serialize())

    try:
        commander.execute(name, args, r)
        if not r.thread:
            return flask.jsonify(r.serialize())

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
                    step_changes=server_runner.get_running_step_changes(),
                    server=server_runner.get_server_data()
                )
                .serialize()
            )

        del server_runner.active_execution_responses[r.thread.uid]
        r.update(
            run_status='complete',
            run_uid=r.thread.uid
        )
    except Exception as err:
        r.fail(
            code='KERNEL_EXECUTION_FAILURE',
            message='Unable to execute command',
            cmd=cmd,
            parts=parts,
            name=name,
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
        response.thread.join(1)

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
