import os
import uuid

from cauldron.cli.commands.steps import renaming as step_support
from cauldron.environ import Response
from cauldron.session import projects


def remove_step(
        response: Response,
        project: 'projects.Project',
        name: str,
        keep_file: bool = False
) -> Response:
    """

    :param response:
    :param project:
    :param name:
    :param keep_file:
    :return:
    """

    step = project.remove_step(name)
    if not step:
        return response.fail(
            code='NO_SUCH_STEP',
            message='Step "{}" not found. Unable to remove.'.format(name)
        ).kernel(
            name=name
        ).console(
            whitespace=1
        ).response

    project.save()
    project.write()

    if not keep_file:
        os.remove(step.source_path)

    res = step_support.synchronize_step_names(project)
    response.consume(res)
    if response.failed:
        return response

    step_renames = res.returned

    removed_name = 'REMOVED--{}'.format(uuid.uuid4())
    step_renames[name] = dict(
        name=removed_name,
        title=''
    )

    step_changes = [dict(
        name=removed_name,
        filename=step.filename,
        action='removed'
    )]

    return response.update(
        project=project.kernel_serialize(),
        step_changes=step_changes,
        step_renames=step_renames
    ).notify(
        kind='SUCCESS',
        code='STEP_REMOVED',
        message='Removed "{}" step from project'.format(name)
    ).console(
        whitespace=1
    ).response
