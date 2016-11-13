from cauldron.session import projects
from cauldron.session.writing.components import bokeh_component
from cauldron.session.writing.components import definitions
from cauldron.session.writing.components import plotly_component
from cauldron.session.writing.components import project_component
from cauldron.session.writing.components import shared_component
from cauldron.session.writing.components.definitions import COMPONENT
from cauldron.session.writing.components.definitions import WEB_INCLUDE


def get(step: 'projects.ProjectStep') -> COMPONENT:
    """

    :param step:
    :return:
    """

    def get_components(lib_name: str) -> COMPONENT:
        if lib_name == 'bokeh':
            return bokeh_component.create(step.project)

        if lib_name == 'plotly':
            return plotly_component.create(step.project)

        return shared_component.create(lib_name)

    components = list(map(get_components, step.report.library_includes))

    return definitions.merge_components(
        project_component.create_many(step.project, step.web_includes),
        *components,
    )



