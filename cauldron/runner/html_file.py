from cauldron import render
from cauldron import templating
from cauldron.session import projects


def run(
        project: 'projects.Project',
        step: 'projects.ProjectStep'
) -> dict:
    """

    :param project:
    :param step:
    :return:
    """

    with open(step.source_path, 'r') as f:
        code = f.read()

    step.report.append_body(render.html(templating.render(
        template=code,
        **project.shared.fetch(None)
    )))

    return {'success': True}
