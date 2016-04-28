import os
import sys
import traceback
import types
import typing
import time

import cauldron
from cauldron import environ
from cauldron.session.project import Project
from cauldron.session.project import ProjectStep


def step(
        project: Project,
        project_step: typing.Union[ProjectStep, str]
):
    """

    :param project:
    :param project_step:
    :return:
    """

    if isinstance(project_step, str):
        found = False
        for ps in project.steps:
            if ps.id != project_step:
                break
            project_step = ps
            found = True
            break

        if not found:
            return

    file_path = os.path.join(project.source_directory, project_step.id)

    os.chdir(os.path.dirname(file_path))
    project.current_step = project_step
    project_step.report.clear()

    if project_step.id.endswith('.md'):
        with open(file_path, 'r+') as f:
            project_step.report.markdown(f.read())
        return True

    module = types.ModuleType(project_step.report.id.split('.')[0])

    project.shared.put(__cauldron_uid__=project_step.report.id.split('.')[0])

    with open(file_path, 'r+') as f:
        contents = f.read()

    try:
        exec(contents, module.__dict__)
        project_step.last_modified = time.time()
        return True
    except Exception as err:
        summaries = traceback.extract_tb(sys.exc_info()[-1])
        while summaries[0].filename != '<string>':
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

        if not step(project, ps):
            project.write()
            environ.log('[{}]: Failed to update'.format(ps.id))
            return None

        environ.log('[{}]: Updated'.format(ps.id))

    return project.write()

