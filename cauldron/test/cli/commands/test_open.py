import os
from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron import environ
from cauldron.test import support
from cauldron.test.support import scaffolds

MY_DIRECTORY = os.path.realpath(os.path.dirname(__file__))


class TestOpen(scaffolds.ResultsTest):

    def test_list(self):
        """Should list available command actions without error."""
        support.run_command('open --available')

    @patch('cauldron.cli.commands.open.actions.fetch_last')
    def test_last(self, fetch_last: MagicMock):
        """Should open the last opened project."""
        fetch_last.return_value = os.path.realpath(os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'resources', 'examples', 'seaborn'
        ))
        r = support.run_command('open -l --forget')
        self.assertFalse(r.failed, 'should not have failed')

    def test_open_example(self):
        """..."""
        r = support.open_project(self, '@examples:hello_cauldron')

        self.assertFalse(r.failed, 'should have opened successfully')
        self.assertIn(
            'project', r.data,
            'missing project data from response'
        )
        self.assertEqual(
            len(r.messages), 1,
            'success response message?'
        )

    def test_open_new_project(self):
        """..."""
        r = support.create_project(self, 'test_project')
        r = support.open_project(self, r.data['source_directory'])

        self.assertFalse(r.failed, 'should have opened successfully')
        self.assertIn(
            'project', r.data,
            'missing project data from response'
        )
        self.assertEqual(
            len(r.messages), 1,
            'success response message?'
        )

    def test_autocomplete_flags(self):
        """..."""
        result = support.autocomplete('open --r')
        self.assertEqual(result, ['recent'])

        result = support.autocomplete('open -')
        self.assertGreater(len(result), 3)

    def test_autocomplete_aliases(self):
        """..."""
        result = support.autocomplete('open @fake:')
        self.assertEqual(len(result), 0)

        # Get all directories in the examples folder
        path = environ.paths.resources('examples')
        items = [(e, os.path.join(path, e)) for e in os.listdir(path)]
        items = [e for e in items if os.path.isdir(e[1])]

        result = support.autocomplete('open @examples:')
        self.assertEqual(len(result), len(items))

        result = support.autocomplete('open @ex')
        self.assertIn('examples:', result)


@patch('cauldron.cli.commands.open.environ.paths.home')
def test_autocomplete_home(home: MagicMock):
    """Should autocomplete a home alias."""
    home.return_value = environ.paths.resources('examples', 'hello')
    result = support.autocomplete('open @home:hello')
    assert 0 < len(result)


@patch('cauldron.cli.commands.open.environ.configs.fetch')
def test_autocomplete_custom_alias(
        fetch: MagicMock,
):
    """Should autocomplete a home alias."""
    fetch.return_value = {'foo': {'path': environ.paths.resources('examples')}}
    result = support.autocomplete('open @foo:hello')
    assert 0 < len(result)


def test_autocomplete_custom_explicit_path():
    """Should autocomplete a custom path."""
    result = support.autocomplete(
        'open {}'.format(os.path.join(
            os.path.dirname(MY_DIRECTORY),
            os.path.basename(MY_DIRECTORY)[:2]
        ))
    )
    assert 0 < len(result), """
        Expect at least one result, which is the directory in which
        this test file resides.
        """
