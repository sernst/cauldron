import glob
import importlib
import os
import sys
import typing

import cauldron
from cauldron import environ
from cauldron.environ import Response
from cauldron.runner import source
from cauldron.session.projects import Project
from cauldron.session.projects import ProjectStep


def add_library_path(path: str) -> bool:
    """
    Adds the path to the Python system path if not already added and the path
    exists.

    :param path:
        The path to add to the system paths
    :return:
        Whether or not the path was added. Only returns False if the path was
        not added because it doesn't exist
    """

    if not os.path.exists(path):
        return False

    if path not in sys.path:
        sys.path.append(path)

    return True


def remove_library_path(path: str) -> bool:
    """
    Removes the path from the Python system path if it is found in the system
    paths.

    :param path:
        The path to remove from the system paths
    :return:
        Whether or not the path was removed.
    """

    if path in sys.path:
        sys.path.remove(path)
        return True

    return False


def initialize(project: typing.Union[str, Project]):
    """

    :param project:
    :return:
    """

    if isinstance(project, str):
        project = Project(source_directory=project)

    cauldron.project.load(project)
    return project


def close():
    """..."""
    os.chdir(os.path.expanduser('~'))
    project = cauldron.project.internal_project
    if not project:
        return False

    [remove_library_path(path) for path in project.library_directories]
    remove_library_path(project.source_directory)

    cauldron.project.unload()
    return True


def reload_libraries(library_directories: list = None):
    """
    Reload the libraries stored in the project's local and shared library
    directories
    """
    directories = library_directories or []
    project = cauldron.project.get_internal_project()
    if project:
        directories += project.library_directories

    if not directories:
        return

    def reload_module(path: str, library_directory: str):
        path = os.path.dirname(path) if path.endswith('__init__.py') else path
        start_index = len(library_directory) + 1
        end_index = -3 if path.endswith('.py') else None
        package_path = path[start_index:end_index]

        module = sys.modules.get(package_path.replace(os.sep, '.'))
        return importlib.reload(module) if module is not None else None

    def reload_library(directory: str) -> list:
        if not add_library_path(directory):
            # If the library wasn't added because it doesn't exist, remove it
            # in case the directory has recently been deleted and then return
            # an empty result
            remove_library_path(directory)
            return []

        glob_path = os.path.join(directory, '**', '*.py')
        return [
            reload_module(path, directory)
            for path in glob.glob(glob_path, recursive=True)
        ]

    return [
        reloaded_module
        for directory in directories
        for reloaded_module in reload_library(directory)
        if reload_module is not None
    ]


def section(
        response: Response,
        project: typing.Union[Project, None],
        starting: ProjectStep = None,
        limit: int = 1,
        force: bool = False,
        skips: typing.List[ProjectStep] = None
) -> list:
    """

    :param response:
    :param project:
    :param starting:
    :param limit:
    :param force:
    :param skips:
        Steps that should be skipped while running this section
    :return:
    """

    limit = max(1, limit)

    if project is None:
        project = cauldron.project.get_internal_project()

    starting_index = 0
    if starting:
        starting_index = project.steps.index(starting)
    count = 0

    steps_run = []

    for ps in project.steps:
        if count >= limit:
            break

        if ps.index < starting_index:
            continue

        if skips and ps in skips:
            continue

        if not force and count == 0 and not ps.is_dirty():
            continue

        steps_run.append(ps)
        if not source.run_step(response, project, ps, force=force):
            return steps_run

        count += 1

    return steps_run


def complete(
        response: Response,
        project: typing.Union[Project, None],
        starting: ProjectStep = None,
        force: bool = False,
        limit: int = -1
) -> list:
    """
    Runs the entire project, writes the results files, and returns the URL to
    the report file

    :param response:
    :param project:
    :param starting:
    :param force:
    :param limit:
    :return:
        Local URL to the report path
    """

    if project is None:
        project = cauldron.project.get_internal_project()

    starting_index = 0
    if starting:
        starting_index = project.steps.index(starting)
    count = 0

    steps_run = []

    for ps in project.steps:
        if 0 < limit <= count:
            break

        if ps.index < starting_index:
            continue

        if not force and not ps.is_dirty():
            if limit < 1:
                environ.log(
                    '[{}]: Nothing to update'.format(ps.definition.name)
                )
            continue

        count += 1

        steps_run.append(ps)
        success = source.run_step(response, project, ps, force=True)
        if not success or project.stop_condition.halt:
            return steps_run

    return steps_run
