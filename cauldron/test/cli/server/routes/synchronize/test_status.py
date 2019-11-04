import os

import cauldron
from cauldron.cli.server.routes.synchronize import status
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message


MY_PATH = os.path.realpath(__file__)
MY_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class TestStatus(scaffolds.ResultsTest):

    def test_of_file_missing(self):
        """Should return empty result for file that does not exist."""

        path = os.path.join(MY_DIRECTORY, 'fictional.file')
        result = status.of_file(path)
        self.assertEqual(result['modified'], -1)
        self.assertEqual(result['path'], path)

    def test_of_file(self):
        """Should return valid result for my file."""

        result = status.of_file(MY_PATH)
        self.assertNotEqual(result['modified'], -1)
        self.assertEqual(result['path'], MY_PATH)

    def test_of_directory(self):
        """Should return status information for my directory."""

        results = status.of_directory(MY_DIRECTORY)
        self.assertTrue('__init__.py' in results)
        self.assertTrue(os.path.basename(__file__) in results)

        for key, result in results.items():
            self.assertNotEqual(result['modified'], -1)

    def test_of_project(self):
        """Should return information about the project."""
        support.create_project(self, 'eric')
        project = cauldron.project.get_internal_project()
        results = status.of_project(project)

        self.assertEqual(len(results['libraries']), 3)
        self.assertEqual(len(results['project'].keys()), 2, """
            Expect one entry for cauldron.json and one entry for the S01.py
            step created by default with a new project.
            """)
