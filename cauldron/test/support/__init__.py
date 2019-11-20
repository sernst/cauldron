import re
import sys
import typing
from unittest.mock import patch

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.cli import commander
from cauldron.cli import parse
from cauldron.cli.shell import CauldronShell
from cauldron.test.support import scaffolds
from cauldron.test.support import server
from cauldron.test.support.functional import ProjectLifecycleTester  # noqa
from cauldron.test.support.functional \
    import make_project_lifecycle_fixture  # noqa
from cauldron.test.support.messages import Message
from cauldron.test.support.mocking import populate_open_mock  # noqa

try:
  import readline
except ImportError:  # pragma: no cover
  import pyreadline as readline


def run_remote_command(
        command: str,
        app=None,
        remote_connection: 'environ.RemoteConnection' = None,
        mock_send_request=None,
) -> 'environ.Response':
    """
    Simulates the execution of a remote command in the local environment,
    which is useful for testing remote behaviors without having to support
    a multi-instance environment during testing.
    """
    name, args = parse.split_line(command)

    if not remote_connection:
        remote_connection = environ.RemoteConnection(
            url='fake-run-remote.command',
            active=True
        )

    # Create a test server to handle the remote command request.
    app = app if app else server.create_test_app()

    def default_mock_send_request(
            endpoint: str,
            data: dict = None,
            method: str = None,
            **kwargs
    ):
        http_method = method.lower() if method else None
        func = server.post if data or http_method == 'post' else server.get
        result = func(
            app=app,
            endpoint=endpoint,
            data=data
        )
        return result.response

    side_effect = (
        mock_send_request
        if mock_send_request else
        default_mock_send_request
    )

    target_path = 'cauldron.cli.sync.comm.send_request'
    with patch(target_path, side_effect=side_effect):
        response = commander.execute(
            name=name,
            raw_args=args,
            remote_connection=remote_connection
        ).response
        response.thread.join()
        return response


def run_command(command: str) -> 'environ.Response':
    """..."""
    cs = CauldronShell()
    cs.default(command)
    return cs.last_response


def create_project(
        tester: scaffolds.ResultsTest,
        name: str,
        path: str = None,
        forget: bool = True,
        confirm: bool = True,
        remote_connection: cli.CommandContext = None,
        **kwargs
) -> 'environ.Response':
    """

    :param tester:
    :param name:
    :param path:
    :param forget:
    :param confirm:
    :param remote_connection:
    :param kwargs:
    :return:
    """
    version = ''.join(['{}'.format(s) for s in sys.version_info])

    if path is None:
        path = tester.get_temp_path('project-{}-{}-'.format(name, version))

    args = [name, path]
    for key, value in kwargs.items():
        args.append('--{}="{}"'.format(key, value))

    if forget:
        args.append('--forget')

    args = ' '.join([a for a in args if a and len(a) > 0])

    r = commander.execute('create', args, remote_connection=remote_connection)
    if r.thread:
        r.thread.join()

    project = (
        cauldron.project.get_internal_project(2)
        if r.success else
        None
    )

    if confirm:
        tester.assertFalse(r.failed, Message(
            'support.create_project',
            'project should have been created',
            response=r
        ))
        tester.assertIsNotNone(project)

    return r


def open_project(
        tester: typing.Union[ProjectLifecycleTester, scaffolds.ResultsTest],
        path: str
) -> 'environ.Response':
    """..."""
    r = environ.Response()
    commander.execute('open', '{} --forget'.format(path), r)
    r.thread.join()
    return r


def autocomplete(command: str):
    """..."""
    # On Linux/OSX the completer delims are retrieved from the readline module,
    # but the delims are different on Windows. So for testing consistency we
    # supply the Linux/OSX delims explicitly here in place of:
    # readline.get_completer_delims()

    completer_delims = ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'

    with patch('readline.get_line_buffer', return_value=command):
        cs = CauldronShell()
        line = command.lstrip()

        splits = re.split('[{}]{{1}}'.format(
            re.escape(completer_delims)),
            line
        )

        return cs.completedefault(
            text=splits[-1],
            line=line,
            begin_index=len(line) - len(splits[-1]),
            end_index=len(line) - 1
        )


def add_step(
        tester: 'scaffolds.ResultsTest',
        name: str = '',
        contents: str = '',
        position: str = None
):
    """

    :param tester:
    :param name:
    :param contents:
    :param position:
    :return:
    """

    cmd = [
        'steps add "{}"'.format(name),
        '--position="{}"'.format(position) if position else None
    ]

    r = run_command(' '.join([c for c in cmd if c]))
    step_path = r.data['step_path']

    with open(step_path, 'w+') as f:
        f.write(contents)

    return step_path


def has_error_code(response: environ.Response, code: str) -> bool:
    """..."""
    assert response.failed, Message(
        'Expected a failed response',
        'Response should have failed if expecting an error',
        response=response
    )

    assert 0 < len(response.errors), Message(
        'Expected to find errors',
        'There should have been an error in the response',
        response=response
    )

    codes = [error.code for error in response.errors]

    return code in codes


def has_success_code(response: environ.Response, code: str):
    """..."""
    assert response.success, Message(
        'Expected a successful response',
        'Response should have succeeded.',
        response=response
    )

    codes = [message.code for message in response.messages]
    return code in codes
