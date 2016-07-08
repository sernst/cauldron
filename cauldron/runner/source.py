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
from cauldron import templating
from cauldron.session.projects import Project
from cauldron.session.projects import ProjectStep


def run_step(
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

    if isinstance(step, str):
        found = False
        for ps in project.steps:
            if ps.definition.name == step:
                step = ps
                found = True
                break

        if not found:
            return False

    status = check_status(project, step, force)
    if status['code'] == 'NOT-FOUND':
        environ.output.fail().notify(
            kind='ERROR',
            code='MISSING_SOURCE_FILE',
            message='Source file not found "{}"'.format(status['path'])
        ).kernel(
            id=step.definition.name,
            path=status['path']
        ).console(
            '[{id}]: Not found "{path}"'.format(
                id=step.definition.name,
                path=status['path']
            )
        )
        return False

    step.error = None

    if status['code'] == 'MUTED':
        environ.log('[{}]: Muted (skipped)'.format(step.definition.name))
        return True

    if status['code'] == 'SKIP':
        environ.log('[{}]: Nothing to update'.format(step.definition.name))
        return True

    os.chdir(os.path.dirname(status['path']))
    project.current_step = step
    step.report.clear()
    step.dom = None

    # Set the top-level display and cache values to the current project values
    # before running the step for availability within the step scripts
    cauldron.shared = cauldron.project.shared

    if status['path'].endswith('.md'):
        with open(status['path'], 'r+') as f:
            code = f.read()

        cauldron.display.markdown(code, **project.shared.fetch(None))
        step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(step.definition.name))
        step.mark_dirty(False)
        step.dumps()
        return True

    if status['path'].endswith('.html'):
        with open(status['path'], 'r+') as f:
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

    # Mark the downstream steps as dirty because this one has run
    [x.mark_dirty(True) for x in project.steps[(step.index + 1):]]

    result = run_python_file(project, step)
    if result['success']:
        environ.log('[{}]: Updated'.format(step.definition.name))
        step.dumps()
        return True

    step.error = result['html_message']
    environ.output.fail(
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

    step.dumps()

    return False


def check_status(
        project: Project,
        target,
        force: bool = False
) -> dict:
    """

    :param project:
    :param target:
    :param force:
    :return:
    """

    result = dict(
        path=target.source_path
    )

    if target.is_muted:
        result['code'] = 'MUTED'
        return result

    if not os.path.exists(result['path']):
        result.update(error=True, code='NOT-FOUND')
        return result

    if not force and not target.is_dirty():
        result['code'] = 'SKIP'
        return result

    result['code'] = 'RUN'
    return result


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
    # project page
    # print_redirect = printing.BufferedStringIO()
    # noinspection PyTypeChecker
    print_redirect = io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)
    sys.stdout = print_redirect
    step.report.print_buffer = print_redirect

    try:
        exec(code, module.__dict__)
        target.last_modified = time.time()
        target.mark_dirty(False)
        out = {'success': True}
    except Exception as err:
        frames = traceback.extract_tb(sys.exc_info()[-1])
        cauldron_path = environ.paths.package('cauldron')
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
