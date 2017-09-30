import os
import sys
import tempfile
import unittest

import cauldron
from cauldron import environ
from cauldron import cli
from cauldron.cli import commander
from cauldron.cli.commands import close
from cauldron.test.support.messages import Message


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

    def trace(self, *args):
        """
        Traces the results to a temporary buffer that is setup
        :return:
        """

        buffer = ' '.join(['{}'.format(arg) for arg in args])
        sys.__stderr__.write('{}\n'.format(buffer))
        sys.__stderr__.flush()

    def tearDown(self):
        super(ResultsTest, self).tearDown()

        # Close any open project so that it doesn't persist to the next test
        if cauldron.project.internal_project is not None:
            close.execute(cli.make_command_context('close'))

        environ.configs.remove('results_directory', include_persists=False)

        environ.systems.remove(self.results_directory)
        self.results_directory = None

        for key, path in self.temp_directories.items():
            environ.systems.remove(path)

        if cauldron.environ.remote_connection.active:
            commander.execute('disconnect', '')

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

    def assert_has_error_code(self, response, code: str):
        """

        :param response:
        :param code:
        :return:
        """

        self.assertTrue(response.failed, Message(
            'Did not Fail',
            'Response should have failed if expecting an error',
            response=response
        ))

        self.assertGreater(len(response.errors), 0, Message(
            'No Errors Found',
            'There should have been an error in the response',
            response=response
        ))

        codes = [error.code for error in response.errors]

        self.assertIn(code, codes, Message(
            'Error Code Not Found',
            'The error code "{}" was not found in the response errors',
            response=response
        ))

    def assert_no_errors(self, response: environ.Response):
        """ asserts that the response object contains no errors """

        self.assertEqual(0, len(response.errors), Message(
            'Errors found',
            'should not have had errors',
            response=response
        ))

    def assert_has_success_code(self, response, code: str):
        """

        :param response:
        :param code:
        """

        self.assertGreater(len(response.messages), 0, Message(
            'No Messages Found',
            'There should have been a message in the response',
            response=response
        ))

        codes = [message.code for message in response.messages]

        self.assertIn(code, codes, Message(
            'Notification Code Not Found',
            'The code "{}" was not found in the response messages',
            response=response
        ))
