import typing
from argparse import ArgumentParser

import requests
from requests import exceptions as request_exceptions

from cauldron import cli
from cauldron import environ
from cauldron.environ import Response

NAME = 'connect'
DESCRIPTION = """
    Connect to a remote cauldron server and drive that server from this shell
    """


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
        'url',
        type=str,
        default=None,
        help=cli.reformat(
            'The URL of the remote cauldron server including port'
        )
    )

    parser.add_argument(
        '-f', '--force',
        dest='force',
        default=False,
        action='store_true',
        help=cli.reformat(
            """
            When this option is included, the connection will be established
            without communicating with the remote cauldron instead to validate
            the connection. This should only be used in cases where you are
            absolutely confident that the connection is valid and accessible.
            """
        )
    )


def check_connection(url: str, force: bool) -> Response:
    """ """

    response = Response()
    if force:
        return response

    ping = '{}/ping'.format(url)

    response.notify(
        kind='STARTING',
        code='CONNECTING',
        message='Establishing connection to: {}'.format(url)
    ).console(
        whitespace_top=1
    )

    try:
        result = requests.get(ping)

        if result.status_code != 200:
            raise request_exceptions.ConnectionError()
    except request_exceptions.InvalidURL as error:
        return response.fail(
            code='INVALID_URL',
            message='Invalid connection URL. Unable to establish connection',
            error=error
        ).console(
            whitespace=1
        ).response
    except request_exceptions.ConnectionError as error:
        return response.fail(
            code='CONNECTION_ERROR',
            message='Unable to connect to remote cauldron host',
            error=error
        ).console(
            whitespace=1
        ).response
    except Exception as error:
        return response.fail(
            code='CONNECT_COMMAND_ERROR',
            message='Failed to connect to the remote cauldron host',
            error=error
        ).console(
            whitespace=1
        ).response


def execute(
        context: cli.CommandContext,
        url: str = None,
        force: bool = False
) -> Response:
    """ """

    url_clean = '{}{}'.format(
        '' if url.startswith('http') else 'http://',
        url.strip().rstrip('/')
    )

    context.response.consume(check_connection(url_clean, force))
    if context.response.failed:
        return context.response

    environ.remote_connection = environ.RemoteConnection(
        active=True,
        url=url_clean
    )

    return context.response.update(
        url=url_clean,
        remote_connection=environ.remote_connection
    ).notify(
        kind='SUCCESS',
        code='CONNECTED',
        message='Connected to "{}"'.format(url_clean)
    ).console(
        whitespace_bottom=1
    ).response


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    return []
