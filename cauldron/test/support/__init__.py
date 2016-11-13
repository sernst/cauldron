import os
import re
from unittest.mock import patch

from cauldron import environ
from cauldron.cli import commander
from cauldron.cli.shell import CauldronShell
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message

try:
  import readline
except ImportError:
  import pyreadline as readline


def run_command(command: str) -> 'environ.Response':
    """

    :param command:
    :return:
    """

    cs = CauldronShell()
    cs.default(command)
    return cs.last_response


def create_project(
        tester: scaffolds.ResultsTest,
        name: str,
        path: str = None,
        forget: bool = True,
        **kwargs
) -> 'environ.Response':
    """

    :param tester:
    :param name:
    :param path:
    :param forget:
    :param kwargs:
    :return:
    """

    if path is None:
        path = tester.get_temp_path('project-{}-'.format(name))

    r = environ.Response()

    args = [name, path]
    for key, value in kwargs.items():
        args.append('--{}="{}"'.format(key, value))

    if forget:
        args.append('--forget')

    args = ' '.join([a for a in args if a and len(a) > 0])

    commander.execute('create', args, response=r)
    if r.thread:
        r.thread.join()

    return r


def open_project(
        tester: scaffolds.ResultsTest,
        path: str
) -> 'environ.Response':
    """

    :param tester:
    :param path:
    :return:
    """

    r = environ.Response()
    commander.execute('open', '{} --forget'.format(path), r)
    r.thread.join()
    return r


def autocomplete(command: str):
    """

    :param command:
    :return:
    """

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
        contents: str = ''
):
    """

    :param tester:
    :param name:
    :param contents:
    :return:
    """

    r = run_command('steps add "{}"'.format(name))
    step_path = r.data['step_path']

    with open(step_path, 'w+') as f:
        f.write(contents)

    return step_path
