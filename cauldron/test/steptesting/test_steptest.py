import os
from unittest.mock import MagicMock
from unittest.mock import patch

import cauldron as cd
from cauldron import steptest
from cauldron.steptest import StepTestCase


class TestStepTesting(StepTestCase):
    """Test suite for the step testing module"""

    def test_first_step(self):
        """Should not be any null/NaN values in df"""
        self.assertIsNone(cd.shared.fetch('df'))
        step = self.run_step('S01-first.py')
        df = cd.shared.df
        self.assertFalse(df.isnull().values.any())

        error_echo = step.echo_error()
        self.assertEqual(error_echo, '')

    def test_second_step(self):
        """ 
        Should fail without exception because of an exception raised in the
        source but failure is allowed
        """
        step = self.run_step('S02-errors.py', allow_failure=True)
        self.assertFalse(step.success)

        error_echo = step.echo_error()
        self.assertGreater(len(error_echo), 0)

    def test_second_step_strict(self):
        """ 
        Should fail because of an exception raised in the source when strict
        failure is enforced
        """
        with self.assertRaises(Exception):
            self.run_step('S02-errors.py', allow_failure=False)

    @patch('_testlib.patching_test')
    def test_second_step_with_patching(self, patching_test: MagicMock):
        """Should override the return value with the patch"""
        patching_test.return_value = 12
        cd.shared.value = 42

        self.run_step('S03-lib-patching.py')
        self.assertEqual(cd.shared.result, 12)

    def test_second_step_without_patching(self):
        """Should succeed running the step without patching"""
        cd.shared.value = 42
        self.run_step('S03-lib-patching.py')
        self.assertEqual(cd.shared.result, 42)

    def test_to_strings(self):
        """ should convert list of integers to a list of strings """
        before = [1, 2, 3]
        step = self.run_step('S01-first.py')
        after = step.local.to_strings(before)
        self.assertTrue(step.success)
        self.assertEqual(['1', '2', '3'], after)

    def test_modes(self):
        """Should be testing and not interactive or single run"""
        step = self.run_step('S01-first.py')
        self.assertTrue(step.success)
        self.assertTrue(step.local.is_testing)
        self.assertFalse(step.local.is_interactive)
        self.assertFalse(step.local.is_single_run)

    def test_find_in_current_path(self):
        """Should find a project in this file's directory"""
        directory = os.path.dirname(os.path.realpath(__file__))
        result = steptest.find_project_directory(directory)
        self.assertEqual(directory, result)

    def test_find_in_parent_path(self):
        """Should find a project in the parent directory"""
        directory = os.path.dirname(os.path.realpath(__file__))
        subdirectory = os.path.join(directory, 'fake')
        result = steptest.find_project_directory(subdirectory)
        self.assertEqual(directory, result)

    def test_find_in_grandparent_path(self):
        """Should find a project in the grandparent directory"""
        directory = os.path.dirname(os.path.realpath(__file__))
        subdirectory = os.path.join(directory, 'fake', 'fake')
        result = steptest.find_project_directory(subdirectory)
        self.assertEqual(directory, result)

    def test_find_failed_at_root(self):
        """Should return None if top-level directory has no project"""
        directory = os.path.dirname(os.path.realpath(__file__))
        subdirectory = os.path.join(directory, 'fake')

        with patch('os.path.dirname', return_value=subdirectory) as func:
            with self.assertRaises(FileNotFoundError):
                steptest.find_project_directory(subdirectory)
            func.assert_called_once_with(subdirectory)

    def test_make_temp_path(self):
        """Should make a temp path for testing"""
        temp_path = self.make_temp_path('some-id', 'a', 'b.test')
        self.assertTrue(temp_path.endswith('b.test'))

    def test_no_such_step(self):
        """Should fail if no such step exists"""
        with self.assertRaises(Exception):
            self.run_step('FAKE-STEP.no-exists')

    def test_no_such_project(self):
        """Should fail if no project exists"""
        project = cd.project.get_internal_project()
        cd.project.load(None)

        with self.assertRaises(Exception):
            self.run_step('FAKE')

        cd.project.load(project)

    def test_open_project_fails(self):
        """Should raise Assertion error after failing to open the project"""
        with patch('cauldron.steptest.support.open_project') as open_project:
            open_project.side_effect = RuntimeError('FAKE')
            with self.assertRaises(AssertionError):
                self.open_project()
