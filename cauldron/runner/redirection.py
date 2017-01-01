import sys
from cauldron.session import projects
from cauldron.session.buffering import RedirectBuffer


def enable(step: 'projects.ProjectStep'):
    """
    Create a print equivalent function that also writes the output to the
    project page. The write_through is enabled so that the TextIOWrapper
    immediately writes all of its input data directly to the underlying
    BytesIO buffer. This is needed so that we can safely access the buffer
    data in a multi-threaded environment to display updates while the buffer
    is being written to.

    :param step:
    """

    stdout_interceptor = RedirectBuffer(sys.stdout)
    sys.stdout = stdout_interceptor
    step.report.stdout_interceptor = stdout_interceptor

    stderr_interceptor = RedirectBuffer(sys.stderr)
    sys.stderr = stderr_interceptor
    step.report.stderr_interceptor = stderr_interceptor


def disable(step: 'projects.ProjectStep'):
    # Restore the print buffer

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    stdout_interceptor = step.report.stdout_interceptor
    stdout_interceptor.close()
    step.report.stdout_interceptor = None

    stderr_interceptor = step.report.stderr_interceptor
    stderr_interceptor.close()
    step.report.stderr_interceptor = None
