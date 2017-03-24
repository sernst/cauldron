import time
import typing

from cauldron import environ
from cauldron.cli.sync import comm
from cauldron.environ.response import Response


def is_finished(self, responses: typing.List[Response]) -> bool:
    """ """

    has_response = len(responses) > 0
    has_finished_response = has_response and (
        self.responses[-1].failed or
        self.responses[-1].data['run_status'] != 'running'
    )

    return has_finished_response


def check_status(responses, remote_connection) -> Response:
    """ """

    run_uid = responses[-1].data.get('run_uid', '')
    endpoint = '/run-status/{}'.format(run_uid)

    return comm.send_request(
        endpoint=endpoint,
        remote_connection=remote_connection,
        method='GET'
    )


def send_remote_command(
        command: str,
        raw_args: str = '',
        asynchronous: bool = True,
        remote_connection: 'environ.RemoteConnection' = None
) -> typing.List[Response]:
    """ """

    remote_connection = (
        remote_connection
        if remote_connection else
        environ.remote_connection
    )

    responses = []
    endpoint = '/command-async' if asynchronous else '/command-sync'

    try:
        responses.append(comm.send_request(
            endpoint=endpoint,
            remote_connection=remote_connection,
            data=dict(command=command, args=raw_args)
        ))
    except Exception as error:
        responses.append(Response().fail(
            code='COMM_EXECUTION_ERROR',
            error=error,
            message='Communication execution error'
        ).response)

    while not is_finished:
        time.sleep(1)
        responses.append(check_status(responses, remote_connection))

    return responses
