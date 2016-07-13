import os

from cauldron.test import support
from cauldron.test.support import scaffolds


class TestCreate(scaffolds.ResultsTest):

    def test_create_no_args(self):
        """
        """

        r = support.create_project(self, '', '')
        self.assertTrue(r.failed, 'should have failed')

    def test_create_no_path(self):
        """
        """

        r = support.create_project(self, 'test_create', '')
        self.assertTrue(r.failed, 'should have failed')

    def test_create_simple_success(self):
        """
        """

        r = support.create_project(self, 'test_create')

        self.assertFalse(
            r.failed,
            'Failed to create project\n:{}'.format(r.echo())
        )

        self.assertTrue(
            os.path.exists(
                os.path.join(r.data['source_directory'], 'cauldron.json')
            ),
            'Missing cauldron.json in new project folder\n:{}'.format(r.echo())
        )

    def test_create_twice(self):
        """
        """

        r = support.create_project(self, 'test_create')
        r = support.create_project(self, 'test_create')

        self.assertTrue(
            r.failed, 'No second project\n:{}'.format(r.echo())
        )

    def test_create_full_success(self):
        """
        """

        r = support.create_project(
            self, 'test_create',
            title='This is a test',
            summary='More important information goes in this spot',
            author='Kermit the Frog'
        )

        self.assertFalse(
            r.failed,
            'Failed to create project\n:{}'.format(r.echo())
        )

        self.assertTrue(
            os.path.exists(
                os.path.join(r.data['source_directory'], 'cauldron.json')
            ),
            'Missing cauldron.json in new project folder\n:{}'.format(r.echo())
        )



