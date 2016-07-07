import glob
import os

import cauldron
from cauldron import environ
from cauldron import runner
from cauldron import session
from cauldron.cli.interaction import query


def echo_known_projects() -> dict:
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
        example={
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


def fetch_recent() -> str:
    """

    :return:
    """

    recent_paths = environ.configs.fetch('recent_paths', [])

    if len(recent_paths) < 1:
        environ.output.fail().notify(
            kind='ABORTED',
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


def fetch_location(path: str) -> str:
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


def fetch_last() -> str:
    """

    :return:
    """

    recent_paths = environ.configs.fetch('recent_paths', [])

    if len(recent_paths) < 1:
        environ.output.fail().notify(
            kind='ABORTED',
            code='NO_RECENT_PROJECTS',
            message='No projects have been opened recently'
        ).console()
        return None

    return recent_paths[0]


def open_project(path: str) -> bool:
    """

    :return:
    """

    try:
        runner.close()
    except Exception:
        pass

    recent_paths = environ.configs.fetch('recent_paths', [])
    path = environ.paths.clean(path)

    if not os.path.exists(path):
        environ.output.fail().notify(
            kind='ERROR',
            code='PROJECT_NOT_FOUND',
            message='The project path does not exist'
        ).kernel(
            path=path
        ).console(
            """
            [ERROR]: The specified path does not exist

              {path}

            The operation was aborted
            """.format(path=path)
        )
        return False

    try:
        runner.initialize(path)
    except FileNotFoundError:
        environ.output.fail().notify(
            kind='ERROR',
            code='PROJECT_NOT_FOUND',
            message='Project not found'
        ).console()
        return

    if path in recent_paths:
        recent_paths.remove(path)
    recent_paths.insert(0, path)
    environ.configs.put(recent_paths=recent_paths[:10], persists=True)
    environ.configs.save()

    project = cauldron.project.internal_project

    # Set the top-level display and cache values to the current project values
    # before running the step for availability within the step scripts
    cauldron.shared = cauldron.project.shared

    if project.results_path:
        session.initialize_results_path(project.results_path)

    path = project.output_path
    if not path or not os.path.exists(path):
        project.write()

    environ.output.update(
        project=project.kernel_serialize()
    )

    environ.log_header(project.title, level=2)
    environ.log(
        """
        PATH: {path}
         URL: {url}
        """.format(path=path, url=project.url),
        whitespace=1
    )

