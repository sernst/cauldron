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

    file_path = os.path.join(project.source_directory, project_step.id)

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
    project_step.code = code

    if project_step.id.endswith('.md'):
        project_step.report.markdown(code, **project.shared.fetch(None))
        project_step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(project_step.id))
        return True

    if project_step.id.endswith('.html'):
        project_step.report.html(templating.render(
            template=code,
            **project.shared.fetch(None)
        ))
        project_step.last_modified = time.time()
        environ.log('[{}]: Updated'.format(project_step.id))
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


def complete(
        project: typing.Union[Project, None],
        starting: ProjectStep = None,
        force: bool = False
) -> str:
    """
    Runs the entire project, writes the results files, and returns the URL to
    the report file

    :param project:
    :param starting:
    :param force:
    :return:
        Local URL to the report path
    """

    if project is None:
        project = cauldron.project.internal_project

    starting_index = 0
    if starting:
        starting_index = project.steps.index(starting)
    active = False

    for ps in project.steps:
        if ps.index < starting_index:
            continue

        if not force and not active and not ps.is_dirty():
            environ.log('[{}]: Nothing to update'.format(ps.id))
            continue
        active = True

        if not step(project, ps, force=True):
            project.write()
            return None

    return project.write()

