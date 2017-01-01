import os
import sys
import threading
import traceback
import types
from importlib.abc import InspectLoader

from cauldron import environ
from cauldron import templating
from cauldron.cli import threads
from cauldron.runner import redirection
from cauldron.session import projects


class UserAbortError(Exception):
    pass


def set_executing(on: bool):
    """

    :param on:
    :return:
    """

    my_thread = threading.current_thread()

    if isinstance(my_thread, threads.CauldronThread):
        my_thread.is_executing = on


def run(
        project: 'projects.Project',
        step: 'projects.ProjectStep',
) -> dict:
    """

    :param project:
    :param step:
    :return:
    """

    module_name = step.definition.name.rsplit('.', 1)[0]
    module = types.ModuleType(module_name)

    with open(step.source_path, 'r+') as f:
        source_code = f.read()

    try:
        code = InspectLoader.source_to_code(source_code, step.source_path)
    except SyntaxError as error:
        return render_syntax_error(project, source_code, error)

    setattr(module, '__file__', step.source_path)
    setattr(
        module,
        '__package__',
        '.'.join(
            [project.id.replace('.', '-')] +
            step.filename.rsplit('.', 1)[0].split(os.sep)
        )
    )

    def exec_test():
        step.test_locals = dict()
        step.test_locals.update(module.__dict__)
        exec(code, step.test_locals)

    try:
        set_executing(True)
        threads.abort_thread()

        if environ.modes.has(environ.modes.TESTING):
            exec_test()
        else:
            exec(code, module.__dict__)
        out = None
    except threads.ThreadAbortError:
        out = {'success': False}
        step.mark_dirty(True)
    except UserAbortError:
        out = None
    except Exception as error:
        out = render_error(project, error)

    set_executing(False)

    if out is None:
        step.mark_dirty(False)
        out = {'success': True}

    return out


def render_syntax_error(
        project: 'projects.Project',
        code: str,
        error: SyntaxError
) -> dict:
    """

    :param project:
    :param code:
    :param error:
    :return:
    """

    stack = [dict(
        filename=error.filename,
        location=None,
        line_number=error.lineno,
        line=error.text.rstrip()
    )]

    render_data = dict(
        type=error.__class__.__name__,
        message='{}'.format(error),
        stack=stack
    )

    return dict(
        success=False,
        error=error,
        message=templating.render_template(
            'user-code-error.txt',
            **render_data
        ),
        html_message=templating.render_template(
            'user-code-error.html',
            **render_data
        )
    )


def get_stack_frames():
    """

    :return:
    """

    cauldron_path = environ.paths.package()
    resources_path = environ.paths.resources()
    frames = list(traceback.extract_tb(sys.exc_info()[-1])).copy()

    def is_cauldron_code(test_filename: str) -> bool:
        if not test_filename or not test_filename.startswith(cauldron_path):
            return False

        if test_filename.startswith(resources_path):
            return False

        return True

    while len(frames) > 1 and is_cauldron_code(frames[0].filename):
        frames.pop(0)

    return frames


def format_stack_frame(stack_frame, project: 'projects.Project'):
    """

    :param stack_frame:
    :param project:
    :return:
    """

    filename = stack_frame.filename
    if filename.startswith(project.source_directory):
        filename = filename[len(project.source_directory) + 1:]

    location = stack_frame.name
    if location == '<module>':
        location = None

    return dict(
        filename=filename,
        location=location,
        line_number=stack_frame.lineno,
        line=stack_frame.line
    )


def render_error(
        project: 'projects.Project',
        error: Exception
) -> dict:
    """

    :param project:
    :param error:
    :return:
    """

    render_data = dict(
        type=error.__class__.__name__,
        message='{}'.format(error),
        stack=[format_stack_frame(f, project) for f in get_stack_frames()]
    )

    return dict(
        success=False,
        error=error,
        message=templating.render_template(
            'user-code-error.txt',
            **render_data
        ),
        html_message=templating.render_template(
            'user-code-error.html',
            **render_data
        )
    )
