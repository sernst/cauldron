import os

from cauldron import environ
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestOpen(scaffolds.ResultsTest):

    def test_list(self):
        """

        :return:
        """

        support.run_command('open --available')

    def test_last(self):
        """

        :return:
        """

        support.run_command('open @examples:seaborn')
        support.run_command('close')
        r = support.run_command('open -l')
        self.assertFalse(r.failed, 'should not have failed')

    def test_open_example(self):
        """
        """

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
        """
        """

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
        """

        :return:
        """

        result = support.autocomplete('open --r')
        self.assertEqual(result, ['recent'])

        result = support.autocomplete('open -')
        self.assertGreater(len(result), 3)

    def test_autocomplete_aliases(self):
        """

        :return:
        """

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
