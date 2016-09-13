import io
import os
import sys
import time
import traceback
import types
import typing
from importlib.abc import InspectLoader

import cauldron
from cauldron import environ
from cauldron.environ import Response
from cauldron import templating
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

    result = run_python_file(project, step)

    if result['success']:
        step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(step.definition.name))
    else:
        step.last_modified = 0.0
        step.error = result['html_message']
        response.fail(
            project=project.kernel_serialize()
        ).notify(
            kind='ERROR',
            message='Step execution error',
            code='EXECUTION_ERROR'
        ).kernel(
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
        response.fail().notify(
            kind='ERROR',
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


def run_python_file(
        project: Project,
        target,
) -> dict:
    """

    :param project:
    :param target:
    :return:
    """

    step = project.current_step
    module_name = target.definition.name.rsplit('.', 1)[0]
    module = types.ModuleType(module_name)

    with open(target.source_path, 'r+') as f:
        code = f.read()

    code = InspectLoader.source_to_code(code, target.source_path)

    setattr(module, '__file__', target.source_path)
    setattr(
        module,
        '__package__',
        '.'.join(
            [project.id.replace('.', '-')] +
            target.filename.rsplit('.', 1)[0].split(os.sep)
        )
    )

    # Create a print equivalent function that also writes the output to the
    # project page. The write_through is enabled so that the TextIOWrapper
    # immediately writes all of its input data directly to the underlying
    # BytesIO buffer. This is needed so that we can safely access the buffer
    # data in a multi-threaded environment to display updates while the buffer
    # is being written to.
    #
    # noinspection PyTypeChecker
    print_redirect = io.TextIOWrapper(
        io.BytesIO(),
        sys.stdout.encoding,
        write_through=True
    )
    sys.stdout = print_redirect
    step.report.print_buffer = print_redirect

    try:
        exec(code, module.__dict__)
        target.last_modified = time.time()
        target.mark_dirty(False)
        out = {'success': True}
    except Exception as err:
        frames = traceback.extract_tb(sys.exc_info()[-1])
        cauldron_path = environ.paths.package()
        while frames and frames[0].filename.startswith(cauldron_path):
            frames.pop(0)

        stack = []
        for frame in frames:
            filename = frame.filename
            if filename.startswith(project.source_directory):
                filename = filename[len(project.source_directory) + 1:]

            location = frame.name
            if location == '<module>':
                location = None

            stack.append(dict(
                filename=filename,
                location=location,
                line_number=frame.lineno,
                line=frame.line
            ))

        render_data = dict(
            type=err.__class__.__name__,
            message='{}'.format(err),
            stack=stack
        )

        out = dict(
            success=False,
            error=err,
            message=templating.render_template(
                'user-code-error.txt',
                **render_data
            ),
            html_message=templating.render_template(
                'user-code-error.html',
                **render_data
            )
        )

    # Restore the print buffer
    sys.stdout = sys.__stdout__
    step.report.flush_prints()
    print_redirect.close()
    step.report.print_buffer = None

    return out
