import typing
from argparse import ArgumentParser

import requests
from cauldron import cli
from cauldron.environ import Response
from requests import exceptions as request_exceptions

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


def execute(
        parser: ArgumentParser,
        response: Response,
        url: str = None,
) -> Response:
    """

    :return:
    """

    url_clean = '{}{}'.format(
        '' if url.startswith('http') else 'http://',
        url.strip().rstrip('/')
    )

    ping = '{}/ping'.format(url_clean)

    print('CONNECTING TO: {}'.format(url_clean))

    try:
        result = requests.get(ping)
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

    return response.update(
        url=url_clean
    ).notify(
        kind='SUCCESS',
        code='CONNECTED',
        message='Connected to "{}"'.format(url_clean)
    ).console(
        whitespace=1
    ).response


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    return []
