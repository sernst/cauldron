import os
import time
import typing

import cauldron
from cauldron import environ
from cauldron import templating
from cauldron.environ import Response
from cauldron.runner import python_file
from cauldron.session.projects import Project
from cauldron.session.projects import ProjectStep

ERROR_STATUS = 'error'
OK_STATUS = 'ok'
SKIP_STATUS = 'skip'


def get_step(
        project: Project,
        step: typing.Union[ProjectStep, str]
) -> ProjectStep:
    """

    :param project:
    :param step:
    :return:
    """

    if isinstance(step, ProjectStep):
        return step

    for ps in project.steps:
        if ps.definition.name == step:
            return ps

    return None


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

    # Set the top-level display and cache values to the current project values
    # before running the step for availability within the step scripts
    cauldron.shared = cauldron.project.shared

    if run_markdown_file(project, step):
        return True

    if run_html_file(project, step):
        return True

    step.is_running = True

    # Mark the downstream steps as dirty because this one has run
    [x.mark_dirty(True) for x in project.steps[(step.index + 1):]]

    result = python_file.run(project, step)

    if result['success']:
        step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(step.definition.name))
    else:
        step.last_modified = 0.0
        step.error = result['html_message']
        response.fail(
            message='Step execution error',
            code='EXECUTION_ERROR'
        ).kernel(
            project=project.kernel_serialize(),
            step_name=step.definition.name
        ).console_raw(
            result['message']
        )

    step.is_running = False
    step.dumps()

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
            message='Source file not found "{}"'.format(path)
        ).kernel(
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


def run_markdown_file(
        project: Project,
        step: ProjectStep
) -> bool:
    """

    :param project:
    :param step:
    :return:
    """

    if not step.source_path.endswith('.md'):
        return False

    with open(step.source_path, 'r+') as f:
        code = f.read()

    cauldron.display.markdown(code, **project.shared.fetch(None))
    step.last_modified = time.time()
    environ.log('[{}]: Updated'.format(step.definition.name))
    step.mark_dirty(False)
    step.dumps()

    return True


def run_html_file(
        project: Project,
        step: ProjectStep
) -> bool:
    """

    :param project:
    :param step:
    :return:
    """

    if not step.source_path.endswith('.html'):
        return False

    with open(step.source_path, 'r+') as f:
        code = f.read()

    step.report.html(templating.render(
        template=code,
        **project.shared.fetch(None)
    ))
    step.last_modified = time.time()
    environ.log('[{}]: Updated'.format(step.definition.name))
    step.mark_dirty(False)
    step.dumps()
    return True



