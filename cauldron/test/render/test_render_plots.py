from unittest.mock import MagicMock

from cauldron.test import support
from cauldron.render import plots


def test_pyplot_bs4_error():
    """Should render import error if bs4 is not installed."""
    with support.ImportPatcher() as mocked_importer:
        mocked_importer.error_on = ['bs4']
        result = plots.pyplot()

    assert 'The beatifulsoup4 library is needed' in result


def test_pyplot_pyplot_error():
    """Should render import error if matplotlib is not installed."""
    with support.ImportPatcher() as mocked_importer:
        mocked_importer.error_on = ['matplotlib']
        result = plots.pyplot()

    assert 'matplotlib' in result


def test_pyplot_no_figure():
    """Should create default render if no figure is specified."""
    result = plots.pyplot(aspect_ratio=[4, 3])
    assert result is not None


def test_bokeh_plot_import_error():
    """Should render bokeh import error if library not installed."""
    with support.ImportPatcher() as mocked_importer:
        mocked_importer.error_on = ['bokeh']
        result = plots.bokeh_plot(MagicMock())

    assert 'bokeh' in result
