import glob
import os

import cauldron
from cauldron import environ
from cauldron import runner
from cauldron import session
from cauldron.cli.interaction import query
from cauldron.environ import Response


def echo_known_projects(response: Response) -> dict:
    """

    :return:
    """

    def print_path_group(header, paths):
        if not paths:
            return

        environ.log_header(header, level=6, indent_by=2)
        entries = []
        for p in paths:
            parts = p.rstrip(os.sep).split(os.sep)
            name = parts[-1]
            if name.startswith('@'):
                name = name.split(':', 1)[-1]
            entries.append(
                '* "{name}" -> {path}'.format(name=name, path=p)
            )

        environ.log('\n'.join(entries), indent_by=4)

    def project_paths_at(root_path):
        glob_path = os.path.join(root_path, '**', 'cauldron.json')
        return [
            os.path.dirname(x)[(len(root_path) + 1):]
            for x in glob.iglob(glob_path, recursive=True)
        ]

    environ.log_header('Existing Projects')

    print_path_group(
        'Recently Opened',
        environ.configs.fetch('recent_paths', [])
    )

    environ.configs.load()
    aliases = dict(
        home={
            'path': environ.paths.clean(os.path.join('~', 'cauldron'))
        },
        examples={
            'path': environ.paths.package('resources', 'examples')
        }
    )
    aliases.update(environ.configs.fetch('folder_aliases', {}))
    aliases = [(k, p) for k, p in aliases.items()]
    aliases.sort(key=lambda x: x[0])

    for key, data in aliases:
        print_path_group(
            key.capitalize(),
            [
                '@{}:{}'.format(key, x)
                for x in project_paths_at(data['path'])
            ]
        )

    environ.log_blanks()


def fetch_recent(response: Response) -> str:
    """

    :return:
    """

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


def fetch_location(response: Response, path: str) -> str:
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


def fetch_last(response: Response) -> str:
    """

    :return:
    """

    recent_paths = environ.configs.fetch('recent_paths', [])

    if len(recent_paths) < 1:
        response.fail(
            code='NO_RECENT_PROJECTS',
            message='No projects have been opened recently'
        ).console()
        return None

    return recent_paths[0]


