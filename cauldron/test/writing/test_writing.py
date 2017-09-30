from cauldron.test import support
from cauldron.test.support import scaffolds


class TestWriting(scaffolds.ResultsTest):
    """Test suite for the writing module"""

    def test_plotly_project(self):
        """Should properly write a project that has been run"""

        support.open_project(self, '@examples:time-gender')

        response = support.run_command('run')
        self.assertFalse(response.failed)
