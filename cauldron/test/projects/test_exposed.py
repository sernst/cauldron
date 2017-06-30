import cauldron as cd
from cauldron.session import exposed
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestExposed(scaffolds.ResultsTest):
    """

    """

    def test_no_project_defaults(self):
        """Expected defaults when no project exists"""

        ep = exposed.ExposedProject()

        self.assertIsNone(ep.display)
        self.assertIsNone(ep.shared)
        self.assertIsNone(ep.settings)
        self.assertIsNone(ep.title)
        self.assertIsNone(ep.path())

        with self.assertRaises(RuntimeError):
            ep.title = 'Some Title'

    def test_change_title(self):
        """Title should change through exposed project"""

        test_title = 'Some Title'

        support.create_project(self, 'igor')
        cd.project.title = test_title
        self.assertEqual(cd.project.title, test_title)

        support.run_command('close')

    def test_no_step_defaults(self):
        """Exposed step should apply defaults without project"""

        es = exposed.ExposedStep()
        self.assertIsNone(es._step)

    def test_stop_step(self):
        """Should stop the step early"""

        contents = '\n'.join([
            'import cauldron as cd',
            'cd.shared.test = 0',
            'cd.step.breathe()',
            'cd.shared.test = 1',
            'cd.step.stop()',
            'cd.shared.test = 2'
        ])

        support.create_project(self, 'homer')
        support.add_step(self, contents=contents)

        support.run_command('run')
        project = cd.project.internal_project
        step = project.steps[0]

        self.assertEqual(project.shared.fetch('test'), 1)
        self.assertNotEqual(-1, step.dom.find('cd-StepStop'))

        support.run_command('close')

    def test_stop_step_silent(self):
        """Should stop the step early and silently"""

        contents = '\n'.join([
            'import cauldron as cd',
            'cd.shared.test = 0',
            'cd.step.breathe()',
            'cd.shared.test = 1',
            'cd.step.stop(silent=True)',
            'cd.shared.test = 2'
        ])

        support.create_project(self, 'homeritis')
        support.add_step(self, contents=contents)

        support.run_command('run')
        project = cd.project.internal_project
        step = project.steps[0]

        self.assertEqual(project.shared.fetch('test'), 1)
        self.assertEqual(-1, step.dom.find('cd-StepStop'))

        support.run_command('close')
