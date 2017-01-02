import os
import time
import typing

import cauldron
from cauldron import environ
from cauldron.environ import Response
from cauldron.runner import html_file
from cauldron.runner import markdown_file
from cauldron.runner import python_file
from cauldron.session.projects import Project
from cauldron.session.projects import ProjectStep
from cauldron.runner import redirection

ERROR_STATUS = 'error'
OK_STATUS = 'ok'
SKIP_STATUS = 'skip'


def get_step(
        project: Project,
        step: typing.Union[ProjectStep, str]
) -> typing.Union[ProjectStep, None]:
    """

    :param project:
    :param step:
    :return:
    """

    if isinstance(step, ProjectStep):
        return step

    matches = [ps for ps in project.steps if ps.definition.name == step]
    return matches[0] if len(matches) > 0 else None


def has_extension(file_path: str, *args: typing.Tuple[str]) -> bool:
    """
    Checks to see if the given file path ends with any of the specified file
    extensions. If a file extension does not begin with a '.' it will be added
    automatically

    :param file_path:
        The path on which the extensions will be tested for a match
    :param args:
        One or more extensions to test for a match with the file_path argument
    :return:
        Whether or not the file_path argument ended with one or more of the
        specified extensions
    """

    def add_dot(extension):
        return (
            extension
            if extension.startswith('.') else
            '.{}'.format(extension)
        )

    return any([
        file_path.endswith(add_dot(extension))
        for extension in args
    ])


def _execute_step(project: Project, step: ProjectStep) -> dict:
    if has_extension(step.source_path, 'md'):
        return markdown_file.run(project, step)

    if has_extension(step.source_path, 'html'):
        return html_file.run(project, step)

    # Mark the downstream steps as dirty because this one has run
    [x.mark_dirty(True) for x in project.steps[(step.index + 1):]]

    if has_extension(step.source_path, 'py'):
        return python_file.run(project, step)

    return {'success': False}


def run_step(
        response: Response,
        project: Project,
        step: typing.Union[ProjectStep, str],
        force: bool = False
) -> bool:
    """

    :param response:
    :param project:
    :param step:
    :param force:
    :return:
    """

    step = get_step(project, step)
    if step is None:
        return False

    status = check_status(response, project, step, force)
    if status == ERROR_STATUS:
        return False

    step.error = None

    if status == SKIP_STATUS:
        return True

    os.chdir(os.path.dirname(step.source_path))
    project.current_step = step
    step.report.clear()
    step.dom = None
    step.is_running = True
    step.progress_message = None
    step.progress = 0

    # Set the top-level display and cache values to the current project values
    # before running the step for availability within the step scripts
    cauldron.shared = cauldron.project.shared

    redirection.enable(step)

    try:
        result = _execute_step(project, step)
    except Exception as err:
        result = dict(
            success=False,
            html_message='<pre>{}</pre>'.format(err)
        )

    os.chdir(os.path.expanduser('~'))

    step.is_running = False
    step.progress = 0
    step.progress_message = None
    step.dumps()

    # Make sure this is called prior to printing response information to the
    # console or that will come along for the ride
    redirection.disable(step)

    if result['success']:
        step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(step.definition.name))
    else:
        step.last_modified = 0.0
        step.error = result['html_message']
        response.fail(
            message='Step execution error',
            code='EXECUTION_ERROR',
            project=project.kernel_serialize(),
            step_name=step.definition.name
        ).console_raw(result['message'])

    return result['success']


def check_status(
        response: Response,
        project: Project,
        step: ProjectStep,
        force: bool = False
) -> str:
    """

    :param response:
    :param project:
    :param step:
    :param force:
    :return:
    """

    path = step.source_path

    if step.is_muted:
        environ.log('[{}]: Muted (skipped)'.format(step.definition.name))
        return SKIP_STATUS

    if not os.path.exists(path):
        response.fail(
            code='MISSING_SOURCE_FILE',
            message='Source file not found "{}"'.format(path),
            id=step.definition.name,
            path=path
        ).console(
            '[{id}]: Not found "{path}"'.format(
                id=step.definition.name,
                path=path
            )
        )
        return ERROR_STATUS

    if not force and not step.is_dirty():
        environ.log('[{}]: Nothing to update'.format(step.definition.name))
        return SKIP_STATUS

    return OK_STATUS
