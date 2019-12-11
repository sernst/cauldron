from unittest.mock import MagicMock

from cauldron.session.writing.components import bokeh_component
from cauldron.test import support


def test_bokeh_component_import_error():
    """Should return empty component if bokeh is not install."""
    with support.ImportPatcher() as mocked_importer:
        mocked_importer.error_on = ['bokeh.resources']
        result = bokeh_component.create(MagicMock())

    assert bokeh_component.COMPONENT([], []) == result
