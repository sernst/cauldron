from cauldron.environ import Response
from cauldron.session.projects import Project


def select_step(
        response: Response,
        project: Project,
        step_name: str,
) -> Response:
    """..."""
    if project.select_step(step_name) is None:
        return (
            response
            .update(project=project.kernel_serialize())
            .fail(
                code='NO_SUCH_STEP',
                message='Step "{}" was not found to select.'.format(step_name)
            )
            .console(whitespace=1)
            .response
        )

    return (
        response
        .update(project=project.kernel_serialize())
        .notify(
            kind='SELECTED',
            code='SELECTED',
            message='Step "{}" has been selected.'.format(step_name)
        )
        .console(whitespace=1)
        .response
    )
