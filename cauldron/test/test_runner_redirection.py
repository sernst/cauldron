import sys

import cauldron as cd
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.runner import redirection


class TestRunnerRedirection(scaffolds.ResultsTest):
    """ """

    def test_restore(self):
        """ should not cause an exception when already defaulted """

        redirection.restore_default_configuration()

    def test_enable_disable(self):
        """ should properly enable and disable redirection """

        support.create_project(self, 'tonks')
        support.add_step(self)

        project = cd.project.internal_project
        step = project.steps[0]

        redirection.enable(step)
        self.assertIsInstance(sys.stdout, redirection.RedirectBuffer)
        self.assertIsInstance(sys.stderr, redirection.RedirectBuffer)

        redirection.disable(step)
        self.assertNotIsInstance(sys.stdout, redirection.RedirectBuffer)
        self.assertNotIsInstance(sys.stderr, redirection.RedirectBuffer)
        self.assertEqual(sys.stdout, sys.__stdout__)
        self.assertEqual(sys.stderr, sys.__stderr__)

        support.run_command('close')
