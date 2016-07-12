import os
import tempfile
import unittest

from cauldron import environ


class ResultsTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ResultsTest, self).__init__(*args, **kwargs)
        self.results_directory = None
        self.temp_directories = dict()

    def setUp(self):
        super(ResultsTest, self).setUp()
        results_directory = tempfile.mkdtemp(prefix='cauldron_test')
        environ.configs.put(results_directory=results_directory)
        self.temp_directories = dict()

    def tearDown(self):
        super(ResultsTest, self).tearDown()
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
                prefix='cauldron_test_{}'.format(identifier)
            )

        return os.path.realpath(
            os.path.join(self.temp_directories[identifier], *args)
        )



