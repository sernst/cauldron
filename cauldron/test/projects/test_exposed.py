import os
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import cauldron as cd
from cauldron.session import exposed
from cauldron.test import support
from cauldron.test.support import scaffolds

ROOT = 'cauldron.session.exposed'


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

    @patch('{}.ExposedStep._step'.format(ROOT), new_callable=PropertyMock)
    def test_step_properties(self, _step: PropertyMock):
        """Should return values from the internal _step object."""
        now = datetime.utcnow()
        _step.return_value = MagicMock(
            start_time=now,
            end_time=now,
            elapsed_time=0,
            is_visible=True
        )
        es = exposed.ExposedStep()
        self.assertEqual(now, es.start_time)
        self.assertEqual(now, es.end_time)
        self.assertEqual(0, es.elapsed_time)

    @patch('{}.ExposedStep._step'.format(ROOT), new_callable=PropertyMock)
    def test_step_visibility(self, _step: PropertyMock):
        """Should return values from the internal _step object."""
        _step.return_value = MagicMock(is_visible=True)
        es = exposed.ExposedStep()
        self.assertTrue(es.visible)
        es.visible = False
        self.assertFalse(es.visible)

    @patch('{}.ExposedStep._step'.format(ROOT), new_callable=PropertyMock)
    def test_step_stop_aborted(self, _step: PropertyMock):
        """
        Should abort stopping and not raise an error when no internal step
        is available to stop.
        """
        _step.return_value = None
        es = exposed.ExposedStep()
        es.stop()

    @patch('cauldron.session.exposed.ExposedProject.get_internal_project')
    def test_project_stop_aborted(self, get_internal_project: MagicMock):
        """
        Should abort stopping and not raise an error when no internal project
        is available to stop.
        """
        get_internal_project.return_value = None
        ep = exposed.ExposedProject()
        ep.stop()

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

    @patch(
        'cauldron.session.exposed.ExposedStep._step',
        new_callable=PropertyMock
    )
    def test_write_to_console(self, _step: PropertyMock):
        """
        Should write to the console using a write_source function
        call on the internal step report's stdout_interceptor.
        """
        trials = [2, True, None, 'This is a test', b'hello']

        for message in trials:
            _step_mock = MagicMock()
            write_source = MagicMock()
            _step_mock.report.stdout_interceptor.write_source = write_source
            _step.return_value = _step_mock
            step = exposed.ExposedStep()
            step.write_to_console(message)

            args, kwargs = write_source.call_args
            self.assertEqual('{}'.format(message), args[0])

    @patch(
        'cauldron.session.exposed.ExposedStep._step',
        new_callable=PropertyMock
    )
    def test_render_to_console(self, _step: PropertyMock):
        """
        Should render to the console using a write_source function
        call on the internal step report's stdout_interceptor.
        """
        message = '   {{ a }} is not {{ b }}.'

        _step_mock = MagicMock()
        write_source = MagicMock()
        _step_mock.report.stdout_interceptor.write_source = write_source
        _step.return_value = _step_mock
        step = exposed.ExposedStep()
        step.render_to_console(message, a=7, b='happy')

        args, kwargs = write_source.call_args
        self.assertEqual('7 is not happy.', args[0])

    @patch(
        'cauldron.session.exposed.ExposedStep._step',
        new_callable=PropertyMock
    )
    def test_write_to_console_fail(self, _step: PropertyMock):
        """
        Should raise a ValueError when there is no current step to operate
        upon by the write function call.
        """
        _step.return_value = None
        step = exposed.ExposedStep()
        with self.assertRaises(ValueError):
            step.write_to_console('hello')

    @patch('cauldron.render.stack.get_formatted_stack_frame')
    def test_render_stop_display(self, get_formatted_stack_frame: MagicMock):
        """Should render stop display without error"""
        get_formatted_stack_frame.return_value = [
            {'filename': 'foo'},
            {'filename': 'bar'},
            {'filename': os.path.realpath(exposed.__file__)}
        ]
        step = MagicMock()
        exposed.render_stop_display(step, 'FAKE')
        self.assertEqual(1, step.report.append_body.call_count)

    @patch('cauldron.templating.render_template')
    @patch('cauldron.render.stack.get_formatted_stack_frame')
    def test_render_stop_display_error(
            self,
            get_formatted_stack_frame: MagicMock,
            render_template: MagicMock
    ):
        """
        Should render an empty stack frame when the stack data is invalid.
        """
        get_formatted_stack_frame.return_value = None
        step = MagicMock()
        exposed.render_stop_display(step, 'FAKE')
        self.assertEqual({}, render_template.call_args[1]['frame'])

    def test_project_path(self):
        """Should create an absolute path within the project"""
        ep = exposed.ExposedProject()
        project = MagicMock()
        project.source_directory = os.path.realpath(os.path.dirname(__file__))
        ep.load(project)
        result = ep.path('hello.md')
        self.assertTrue(result.endswith('{}hello.md'.format(os.sep)))
