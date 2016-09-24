from argparse import ArgumentParser

from cauldron import environ
from cauldron.environ import Response

NAME = 'version'
DESCRIPTION = 'Displays Cauldron\'s version information'


def execute(
        parser: ArgumentParser,
        response: Response
) -> Response:
    """

    :return:
    """

    data = environ.package_settings

    if data:
        return response.update(
            **data
        ).notify(
            kind='SUCCESS',
            code='VERSION',
            message='Version is: {}'.format(data['version'])
        ).console(
            'Version: {version}'.format(version=data['version']),
            whitespace=1
        ).response

    return response.notify(
        kind='ERROR',
        code='MISSING_PACKAGE_DATA',
        message='Unable to locate version information'
    ).console(
        whitespace=1
    ).response
