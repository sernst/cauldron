import os
import sys
import traceback
import types
import typing
import time
import functools
from importlib.abc import InspectLoader

import cauldron
from cauldron import cli
from cauldron import templating
from cauldron import environ
from cauldron.session.project import Project
from cauldron.session.project import ProjectStep
from cauldron.session.project import ProjectDependency


def step_print(
        project_step: ProjectStep,
        *args, sep='',
        end='\n',
        file=None,
        flush=False
):
    """

    :param project_step:
    :param args:
    :param sep:
    :param end:
    :param file:
    :param flush:
    :return:
    """

    if hasattr(project_step, 'report'):
        text = '\t'.join([str(x) for x in args])
        project_step.report.text(text, preformatted=True)

    print(*args, sep=sep, end='\n', file=file, flush=flush)


def source_dependency(
        project: Project,
        dependency: ProjectDependency
) -> bool:
    """

    :param project:
    :param dependency:
    :return:
    """

    if isinstance(dependency, str):
        found = False
        for pd in project.dependencies:
            if pd.id == dependency:
                dependency = pd
                found = True
                break

        if not found:
            return False

    status = check_status(project, dependency)
    if status['code'] == 'NOT-FOUND':
        environ.log('[{id}]: Dependency Not found "{path}"'.format(
            id=dependency.id,
            path=status['path']
        ))
        return False

    dependency.error = None
    if status['code'] == 'SKIP':
        return True

    os.chdir(os.path.dirname(status['path']))
    project.current_step = None

    # Set the top-level display and cache values to the current project values
    # before running the step for availability within the step scripts
    cauldron.display = None
    cauldron.shared = cauldron.project.shared

    result = run_python_file(project, dependency)
    if result['success']:
        environ.log('[{}]: Updated'.format(dependency.id))
        return True

    environ.log_raw(result['message'])
    dependency.error = result['html_message']

    return False


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
            if ps.id == step:
                step = ps
                found = True
                break

        if not found:
            return False

    status = check_status(project, step, force)
    if status['code'] == 'NOT-FOUND':
        environ.log('[{id}]: Not found "{path}"'.format(
            id=step.id,
            path=status['path']
        ))
        return False

    step.error = None
    if status['code'] == 'SKIP':
        environ.log('[{}]: Nothing to update'.format(step.id))
        return True

    os.chdir(os.path.dirname(status['path']))
    project.current_step = step
    step.report.clear()

    # Set the top-level display and cache values to the current project values
    # before running the step for availability within the step scripts
    cauldron.display = cauldron.project.display
    cauldron.shared = cauldron.project.shared

    if status['path'].endswith('.md'):
        with open(status['path'], 'r+') as f:
            code = f.read()

        step.report.markdown(code, **project.shared.fetch(None))
        step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(step.id))
        step.mark_dirty(False)
        return True

    if status['path'].endswith('.html'):
        with open(status['path'], 'r+') as f:
            code = f.read()

        step.report.html(templating.render(
            template=code,
            **project.shared.fetch(None)
        ))
        step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(step.id))
        step.mark_dirty(False)
        return True

    # Mark the downstream steps as dirty because this one has run
    [x.mark_dirty(True) for x in project.steps[(step.index + 1):]]

    result = run_python_file(project, step)
    if result['success']:
        environ.log('[{}]: Updated'.format(step.id))
        return True

    environ.log_raw(result['message'])
    step.error = result['html_message']

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
):

    module_name = target.id.rsplit('.', 1)[0]
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
    setattr(module, 'print', functools.partial(step_print, target))

    try:
        exec(code, module.__dict__)
        target.last_modified = time.time()
        target.mark_dirty(False)
        return {'success': True}
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

        return dict(
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
