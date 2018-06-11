from unittest.mock import MagicMock
from unittest.mock import patch

import cauldron
from cauldron.cli.commands.steps import actions as step_actions
from cauldron.environ.response import Response
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestStepsCreateStep(scaffolds.ResultsTest):
    """ """

    def test_nameless_step(self):
        """ should convert float index to integer """

        support.create_project(self, 'minneapolis')
        project = cauldron.project.get_internal_project()
        project.naming_scheme = None

        r = Response()
        step_actions.create_step(r, project, '', '', 'This is my step')

        self.assertFalse(r.failed)

    @patch('cauldron.cli.commands.steps.renaming.synchronize_step_names')
    def test_sync_failure(self, synchronize_step_names: MagicMock):
        """ should fail synchronizing step names fails """

        failedResponse = Response().fail(
            'Fake-Fail',
            'FAKE_FAIL'
        ).response
        synchronize_step_names.return_value = failedResponse

        support.create_project(self, 'st-paul')
        project = cauldron.project.get_internal_project()

        r = Response()
        step_actions.create_step(r, project, '', '', 'This is my step')

        self.assertTrue(r.failed)
        self.assertEqual(r.errors[0], failedResponse.errors[0])
