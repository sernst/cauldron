import cauldron
from cauldron.cli.server import run as server_run
from cauldron.environ.response import Response
import flask


@server_run.APPLICATION.route('/ping', methods=['GET', 'POST'])
def server_status():
    """

    :return:
    """

    r = Response()
    r.update(
        success=True,
        __server__=server_run.get_server_data()
    )

    return flask.jsonify(r.serialize())


@server_run.APPLICATION.route('/status', methods=['GET', 'POST'])
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
            error=str(err)
        )

    r.update(__server__=server_run.get_server_data())
    return flask.jsonify(r.serialize())


@server_run.APPLICATION.route('/project', methods=['GET', 'POST'])
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
            error=str(err)
        )

    r.update(__server__=server_run.get_server_data())
    return flask.jsonify(r.serialize())


