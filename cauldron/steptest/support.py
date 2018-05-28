import json
import os
import tempfile
import time
import typing

import cauldron as cd
from cauldron import environ
from cauldron.cli import commander
from cauldron.session import exposed
from cauldron.steptest.results import StepTestRunResult


def find_project_directory(subdirectory: str) -> typing.Union[str, None]:
    """
    Finds the root project directory from a subdirectory within the project
    folder.

    :param subdirectory:
        The subdirectory to use to search for the project directory. The
        subdirectory may also be the project directory.
    :return:
        The project directory that contains the specified subdirectory or None
        if no project directory was found.
    """
    if os.path.exists(os.path.join(subdirectory, 'cauldron.json')):
        return subdirectory

    parent = os.path.dirname(subdirectory)
    if parent == subdirectory:
        raise FileNotFoundError('Unable to find a Cauldron project directory.')

    if os.path.exists(os.path.join(parent, 'cauldron.json')):
        return parent

    return find_project_directory(parent)


def open_project(project_path: str) -> 'exposed.ExposedProject':
    """
    Returns the Response object populated by the open project command
    """
    res = commander.execute(
        name='open',
        raw_args='{} --forget'.format(project_path),
        response=environ.Response()
    )
    res.thread.join()

    # Prevent threading race conditions
    check_count = 0
    while res.success and not cd.project.internal_project:
        if check_count > 100:
            break

        check_count += 1
        time.sleep(0.25)

    if res.failed or not cd.project.internal_project:
        raise RuntimeError(
            'Unable to open project at path "{}"'.format(project_path)
        )

    os.chdir(cd.project.internal_project.source_directory)

    return cd.project


def run_step(
        step_name: str,
        allow_failure: bool = False
) -> StepTestRunResult:
    """
    Runs the specified step by name its complete filename including extension

    :param step_name:
        The full filename of the step to be run including its extension.
    :param allow_failure:
        Whether or not to allow a failed result to be returned. If False,
        a failed attempt to run a step will cause the current test to
        fail immediately before returning a value from this function call.
        Override this with a True value to have the step failure data
        passed back for inspection.
    :return:
        A StepTestRunResult instance containing information about the
        execution of the step.
    """
    project = cd.project.internal_project
    if not project:
        raise AssertionError(
            'No project was open. Unable to run step "{}"'
            .format(step_name)
        )

    step = project.get_step(step_name)
    if not step:
        raise AssertionError('No step named "{}" was found'.format(step_name))

    response = commander.execute('run', '"{}" --force'.format(step_name))
    response.thread.join()

    if not allow_failure and response.failed:
        raise AssertionError('Failed to run step "{}"'.format(step_name))

    return StepTestRunResult(step, response)


def make_temp_path(existing_directories, identifier, *args) -> str:
    """
    :param existing_directories:
    :param identifier:
    :param args:
    :return:
    """
    if identifier not in existing_directories:
        existing_directories[identifier] = tempfile.mkdtemp(
            prefix='cd-step-test-{}'.format(identifier)
        )
    return os.path.realpath(
        os.path.join(existing_directories[identifier], *args)
    )


def get_library_paths(project_path: str):
    """..."""
    path = (
        os.path.join(project_path, 'cauldron.json')
        if not project_path.endswith('cauldron.json') else
        project_path
    )
    directory = os.path.dirname(path)

    with open(path, 'r') as f:
        settings = json.load(f)

    def listify(value):
        return [value] if isinstance(value, str) else list(value)

    folders = listify(settings.get('library_folders') or ['libs'])

    # Include the remote shared library folder as well
    folders.append('../__cauldron_shared_libs')

    results = [
        environ.paths.clean(os.path.join(directory, folder))
        for folder in folders
    ]
    return [r for r in results if os.path.exists(r) and os.path.isdir(r)]
