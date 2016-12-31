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

    print_redirect = RedirectBuffer(sys.stdout)
    sys.stdout = print_redirect
    step.report.print_buffer = print_redirect


def disable(step: 'projects.ProjectStep'):
    # Restore the print buffer

    print_redirect = step.report.print_buffer

    sys.stdout = sys.__stdout__
    print(step.report.flush_prints())
    print_redirect.close()
    step.report.print_buffer = None
