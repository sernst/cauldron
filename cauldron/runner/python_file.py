import io
import os
import sys
import time
import traceback
import types
from importlib.abc import InspectLoader

from cauldron import environ
from cauldron import templating
from cauldron.session.projects import Project
from cauldron.session.projects import ProjectStep


class UserAbortError(Exception):
    pass


def run(
        project: Project,
        step: ProjectStep,
) -> dict:
    """

    :param project:
    :param step:
    :return:
    """

    step = project.current_step
    module_name = step.definition.name.rsplit('.', 1)[0]
    module = types.ModuleType(module_name)

    with open(step.source_path, 'r+') as f:
        code = f.read()

    code = InspectLoader.source_to_code(code, step.source_path)

    setattr(module, '__file__', step.source_path)
    setattr(
        module,
        '__package__',
        '.'.join(
            [project.id.replace('.', '-')] +
            step.filename.rsplit('.', 1)[0].split(os.sep)
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

    out = None

    try:
        exec(code, module.__dict__)
    except Exception as err:
        if not isinstance(err, UserAbortError):
            out = render_error(project, err)

    if out is None:
        step.last_modified = time.time()
        step.mark_dirty(False)
        out = {'success': True}

    # Restore the print buffer
    sys.stdout = sys.__stdout__
    step.report.flush_prints()
    print_redirect.close()
    step.report.print_buffer = None

    return out


def render_error(project, error):
    """

    :param project:
    :param error:
    :return:
    """

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
