import os
import typing

from cauldron import environ
from cauldron.cli.interaction import query
from cauldron.environ import Response
from cauldron.cli.commands.listing import discovery


def fetch_recent(response: Response) -> typing.Optional[str]:
    """Return recently opened projects."""

    recent_paths = environ.configs.fetch('recent_paths', [])

    if len(recent_paths) < 1:
        response.fail(
            code='NO_RECENT_PROJECTS',
            message='There are no recent projects available'
        ).console()
        return None

    index, path = query.choice(
        'Recently Opened Projects',
        'Choose a project',
        recent_paths + ['Cancel'],
        0
    )
    if index == len(recent_paths):
        return None

    return path


def fetch_location(response: Response, path: str) -> typing.Optional[str]:
    """

    :param path:
    :return:
    """

    if not path or not path.startswith('@'):
        return None

    parts = path.lstrip(':').split(':', 1)
    segments = parts[-1].replace('\\', '/').strip('/').split('/')

    if parts[0] == '@examples':
        return environ.paths.package('resources', 'examples', *segments)
    if parts[0] == '@home':
        return environ.paths.clean(os.path.join('~', 'cauldron', *segments))

    environ.configs.load()
    aliases = environ.configs.fetch('folder_aliases', {})
    key = parts[0][1:]
    if key in aliases:
        return environ.paths.clean(os.path.join(
            aliases[key]['path'],
            *segments
        ))

    return None


def fetch_last(response: Response) -> typing.Union[str, None]:
    """ Returns the last opened project path if such a path exists."""

    recent_paths = environ.configs.fetch('recent_paths', [])

    if len(recent_paths) < 1:
        response.fail(
            code='NO_RECENT_PROJECTS',
            message='No projects have been opened recently'
        ).console()
        return None

    return recent_paths[0]


def select_from_available(response: Response) ->typing.Optional[str]:
    """Returns the selected project path based on all available."""
    discovery.echo_known_projects(response)
    specs = response.data['specs']

    print(
        '\nEnter the number corresponding to the project you wish'
        '\nto open or blank to cancel.\n'
    )
    result = input('Select Project []: ')

    try:
        spec = specs[int(result) - 1]
        return spec.get('directory', {}).get('absolute')
    except Exception as error:
        return None
