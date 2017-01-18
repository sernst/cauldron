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

    # Prevent anything unusual from causing buffer issues
    restore_default_configuration()

    stdout_interceptor = RedirectBuffer(sys.stdout)
    sys.stdout = stdout_interceptor
    step.report.stdout_interceptor = stdout_interceptor

    stderr_interceptor = RedirectBuffer(sys.stderr)
    sys.stderr = stderr_interceptor
    step.report.stderr_interceptor = stderr_interceptor

    stdout_interceptor.active = True
    stderr_interceptor.active = True


def restore_default_configuration():
    """
    Restores the sys.stdout and the sys.stderr buffer streams to their default
    values without regard to what step has currently overridden their values.
    This is useful during cleanup outside of the running execution block
    """

    def restore(target, default_value):
        if target == default_value:
            return default_value

        if not isinstance(target, RedirectBuffer):
            return target

        try:
            target.active = False
            target.close()
        except Exception:
            pass

        return default_value

    sys.stdout = restore(sys.stdout, sys.__stdout__)
    sys.stderr = restore(sys.stderr, sys.__stderr__)


def disable(step: 'projects.ProjectStep'):
    # Restore the print buffer

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    stdout_interceptor = step.report.stdout_interceptor
    if stdout_interceptor:
        stdout_interceptor.active = False
        stdout_interceptor.close()
    step.report.stdout_interceptor = None

    stderr_interceptor = step.report.stderr_interceptor
    if stderr_interceptor:
        stderr_interceptor.active = False
        stderr_interceptor.close()
    step.report.stderr_interceptor = None
