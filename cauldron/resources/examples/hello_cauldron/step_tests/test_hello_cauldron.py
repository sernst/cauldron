from cauldron.steptest import StepTestCase


class TestNotebook(StepTestCase):

    def test_first_attempt(self):
        """Should run the step without error."""
        self.run_step('S01-create-data.py')

    def test_second_attempt(self):
        """Should run the same step a second time without error."""
        self.run_step('S01-create-data.py')
