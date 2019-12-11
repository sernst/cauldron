from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.session.writing.components import plotly_component
from cauldron.test.support import scaffolds


def _fake_import(*args, **kwargs):
    raise ImportError('Fake Error')


class TestPlotlyComponent(scaffolds.ResultsTest):
    """..."""

    def test_import_error(self):
        """..."""
        with patch('builtins.__import__') as import_func:
            import_func.side_effect = _fake_import
            component = plotly_component.create(MagicMock())

        self.assertEqual(len(component.files), 0)
        self.assertEqual(len(component.includes), 0)

    def test_version_one_import_error(self):
        """..."""
        with patch('builtins.__import__') as import_func:
            import_func.side_effect = _fake_import
            result = plotly_component.get_version_one_path()

        self.assertIsNone(result)

    def test_version_one(self):
        """..."""
        result = plotly_component.get_version_one_path()
        self.assertIsNotNone(result)

    def test_version_two_import_error(self):
        """..."""
        with patch('builtins.__import__') as import_func:
            import_func.side_effect = _fake_import
            result = plotly_component.get_version_two_path()

        self.assertIsNone(result)

    def test_version_two(self):
        """..."""
        result = plotly_component.get_version_two_path()
        self.assertIsNotNone(result)
