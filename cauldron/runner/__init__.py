import os
import sys
import traceback
import types
import typing

import cauldron
from cauldron import environ
from cauldron.reporting.report import Report
from cauldron.session.project import Project


def step(
        project: Project,
        step_report: Report
):
    """

    :param project:
    :param step_report:
    :return:
    """

    file_path = os.path.join(project.source_path, step_report.id)

    os.chdir(os.path.dirname(file_path))
    project.current_step = step_report
    step_report.clear()

    if step_report.id.endswith('.md'):
        with open(file_path, 'r+') as f:
            step_report.markdown(f.read())
        return True

    module = types.ModuleType(step_report.id.split('.')[0])

    project.shared.put(__cauldron_uid__=step_report.id.split('.')[0])

    with open(file_path, 'r+') as f:
        contents = f.read()

    try:
        exec(contents, module.__dict__)
        return True
    except Exception as err:
        summaries = traceback.extract_tb(sys.exc_info()[-1])
        while summaries[0].filename != '<string>':
            summaries.pop(0)

        stack = []
        for s in summaries:
            filename = s.filename
            if filename == '<string>':
                filename = file_path
            stack.append('FILE: {} AT LINE: {}'.format(filename, s.lineno))

        environ.log(
            """
            ERROR: Execution failed in "{filename}"
                {type}: {message}
            {stack}
            """.format(
                filename=step_report.id,
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
        project = Project(source_path=project)

    cauldron.project.load(project)
    return project


def complete(project: typing.Union[Project, None]) -> str:
    """
    Runs the entire project, writes the results files, and returns the URL to
    the report file

    :param project:
    :return:
        Local URL to the report path
    """

    if project is None:
        project = cauldron.project.internal_project

    for s in project.steps:
        if not step(project, s):
            project.write()
            return None

    return project.write()



