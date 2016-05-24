import os
import sys
import traceback
import types
import typing
import time
import functools

import cauldron
from cauldron import environ
from cauldron.session.project import Project
from cauldron.session.project import ProjectStep
from cauldron import templating


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

    text = '\t'.join([str(x) for x in args])
    project_step.report.text(text, preformatted=True)

    print(*args, sep=sep, end='\n', file=file, flush=flush)


def step(
        project: Project,
        project_step: typing.Union[ProjectStep, str],
        force: bool = False
) -> bool:
    """

    :param project:
    :param project_step:
    :param force:
    :return:
    """

    if isinstance(project_step, str):
        found = False
        for ps in project.steps:
            if ps.id == project_step:
                project_step = ps
                found = True
                break

        if not found:
            return False

    file_path = project_step.source_path
    if not os.path.exists(file_path):
        environ.log('[{id}]: Not found "{path}"'.format(
            id=project_step.id,
            path=file_path
        ))
        return False

    if not force and not project_step.is_dirty():
        environ.log('[{}]: Nothing to update'.format(project_step.id))
        return True

    os.chdir(os.path.dirname(file_path))
    project.current_step = project_step
    project_step.report.clear()

    with open(file_path, 'r+') as f:
        code = f.read()

    # Set the top-level display and cache values to the current project values
    # before running the step for availability within the step scripts
    cauldron.display = cauldron.project.display
    cauldron.shared = cauldron.project.shared

    # Mark the downstream steps as dirty because this one has run
    [x.mark_dirty(True) for x in project.steps[(project_step.index + 1):]]

    if file_path.endswith('.md'):
        project_step.report.markdown(code, **project.shared.fetch(None))
        project_step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(project_step.id))
        project_step.mark_dirty(False)
        return True

    if file_path.endswith('.html'):
        project_step.report.html(templating.render(
            template=code,
            **project.shared.fetch(None)
        ))
        project_step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(project_step.id))
        project_step.mark_dirty(False)
        return True

    module = types.ModuleType(project_step.report.id.split('.')[0])

    # Add the file attribute
    setattr(module, '__file__', file_path)

    # Create a print equivalent function that also writes the output to the
    # project page
    setattr(module, 'print', functools.partial(step_print, project_step))

    project.shared.put(__cauldron_uid__=project_step.report.id.split('.')[0])

    try:
        exec(code, module.__dict__)
        project_step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(project_step.id))
        project_step.mark_dirty(False)
        return True
    except Exception as err:
        environ.log('[{}]: Failed to update'.format(project_step.id))
        summaries = traceback.extract_tb(sys.exc_info()[-1])
        while summaries and summaries[0].filename != '<string>':
            summaries.pop(0)

        stack = []
        for ps in summaries:
            filename = ps.filename
            if filename == '<string>':
                filename = file_path
            stack.append('FILE: {} AT LINE: {}'.format(filename, ps.lineno))

        environ.log(
            """
            ERROR: Execution failed in "{filename}"
                {type}: {message}
            {stack}
            """.format(
                filename=project_step.report.id,
                type=err.__class__.__name__,
                message=err,
                stack='\n'.join(stack)
            )
        )


def initialize(project: typing.Union[str, Project]):
    """

    :param project:
    :return:
    """

    if isinstance(project, str):
        project = Project(source_directory=project)

    cauldron.project.load(project)
    return project


def section(
        project: typing.Union[Project, None],
        starting: ProjectStep = None,
        limit: int = 1
) -> str:
    """

    :param project:
    :param starting:
    :param limit:
    :return:
    """

    if project is None:
        project = cauldron.project.internal_project

    starting_index = 0
    if starting:
        starting_index = project.steps.index(starting)
    count = 0

    for ps in project.steps:
        if count >= limit:
            break

        if ps.index < starting_index:
            continue

        if count == 0 and not ps.is_dirty():
            continue

        if not step(project, ps):
            project.write()
            return None

        count += 1

    return project.write()


def complete(
        project: typing.Union[Project, None],
        starting: ProjectStep = None,
        force: bool = False,
        limit: int = -1
) -> str:
    """
    Runs the entire project, writes the results files, and returns the URL to
    the report file

    :param project:
    :param starting:
    :param force:
    :param limit:
    :return:
        Local URL to the report path
    """

    if project is None:
        project = cauldron.project.internal_project

    starting_index = 0
    if starting:
        starting_index = project.steps.index(starting)
    count = 0

    for ps in project.steps:
        if 0 < limit <= count:
            break

        if ps.index < starting_index:
            continue

        if not force and not ps.is_dirty():
            if limit < 1:
                environ.log('[{}]: Nothing to update'.format(ps.id))
            continue

        count += 1

        if not step(project, ps, force=True):
            project.write()
            return None

    return project.write()

