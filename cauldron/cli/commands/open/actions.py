import os

import cauldron
from cauldron import environ
from cauldron.cli import query
from cauldron import runner
from cauldron import reporting


def fetch_recent() -> str:
    """

    :return:
    """

    recent_paths = environ.configs.fetch('recent_paths', [])

    if len(recent_paths) < 1:
        environ.log(
            '[ABORTED]: There are no recent projects available'
        )
        return

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

    return None


def fetch_last() -> str:
    """

    :return:
    """

    recent_paths = environ.configs.fetch('recent_paths', [])

    if len(recent_paths) < 1:
        environ.log('[ABORTED]: No projects have been opened recently')
        return None

    return recent_paths[0]


def open_project(path: str) -> bool:
    """

    :return:
    """

    recent_paths = environ.configs.fetch('recent_paths', [])
    path = environ.paths.clean(path)

    if not os.path.exists(path):
        environ.log(
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
        environ.log('Error: Project not found')
        return

    if path in recent_paths:
        recent_paths.remove(path)
    recent_paths.insert(0, path)
    environ.configs.put(recent_paths=recent_paths[:10], persists=True)
    environ.configs.save()

    project = cauldron.project.internal_project

    if project.results_path:
        reporting.initialize_results_path(project.results_path)

    path = project.output_path
    if not path or not os.path.exists(path):
        project.write()

    url = project.url

    header = 'OPENED: {}'.format(project.title)
    environ.log(
        """
        {bars}
        {header}
        {bars}

          PATH: {path}

           URL: {url}
        """.format(
            bars='=' * len(header),
            header=header,
            path=path,
            url=url
        ),
        whitespace=1
    )

