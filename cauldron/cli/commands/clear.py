from argparse import ArgumentParser

import cauldron
from cauldron.environ import Response

NAME = 'clear'
DESCRIPTION = """
    Clears all shared data in the cache and reloads all internal project
    libraries.
    """


def execute(parser: ArgumentParser, response: Response) -> Response:
    """

    :return:
    """

    project = cauldron.project.internal_project

    if not project:
        return response.fail(
            code='NO_OPEN_PROJECT',
            message='No open project on which to clear data'
        ).console(
            whitespace=1
        ).response

    project.shared.clear()

    for ps in project.steps:
        ps.mark_dirty(True)

    return response.update(
        project=project.kernel_serialize()
    ).notify(
        kind='SUCCESS',
        code='SHARED_CLEARED',
        message='Shared data has been cleared'
    ).console(
        whitespace=1
    ).response
