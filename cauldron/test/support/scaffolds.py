import os
import tempfile
import unittest
import json

from cauldron import environ
from cauldron.cli import commander


class ResultsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ResultsTest, self).__init__(*args, **kwargs)
        self.results_directory = None
        self.temp_directories = dict()

    def setUp(self):
        super(ResultsTest, self).setUp()
        results_directory = tempfile.mkdtemp(
            prefix='cd-test-results-{}--'.format(self.__class__.__name__)
        )
        self.results_directory = results_directory
        environ.configs.put(results_directory=results_directory, persists=False)
        self.temp_directories = dict()

    def tearDown(self):
        super(ResultsTest, self).tearDown()

        # Close any open project so that it doesn't persist to the next test
        commander.execute('close', '')

        environ.configs.remove('results_directory', include_persists=False)

        environ.systems.remove(self.results_directory)
        self.results_directory = None

        for key, path in self.temp_directories.items():
            environ.systems.remove(path)

    def get_temp_path(self, identifier, *args):
        """

        :param identifier:
        :param args:
        :return:
        """

        if identifier not in self.temp_directories:
            self.temp_directories[identifier] = tempfile.mkdtemp(
                prefix='cd-test-{}'.format(identifier)
            )

        return os.path.realpath(
            os.path.join(self.temp_directories[identifier], *args)
        )

    @classmethod
    def read_flask_response(cls, response):
        """

        :param response:
        :return:
        """

        return json.loads(response.data.decode('utf-8', 'ignore'))


