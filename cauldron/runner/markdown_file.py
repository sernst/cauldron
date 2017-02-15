import cauldron
from cauldron import templating
from cauldron.session import projects


def run(
        project: 'projects.Project',
        step: 'projects.ProjectStep'
) -> dict:
    """
    Runs the markdown file and renders the contents to the notebook display

    :param project:
    :param step:
    :return:
        A run response dictionary containing
    """

    with open(step.source_path, 'r') as f:
        code = f.read()

    try:
        cauldron.display.markdown(code, **project.shared.fetch(None))
        return {'success': True}
    except Exception as err:
        return dict(
            success=False,
            html_message=templating.render_template(
                'markdown-error.html',
                error=err
            )
        )
