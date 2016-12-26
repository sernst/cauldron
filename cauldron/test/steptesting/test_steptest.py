import cauldron as cd
from cauldron.steptest import StepTestCase


class StepTest(StepTestCase):

    def test_first_step(self):
        """ should not be any null/NaN values in df """

        self.assertIsNone(cd.shared.fetch('df'))
        self.run_step('S01-first.py')
        df = cd.shared.df
        self.assertFalse(df.isnull().values.any())

    def test_to_strings(self):
        """ should convert list of integers to a list of strings """

        before = [1, 2, 3]
        step = self.run_step('S01-first.py')
        after = step.local.to_strings(before)
        self.assertEqual(['1', '2', '3'], after)

    def test_modes(self):
        """ should be testing and not interactive or single run """

        step = self.run_step('S01-first.py')
        self.assertTrue(step.local.is_testing)
        self.assertFalse(step.local.is_interactive)
        self.assertFalse(step.local.is_single_run)
