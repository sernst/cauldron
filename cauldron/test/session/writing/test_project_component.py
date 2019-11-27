import os
from unittest.mock import MagicMock

from cauldron.session.writing.components import project_component


def test_project_component_does_not_exist():
    """Should return empty component when source does not exist."""
    project = MagicMock()
    project.source_directory = os.path.realpath(os.path.dirname(__file__))
    result = project_component.create(project, 'fake-include-path')
    assert project_component.COMPONENT([], []) == result
