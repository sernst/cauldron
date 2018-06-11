from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import PropertyMock

import cauldron as cd
from cauldron.session import exposed
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestExposed(scaffolds.ResultsTest):
    """Test suite for the exposed module"""

    def test_no_project_defaults(self):
        """Expected defaults when no project exists"""

        ep = exposed.ExposedProject()

        self.assertIsNone(ep.display)
        self.assertIsNone(ep.shared)
        self.assertIsNone(ep.settings)
        self.assertIsNone(ep.title)
        self.assertIsNone(ep.id)
        self.assertIsNone(ep.path())

        with self.assertRaises(RuntimeError):
            ep.title = 'Some Title'

    def test_change_title(self):
        """Title should change through exposed project"""

        test_title = 'Some Title'

        support.create_project(self, 'igor')
        cd.project.title = test_title
        self.assertEqual(cd.project.title, test_title)

    def test_no_step_defaults(self):
        """Exposed step should apply defaults without project"""

        es = exposed.ExposedStep()
        self.assertIsNone(es._step)

    def test_stop_step_and_halt(self):
        """
        Should stop the step early and not continue running future steps
        """
        support.create_project(self, 'homer')
        support.add_step(self, contents='\n'.join([
            'import cauldron as cd',
            'cd.shared.test = 0',
            'cd.step.breathe()',
            'cd.shared.test = 1',
            'cd.step.stop(halt=True)',
            'cd.shared.test = 2'
        ]))
        support.add_step(self, contents='\n'.join([
            'import cauldron as cd',
            'cd.shared.test = 3'
        ]))

        support.run_command('run')
        project = cd.project.get_internal_project()
        step = project.steps[0]

        self.assertEqual(project.shared.fetch('test'), 1)
        self.assertNotEqual(-1, step.dom.find('cd-StepStop'))

    def test_stop_project(self):
        """
        Should stop the step early and not continue running future steps
        because the project was halted.
        """
        support.create_project(self, 'homer3')
        support.add_step(self, contents='\n'.join([
            'import cauldron as cd',
            'cd.shared.test = 0',
            'cd.step.breathe()',
            'cd.shared.test = 1',
            'cd.project.stop()',
            'cd.shared.test = 2'
        ]))
        support.add_step(self, contents='\n'.join([
            'import cauldron as cd',
            'cd.shared.test = 3'
        ]))

        support.run_command('run')
        project = cd.project.get_internal_project()
        step = project.steps[0]

        self.assertEqual(project.shared.fetch('test'), 1)
        self.assertNotEqual(-1, step.dom.find('cd-StepStop'))

    def test_stop_step_no_halt(self):
        """
        Should stop the step early but continue running future steps
        """
        support.create_project(self, 'homer2')
        support.add_step(self, contents='\n'.join([
            'import cauldron as cd',
            'cd.shared.test = 0',
            'cd.shared.other = 0',
            'cd.step.breathe()',
            'cd.shared.test = 1',
            'cd.step.stop()',
            'cd.shared.test = 2'
        ]))
        support.add_step(self, contents='\n'.join([
            'import cauldron as cd',
            'cd.shared.other = 1'
        ]))

        support.run_command('run')
        project = cd.project.get_internal_project()
        step = project.steps[0]

        self.assertEqual(project.shared.fetch('test'), 1)
        self.assertEqual(project.shared.fetch('other'), 1)
        self.assertNotEqual(-1, step.dom.find('cd-StepStop'))

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
        project = cd.project.get_internal_project()
        step = project.steps[0]

        self.assertEqual(project.shared.fetch('test'), 1)
        self.assertEqual(-1, step.dom.find('cd-StepStop'))

    @patch(
        'cauldron.session.exposed.ExposedProject.internal_project',
        new_callable=PropertyMock
    )
    @patch('time.sleep')
    def test_get_internal_project(
            self,
            sleep: MagicMock,
            internal_project: PropertyMock
    ):
        """Should get internal project on the third attempt"""
        project = exposed.ExposedProject()
        internal_project.side_effect = [None, None, 'test']
        result = project.get_internal_project()
        self.assertEqual('test', result)
        self.assertEqual(2, sleep.call_count)

    @patch(
        'cauldron.session.exposed.ExposedProject.internal_project',
        new_callable=PropertyMock
    )
    @patch('time.time')
    @patch('time.sleep')
    def test_get_internal_project_fail(
            self,
            sleep: MagicMock,
            time_time: MagicMock,
            internal_project: PropertyMock
    ):
        """
        Should fail to get internal project and return None after
        eventually timing out.
        """
        project = exposed.ExposedProject()
        time_time.side_effect = range(20)
        internal_project.return_value = None
        result = project.get_internal_project()
        self.assertIsNone(result)
        self.assertEqual(10, sleep.call_count)
