import os
from unittest.mock import patch
from unittest.mock import MagicMock

import cauldron as cd
from cauldron.steptest import StepTestCase
from cauldron import steptest


class StepTest(StepTestCase):

    def test_first_step(self):
        """ should not be any null/NaN values in df """

        self.assertIsNone(cd.shared.fetch('df'))
        step = self.run_step('S01-first.py')
        df = cd.shared.df
        self.assertFalse(df.isnull().values.any())

        error_echo = step.echo_error()
        self.assertEqual(error_echo, '')

    def test_second_step(self):
        """ should fail because of an exception raised in the source """

        step = self.run_step('S02-errors.py', allow_failure=True)
        self.assertFalse(step.success)

        error_echo = step.echo_error()
        self.assertGreater(len(error_echo), 0)

    def test_to_strings(self):
        """ should convert list of integers to a list of strings """

        before = [1, 2, 3]
        step = self.run_step('S01-first.py')
        after = step.local.to_strings(before)
        self.assertTrue(step.success)
        self.assertEqual(['1', '2', '3'], after)

    def test_modes(self):
        """ should be testing and not interactive or single run """

        step = self.run_step('S01-first.py')
        self.assertTrue(step.success)
        self.assertTrue(step.local.is_testing)
        self.assertFalse(step.local.is_interactive)
        self.assertFalse(step.local.is_single_run)

    def test_find_in_current_path(self):
        """ should find a project in this file's directory """

        directory = os.path.dirname(os.path.realpath(__file__))
        result = steptest.find_project_directory(directory)
        self.assertEqual(directory, result)

    def test_find_in_parent_path(self):
        """ should find a project in the parent directory """

        directory = os.path.dirname(os.path.realpath(__file__))
        subdirectory = os.path.join(directory, 'fake')
        result = steptest.find_project_directory(subdirectory)
        self.assertEqual(directory, result)

    def test_find_in_grandparent_path(self):
        """ should find a project in the grandparent directory """

        directory = os.path.dirname(os.path.realpath(__file__))
        subdirectory = os.path.join(directory, 'fake', 'fake')
        result = steptest.find_project_directory(subdirectory)
        self.assertEqual(directory, result)

    def test_find_failed_at_root(self):
        """ should return None if top-level directory has no project """

        directory = os.path.dirname(os.path.realpath(__file__))
        subdirectory = os.path.join(directory, 'fake')

        with patch('os.path.dirname', return_value=subdirectory) as func:
            result = steptest.find_project_directory(subdirectory)
            func.assert_called_once_with(subdirectory)
        self.assertIsNone(result)
