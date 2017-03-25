import threading
import time
import typing
import uuid

from cauldron import environ
from cauldron.environ.response import Response
from cauldron.cli.sync import comm


def send_remote_command(
        command: str,
        raw_args: str = '',
        asynchronous: bool = True,
        remote_connection: 'environ.RemoteConnection' = None,
        show_logs: bool = True
) -> 'AsyncCommandThread':
    """ """

    thread = AsyncCommandThread(
        command=command,
        arguments=raw_args,
        is_async=asynchronous,
        remote_connection=remote_connection,
        is_logging=show_logs
    )

    thread.start()
    return thread


class AsyncCommandThread(threading.Thread):

    def __init__(
            self,
            command: str,
            arguments: str = '',
            is_async: bool = True,
            remote_connection: 'environ.RemoteConnection' = None,
            is_logging: bool = True,
            **kwargs
    ):
        super(AsyncCommandThread, self).__init__(**kwargs)
        self.daemon = True
        self.abort = False
        self.uid = str(uuid.uuid4())
        self.responses = []  # type: typing.List[Response]
        self.exception = None
        self.is_executing = False
        self.command = command
        self.args = arguments
        self.is_async = is_async
        self.is_logging = is_logging

        self._remote_connection = remote_connection

    @property
    def remote_connection(self) -> 'environ.RemoteConnection':
        return (
            self._remote_connection
            if self._remote_connection else
            environ.remote_connection
        )

    @property
    def is_finished(self) -> bool:
        """ """

        has_response = len(self.responses) > 0
        has_finished_response = has_response and (
            self.responses[-1].failed or
            self.responses[-1].data['run_status'] != 'running'
        )

        return has_finished_response

    def check_status(self) -> Response:
        """ """

        run_uid = self.responses[-1].data.get('run_uid', '')
        endpoint = '/abort' if self.abort else '/run-status/{}'.format(run_uid)

        return comm.send_request(
            endpoint=endpoint,
            remote_connection=self.remote_connection,
            method='GET'
        )

    def add_response(self, response: Response) -> Response:
        """ """

        run_log = response.data.get('run_log', [])
        previous = self.responses + []

        self.responses.append(response)

        if not self.is_logging:
            return response

        log_lengths = [len(r.data.get('run_log', [])) for r in previous]
        start_index = max(log_lengths + [0])
        new_log = run_log[start_index:]

        for message in new_log:
            environ.log_raw(message)

        return response

    def run(self):
        """ """

        self.is_executing = True
        endpoint = '/command-async' if self.is_async else '/command-sync'

        try:
            self.add_response(comm.send_request(
                endpoint=endpoint,
                remote_connection=self.remote_connection,
                data=dict(
                    command=self.command,
                    args=self.args
                )
            ))
        except Exception as error:
            self.exception = error
            self.add_response(Response().fail(
                code='COMM_EXECUTION_ERROR',
                error=error,
                message='Communication execution error'
            ).response)

        while not self.is_finished:
            time.sleep(1)
            self.add_response(self.check_status())

        self.is_executing = False
