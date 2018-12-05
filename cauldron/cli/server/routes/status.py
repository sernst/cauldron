import flask

import cauldron
from cauldron.cli.server import authorization
from cauldron.cli.server import run as server_runner
from cauldron.environ.response import Response


@server_runner.APPLICATION.route('/ping', methods=['GET', 'POST'])
@authorization.gatekeeper
def server_status():
    """

    :return:
    """

    r = Response()
    r.update(
        success=True,
        server=server_runner.get_server_data()
    ).notify(
        kind='CONNECTED',
        code='RECEIVED_PING',
        message='Established remote connection'
    ).console(whitespace=1)

    return flask.jsonify(r.serialize())


@server_runner.APPLICATION.route('/status', methods=['GET', 'POST'])
@authorization.gatekeeper
def project_status():
    """..."""
    r = Response()

    try:
        project = cauldron.project.get_internal_project()
        if project:
            r.update(project=project.status())
        else:
            r.update(project=None)
    except Exception as err:
        r.fail(
            code='PROJECT_STATUS_ERROR',
            message='Unable to check status of currently opened project',
            error=err
        )

    r.update(server=server_runner.get_server_data())
    return flask.jsonify(r.serialize())


@server_runner.APPLICATION.route(
    '/clean-step/<step_name>',
    methods=['GET', 'POST']
)
@authorization.gatekeeper
def clean_step(step_name: str):
    """..."""
    r = Response()
    project = cauldron.project.get_internal_project()

    if not project:
        return flask.jsonify(r.fail(
            code='PROJECT_FETCH_ERROR',
            message='No project is currently open'
        ).response.serialize())

    step = project.get_step(step_name)

    if not step:
        return flask.jsonify(r.fail(
            code='STEP_FETCH_ERROR',
            message='No such step "{}" found'.format(step_name)
        ).response.serialize())

    step.mark_dirty(False, force=True)

    return flask.jsonify(r.update(
        project=project.kernel_serialize()
    ).response.serialize())


@server_runner.APPLICATION.route('/project', methods=['GET', 'POST'])
@authorization.gatekeeper
def project_data():
    """

    :return:
    """

    r = Response()

    try:
        project = cauldron.project.get_internal_project()
        if project:
            r.update(project=project.kernel_serialize())
        else:
            r.update(project=None)
    except Exception as err:
        r.fail(
            code='PROJECT_FETCH_ERROR',
            message='Unable to check status of currently opened project',
            error=err
        )

    r.update(server=server_runner.get_server_data())
    return flask.jsonify(r.serialize())


@server_runner.APPLICATION.route(
    '/run-status/<uid>',
    methods=['GET', 'POST']
)
@authorization.gatekeeper
def run_status(uid: str):
    """

    :param uid:
    :return:
    """

    try:
        r = server_runner.active_execution_responses.get(uid)

        if not r:
            return flask.jsonify(
                Response().update(
                    run_log=[],
                    run_active_uids=list(
                        server_runner.active_execution_responses.keys()
                    ),
                    run_status='unknown',
                    run_multiple_updates=True,
                    run_uid=uid,
                    server=server_runner.get_server_data()
                ).serialize()
            )

        if r.thread.is_running:
            try:
                step_changes = server_runner.get_running_step_changes(True)
            except Exception:
                step_changes = None

            return flask.jsonify(
                Response()
                .update(
                    run_log=r.get_thread_log(),
                    run_status='running',
                    run_multiple_updates=True,
                    run_uid=uid,
                    step_changes=step_changes,
                    server=server_runner.get_server_data()
                ).serialize()
            )

        del server_runner.active_execution_responses[uid]

        return flask.jsonify(
            r.update(
                run_log=r.get_thread_log(),
                run_status='complete',
                run_multiple_updates=True,
                run_uid=r.thread.uid
            ).serialize()
        )

    except Exception as err:
        return flask.jsonify(
            Response().fail(
                code='COMMAND_RUN_STATUS_FAILURE',
                message='Unable to check command execution status',
                error=err,
                run_uid=uid
            ).response.serialize()
        )
