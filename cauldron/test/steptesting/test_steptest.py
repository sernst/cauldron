import cauldron as cd
from cauldron.steptest import StepTestCase


class StepTest(StepTestCase):

    def test_first_step(self):
        """ df should be in shared variables """

        self.assertIsNone(cd.shared.fetch('df'))
        self.run_step('S01-first.py')
        self.assertIsNotNone(cd.shared.fetch('df'))
