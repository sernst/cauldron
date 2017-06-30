import sys
import traceback

from cauldron import environ
from cauldron.session import projects


def get_stack_frames(error_stack: bool = True) -> list:
    """
    Returns a list of the current stack frames, which are pruned focus on the
    Cauldron code where the relevant information resides.
    """

    cauldron_path = environ.paths.package()
    resources_path = environ.paths.resources()
    frames = (
        list(traceback.extract_tb(sys.exc_info()[-1]))
        if error_stack else
        traceback.extract_stack()
    ).copy()

    def is_cauldron_code(test_filename: str) -> bool:
        if not test_filename or not test_filename.startswith(cauldron_path):
            return False

        if test_filename.startswith(resources_path):
            return False

        return True

    while len(frames) > 1 and is_cauldron_code(frames[0].filename):
        frames.pop(0)

    return frames


def format_stack_frame(stack_frame, project: 'projects.Project') -> dict:
    """
    Formats a raw stack frame into a dictionary formatted for render 
    templating and enriched with information from the currently open project.

    :param stack_frame:
        A raw stack frame to turn into an enriched version for templating.
    :param project:
        The currently open project, which is used to contextualize stack
        information with project-specific information.
    :return:
        A dictionary containing the enriched stack frame data.
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


def get_formatted_stack_frame(
        project: 'projects.Project',
        error_stack: bool = True
) -> list:
    """
    Returns a list of the stack frames formatted for user display that has
    been enriched by the project-specific data. 
    
    :param project:
        The currently open project used to enrich the stack data.
    :param error_stack:
        Whether or not to return the error stack. When True the stack of the
        last exception will be returned. If no such exception exists, an empty
        list will be returned instead. When False the current execution stack
        trace will be returned.
    """

    return [
        format_stack_frame(f, project)
        for f in get_stack_frames(error_stack=error_stack)
    ]
