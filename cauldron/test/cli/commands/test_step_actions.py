import os

import cauldron
from cauldron.environ.response import Response
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message
from cauldron.cli.commands.steps import actions as step_actions


class TestStepActions(scaffolds.ResultsTest):
    """ """

    def test_index_from_location_float(self):
        """ Should convert float index to integer """

        result = step_actions.index_from_location(None, None, 12.2)
        self.assertEqual(result, 12)
        self.assertIsInstance(result, int)

    def test_index_from_location_default(self):
        """ Should return default if unable to parse location """

        result = step_actions.index_from_location(None, None, None, 42)
        self.assertEqual(result, 42)

    def test_index_from_location_default_final(self):
        """ Should return default if unable to parse location """

        result = step_actions.index_from_location(None, None, self, 42)
        self.assertEqual(result, 42)

    def test_index_from_location_bad_string(self):
        """ should return default value if bad string is supplied """

        support.create_project(self, 'ray')
        project = cauldron.project.get_internal_project()

        result = step_actions.index_from_location(None, project, '12s', 42)
        self.assertEqual(result, 42)

    def test_index_from_location_step_name(self):
        """ should return index from step name if supplied """

        support.create_project(self, 'bradbury')
        support.add_step(self)
        project = cauldron.project.get_internal_project()
        step = project.steps[0]

        result = step_actions.index_from_location(None, project, step.filename)
        self.assertEqual(result, 1)

    def test_mute_no_such_step(self):
        """ should fail to mute a step that does not exist """

        support.create_project(self, 'lewis')
        project = cauldron.project.get_internal_project()

        r = Response()
        step_actions.toggle_muting(r, project, 'not-a-step')

        self.assertTrue(r.failed)
        self.assertEqual(r.errors[0].code, 'NO_SUCH_STEP')

    def test_toggle_muting(self):
        """ should reverse the muted state of the step """

        support.create_project(self, 'carrol')
        support.add_step(self)

        project = cauldron.project.get_internal_project()
        step = project.steps[0]
        self.assertFalse(step.is_muted)

        r = Response()
        step_actions.toggle_muting(r, project, step.filename)
        self.assertTrue(step.is_muted)

        r = Response()
        step_actions.toggle_muting(r, project, step.filename)
        self.assertFalse(step.is_muted)
