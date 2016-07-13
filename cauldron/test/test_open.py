from cauldron.test import support
from cauldron.test.support import scaffolds


class TestOpen(scaffolds.ResultsTest):

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




