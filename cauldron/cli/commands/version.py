import json
import typing
from argparse import ArgumentParser
from collections import OrderedDict

from cauldron import cli
from cauldron.cli import sync
from cauldron import environ
from cauldron.environ import Response

NAME = 'version'
DESCRIPTION = 'Displays Cauldron\'s version information'


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """

    :param parser:
    :param raw_args:
    :param assigned_args:
    :return:
    """

    parser.add_argument(
        '--verbose',
        dest='verbose',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            Adds verbose version information about the Python environment
            in addition to the basic Cauldron version information.
            """
        )
    )

    parser.add_argument(
        '--json',
        dest='as_json',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            Returns the version information in JSON format
            """
        )
    )


def pretty_print(source: dict, depth: int = 0) -> str:
    """

    :param source:
    :param depth:
    :return:
    """

    out = []

    if isinstance(source, OrderedDict):
        entries = source.items()
    else:
        entries = sorted(source.items(), key=lambda x: x[0])

    def to_string_entry(key, value):
        return '{}{}: {}'.format(depth * '  ', key, value)

    def list_item(index, value):
        key = '  [{}]'.format(index)

        if isinstance(value, (list, tuple, dict)):
            return to_string_entry(
                key,
                '\n{}'.format(pretty_print(value, depth + 2))
            )
        else:
            return to_string_entry(key, value)

    for k, v in entries:
        if isinstance(v, dict):
            out.append('{}{}:'.format(depth * '  ', k))
            out.append(pretty_print(v, depth + 1))
        elif isinstance(v, (list, tuple)):
            out.append('{}{}:'.format(depth * '  ', k))
            out.extend([list_item(i, item) for i, item in enumerate(v)])
        else:
            out.append(to_string_entry(k, v))

    return '\n'.join(out)


def execute_remote(context: cli.CommandContext, **kwargs) -> Response:
    """ """

    thread = sync.send_remote_command(
        command=context.name,
        raw_args=context.raw_args,
        asynchronous=False
    )

    thread.join()

    response = thread.responses[0]
    return context.response.consume(response)


def execute(
        context: cli.CommandContext,
        verbose: bool = False,
        as_json: bool = False
) -> Response:
    """

    :return:
    """

    response = context.response
    settings = environ.package_settings

    if verbose:
        data = environ.systems.get_system_data()
        data['cauldron'] = settings
    else:
        data = settings

    if as_json:
        output = json.dumps(data, indent=2)
    else:
        output = pretty_print(data)

    return response.notify(
        kind='SUCCESS',
        code='VERSION',
        data=data,
        output=output
    ).console(
        output,
        whitespace=1
    ).response
