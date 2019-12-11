from cauldron.session import projects
from cauldron.session.writing.components import bokeh_component
from cauldron.session.writing.components import definitions
from cauldron.session.writing.components import plotly_component
from cauldron.session.writing.components import project_component
from cauldron.session.writing.components.definitions import COMPONENT
from cauldron.session.writing.components.definitions import WEB_INCLUDE


def _get_components(lib_name: str, project: 'projects.Project') -> COMPONENT:
    if lib_name == 'bokeh':
        return bokeh_component.create(project)

    if lib_name == 'plotly':
        return plotly_component.create(project)

    # Unknown components will just return as empty components. There used
    # to be a shared component type that was removed in 1.0.0, but hadn't
    # been used for a long time before that. If that becomes interesting
    # again old code can be reviewed to see how shared components once
    # worked.
    return COMPONENT([], [])


def get(step: 'projects.ProjectStep') -> COMPONENT:
    """..."""
    return definitions.merge_components(
        project_component.create_many(step.project, step.web_includes),
        *[
            _get_components(name, step.project)
            for name in step.report.library_includes
        ],
    )
