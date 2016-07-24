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
        r.update(
            project=project.status()
        )
    except Exception:
        r.fail()

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
        r.update(
            project=project.kernel_serialize()
        )
    except Exception:
        r.fail()

    r.update(__server__=server_run.get_server_data())
    return flask.jsonify(r.serialize())
