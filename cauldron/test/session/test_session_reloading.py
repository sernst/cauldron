from datetime import datetime
from email.mime import text as mime_text

import cauldron as cd
from cauldron.session import reloading
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message


class TestSessionReloading(scaffolds.ResultsTest):
    """

    """

    def setUp(self):
        super(TestSessionReloading, self).setUp()
        support.run_command('close')

    def test_watch_bad_argument(self):
        """

        :return:
        """

        self.assertFalse(
            reloading.refresh(datetime, force=True),
            Message('Should not reload not a module')
        )

    def test_watch_good_argument(self):
        """

        :return:
        """

        self.assertTrue(
            reloading.refresh('datetime', force=True),
            Message('Should reload the datetime module')
        )

    def test_watch_not_needed(self):
        """

        :return:
        """

        support.create_project(self, 'betty')
        support.add_step(self)
        project = cd.project.internal_project
        project.current_step = project.steps[0]

        self.assertFalse(
            reloading.refresh(mime_text),
            Message('Should not reload if the step has not been run before')
        )

        support.run_command('run')

        project.current_step = project.steps[0]

        self.assertFalse(
            reloading.refresh(mime_text),
            Message('Should not reload if module has not changed recently')
        )

        project.current_step = None
        support.run_command('close')

    def test_watch_recursive(self):
        """

        :return:
        """

        self.assertTrue(
            reloading.refresh('email', recursive=True, force=True),
            Message('Should reload the email module')
        )

