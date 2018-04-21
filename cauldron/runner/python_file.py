import codecs
import functools
import os
import threading
import types
import typing
from importlib.abc import InspectLoader

from cauldron import environ
from cauldron import templating
from cauldron.cli import threads
from cauldron.render import stack as render_stack
from cauldron.session import projects


class UserAbortError(Exception):
    """
    Error to raise when the user intentionally aborts a step by stopping it
    programmatically. A custom exception is required because this type of
    error should be handled differently by Cauldron. It should not result in
    the display of an error.
    """

    def __init__(self, halt: bool = False):
        """Create UserAbortError"""
        self.halt = halt


def set_executing(on: bool):
    """
    Toggle whether or not the current thread is executing a step file. This
    will only apply when the current thread is a CauldronThread. This function
    has no effect when run on a Main thread.

    :param on:
        Whether or not the thread should be annotated as executing a step file.
    """

    my_thread = threading.current_thread()

    if isinstance(my_thread, threads.CauldronThread):
        my_thread.is_executing = on


def get_file_contents(source_path: str) -> str:
    """
    Loads the contents of the source into a string for execution using multiple
    loading methods to handle cross-platform encoding edge cases. If none of
    the load methods work, a string is returned that contains an error function
    response that will be displayed when the step is run alert the user to the
    error.

    :param source_path:
        Path of the step file to load.
    """

    open_funcs = [
        functools.partial(codecs.open, source_path, encoding='utf-8'),
        functools.partial(open, source_path, 'r')
    ]

    for open_func in open_funcs:
        try:
            with open_func() as f:
                return f.read()
        except Exception:
            pass

    return (
        'raise IOError("Unable to load step file at: {}")'
        .format(source_path)
    )


def load_step_file(source_path: str) -> str:
    """
    Loads the source for a step file at the given path location and then
    renders it in a template to add additional footer data.

    The footer is used to force the display to flush the print buffer and
    breathe the step to open things up for resolution. This shouldn't be
    necessary, but it seems there's an async race condition with print
    buffers that is hard to reproduce and so this is in place to fix the
    problem.
    """

    return templating.render_template(
        template_name='embedded-step.py.txt',
        source_contents=get_file_contents(source_path)
    )


def create_module(
        project: 'projects.Project',
        step: 'projects.ProjectStep'
):
    """
    Creates an artificial module that will encompass the code execution for
    the specified step. The target module is populated with the standard dunder
    attributes like __file__ to simulate the normal way that Python populates
    values when loading a module.

    :param project:
        The currently open project.
    :param step:
        The step whose code will be run inside the target_module.
    :return
        The created and populated module for the given step.
    """

    module_name = step.definition.name.rsplit('.', 1)[0]
    target_module = types.ModuleType(module_name)

    dunders = dict(
        __file__=step.source_path,
        __package__='.'.join(
            [project.id.replace('.', '-')] +
            step.filename.rsplit('.', 1)[0].split(os.sep)
        )
    )

    for key, value in dunders.items():
        setattr(target_module, key, value)

    return target_module


def run(
        project: 'projects.Project',
        step: 'projects.ProjectStep',
) -> dict:
    """
    Carries out the execution of the step python source file by loading it into
    an artificially created module and then executing that module and returning
    the result.

    :param project:
        The currently open project.
    :param step:
        The project step for which the run execution will take place.
    :return:
        A dictionary containing the results of the run execution, which
        indicate whether or not the run was successful. If the run failed for
        any reason, the dictionary will contain error information for display.
    """

    target_module = create_module(project, step)
    source_code = load_step_file(step.source_path)

    try:
        code = InspectLoader.source_to_code(source_code, step.source_path)
    except SyntaxError as error:
        return render_syntax_error(project, error)

    def exec_test():
        step.test_locals = dict()
        step.test_locals.update(target_module.__dict__)
        exec(code, step.test_locals)

    try:
        set_executing(True)
        threads.abort_thread()

        if environ.modes.has(environ.modes.TESTING):
            exec_test()
        else:
            exec(code, target_module.__dict__)
        out = {
            'success': True,
            'stop_condition': projects.StopCondition(False, False)
        }
    except threads.ThreadAbortError:
        # Raised when a user explicitly aborts the running of the step through
        # a user-interface action.
        out = {
            'success': False,
            'stop_condition': projects.StopCondition(True, True)
        }
    except UserAbortError as error:
        # Raised when a user explicitly aborts the running of the step using
        # a cd.step.stop(). This behavior should be considered a successful
        # outcome as it was intentional on the part of the user that the step
        # abort running early.
        out = {
            'success': True,
            'stop_condition': projects.StopCondition(True, error.halt)
        }
    except Exception as error:
        out = render_error(project, error)

    set_executing(False)
    return out


def render_syntax_error(
        project: 'projects.Project',
        error: SyntaxError
) -> dict:
    """
    Renders a SyntaxError, which has a shallow, custom stack trace derived
    from the data included in the error, instead of the standard stack trace
    pulled from the exception frames.

    :param project:
        Currently open project.
    :param error:
        The SyntaxError to be rendered to html and text for display.
    :return:
        A dictionary containing the error response with rendered display
        messages for both text and html output.
    """

    return render_error(
        project=project,
        error=error,
        stack=[dict(
            filename=getattr(error, 'filename'),
            location=None,
            line_number=error.lineno,
            line=error.text.rstrip()
        )]
    )


def render_error(
        project: 'projects.Project',
        error: Exception,
        stack: typing.List[dict] = None
) -> dict:
    """
    Renders an Exception to an error response that includes rendered text and
    html error messages for display.

    :param project:
        Currently open project.
    :param error:
        The SyntaxError to be rendered to html and text for display.
    :param stack:
        Optionally specify a parsed stack. If this value is None the standard
        Cauldron stack frames will be rendered.
    :return:
        A dictionary containing the error response with rendered display
        messages for both text and html output.
    """

    data = dict(
        type=error.__class__.__name__,
        message='{}'.format(error),
        stack=(
            stack
            if stack is not None else
            render_stack.get_formatted_stack_frame(project)
        )
    )

    return dict(
        success=False,
        error=error,
        message=templating.render_template('user-code-error.txt', **data),
        html_message=templating.render_template('user-code-error.html', **data)
    )
