from cauldron.environ import Response
from cauldron.session.projects import Project


def select_step(
        response: Response,
        project: Project,
        step_name: str,
) -> Response:
    for step in project.steps:
        step.is_selected = step.name == step_name

    return (
        response
        .update(
            project=project.kernel_serialize()
        )
        .notify(
            kind='SELECTED',
            code='SELECTED',
            message='Step "{}" has been selected.'.format(step_name)
        )
        .console(whitespace=1)
        .response
    )
