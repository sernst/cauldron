import cauldron
import flask
from cauldron.cli.server import run as server_runner
from cauldron.environ import logger
from cauldron.environ.response import Response


@server_runner.APPLICATION.route('/ping', methods=['GET', 'POST'])
def server_status():
    """

    :return:
    """

    r = Response()
    r.update(
        success=True,
        server=server_runner.get_server_data()
    )

    return flask.jsonify(r.serialize())


@server_runner.APPLICATION.route('/status', methods=['GET', 'POST'])
def project_status():
    """

    :return:
    """

    r = Response()

    try:
        project = cauldron.project.internal_project
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


@server_runner.APPLICATION.route('/project', methods=['GET', 'POST'])
def project_data():
    """

    :return:
    """

    r = Response()

    try:
        project = cauldron.project.internal_project
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
                    run_active_uids=list(
                        server_runner.active_execution_responses.keys()
                    ),
                    run_status='unknown',
                    run_multiple_updates=True,
                    run_uid=uid,
                    server=server_runner.get_server_data()
                ).serialize()
            )

        if r.thread.is_alive():
            return flask.jsonify(
                Response()
                .update(
                    run_status='running',
                    run_multiple_updates=True,
                    run_uid=uid,
                    step_changes=server_runner.get_running_step_changes(True),
                    server=server_runner.get_server_data()
                ).serialize()
            )

        del server_runner.active_execution_responses[uid]
        r.update(
            run_status='complete',
            run_multiple_updates=True,
            run_uid=r.thread.uid
        )
        return flask.jsonify(r.serialize())

    except Exception as err:
        return flask.jsonify(
            Response().fail(
                code='COMMAND_STATUS_FAILURE',
                message='Unable to check command execution status',
                uid=uid,
                error=err
            ).serialize()
        )
