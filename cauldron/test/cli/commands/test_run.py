from unittest.mock import patch
from unittest.mock import MagicMock

import cauldron
from cauldron import environ
from cauldron.environ.response import Response
from cauldron import cli
from cauldron.cli import commander
from cauldron.cli.commands import run
from cauldron.test.support import scaffolds
from cauldron.test import support


class TestRun(scaffolds.ResultsTest):

    def test_run_example(self):
        """
        """

        support.open_project(self, '@examples:hello_text')

        r = environ.Response()
        commander.execute('run', '', r)
        r.thread.join()

        self.assertFalse(r.failed)

    def test_run_step_example(self):
        """
        """

        support.open_project(self, '@examples:hello_cauldron')

        r = environ.Response()
        commander.execute('run', '.', r)
        r.thread.join()

        self.assertFalse(r.failed)

    def test_run_in_parts(self):
        """ """

        support.open_project(self, '@examples:hello_cauldron')

        r = environ.Response()
        commander.execute('run', 'S01-create-data.py', r)
        r.thread.join()
        self.assertFalse(r.failed)

        r = environ.Response()
        commander.execute('run', 'S02-plot-data.py', r)
        r.thread.join()
        self.assertFalse(r.failed)

    def test_run_bokeh(self):
        """ """

        support.open_project(self, '@examples:bokeh')

        r = environ.Response()
        commander.execute('run', '', r)
        r.thread.join()

        self.assertFalse(r.failed)

    def test_autocomplete_flags(self):
        """ should return list of short flags """

        result = support.autocomplete('run S01.py -')
        self.assertGreater(len(result), 2)
        self.assertIn('-', result)

    def test_autocomplete_long_flags(self):
        """ should return list of long flags """

        result = support.autocomplete('run S01.py --')
        self.assertGreater(len(result), 2)
        self.assertIn('force', result)

    def test_autocomplete_nothing(self):
        """ should return empty autocomplete when no option started """

        result = support.autocomplete('run')
        self.assertEqual(len(result), 0)

    def test_autocomplete(self):
        """ should autocomplete step name """

        support.create_project(self, 'crystal')
        support.add_step(self)

        step = cauldron.project.get_internal_project().steps[0]

        result = support.autocomplete('run {}'.format(step.filename[:2]))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], step.filename)

    def test_run_no_project(self):
        """ should abort if no project is open """

        r = environ.Response()
        run.execute(context=cli.make_command_context(
            name=run.NAME,
            response=r
        ))

        self.assert_has_error_code(r, 'NO_OPEN_PROJECT')

    def test_multiple_steps(self):
        """ should run multiple named steps """

        support.create_project(self, 'robinsdale')
        support.add_step(self)
        support.add_step(self)
        support.add_step(self)

        project = cauldron.project.get_internal_project()
        step_names = [s.filename for s in project.steps[:-1]]

        r = run.execute(
            context=cli.make_command_context(name=run.NAME),
            step=step_names
        )

        self.assertFalse(r.failed)
        self.assertFalse(project.steps[0].is_dirty())
        self.assertFalse(project.steps[1].is_dirty())
        self.assertTrue(project.steps[2].is_dirty())

    def test_single_step(self):
        """ should run single step only """

        support.create_project(self, 'white-bear-lake')
        support.add_step(self)
        support.add_step(self)
        support.add_step(self)

        project = cauldron.project.get_internal_project()

        r = run.execute(
            context=cli.make_command_context(name=run.NAME),
            single_step=True
        )

        self.assertFalse(r.failed)
        self.assertFalse(project.steps[0].is_dirty())
        self.assertTrue(project.steps[1].is_dirty())
        self.assertTrue(project.steps[2].is_dirty())

        r = run.execute(
            context=cli.make_command_context(name=run.NAME),
            single_step=True
        )

        self.assertFalse(r.failed)
        self.assertFalse(project.steps[0].is_dirty())
        self.assertFalse(project.steps[1].is_dirty())
        self.assertTrue(project.steps[2].is_dirty())

    def test_run_count(self):
        """ should run single step only """

        support.create_project(self, 'eagan')
        support.add_step(self)
        support.add_step(self)
        support.add_step(self)

        project = cauldron.project.get_internal_project()

        r = run.execute(
            context=cli.make_command_context(name=run.NAME),
            step=['2']
        )

        self.assertFalse(r.failed)
        self.assertFalse(project.steps[0].is_dirty())
        self.assertFalse(project.steps[1].is_dirty())

    def test_repeats(self):
        """ should not repeat run multiple named steps in a single run """

        support.create_project(self, 'eden-prairie')
        support.add_step(self)
        support.add_step(self)
        support.add_step(self)

        project = cauldron.project.get_internal_project()
        step_names = [s.filename for s in project.steps[:-1]]
        step_names.append(project.steps[0].filename)

        r = run.execute(
            context=cli.make_command_context(name=run.NAME),
            step=step_names
        )

        self.assertFalse(r.failed)
        self.assertFalse(project.steps[0].is_dirty())
        self.assertFalse(project.steps[1].is_dirty())
        self.assertTrue(project.steps[2].is_dirty())

    def test_repeat_additions(self):
        """ should not repeat run multiple named steps in a single run """

        support.create_project(self, 'plymouth')
        support.add_step(self)
        support.add_step(self)
        support.add_step(self)

        project = cauldron.project.get_internal_project()
        step_names = [
            project.steps[1].filename,
            project.steps[0].filename,
            '..'
        ]

        r = run.execute(
            context=cli.make_command_context(name=run.NAME),
            step=step_names
        )

        self.assertFalse(r.failed)
        self.assertFalse(project.steps[0].is_dirty())
        self.assertTrue(project.steps[1].is_dirty())
        self.assertTrue(project.steps[2].is_dirty())

    def test_no_such_step(self):
        """ should fail if unable to find a step """

        support.create_project(self, 'fairfield')
        support.add_step(self)
        support.add_step(self)

        project = cauldron.project.get_internal_project()
        step_names = [s.filename for s in project.steps]
        step_names.append('FAKE-STEP')

        r = run.execute(
            context=cli.make_command_context(name=run.NAME),
            step=step_names
        )

        self.assert_has_error_code(r, 'MISSING_STEP')

    def test_run_remote(self):
        """ should successfully run remote project """

        support.create_project(self, 'rhino')
        support.add_step(self, contents='print("hello!")')

        source_directory = (
            cauldron.project.get_internal_project().source_directory
        )

        opened_response = support.run_remote_command(
            'open "{}"'.format(source_directory)
        )
        self.assertTrue(opened_response.success)

        run_response = support.run_remote_command('run')
        self.assertTrue(run_response.success)

    @patch('cauldron.cli.commands.sync.execute')
    def test_run_remote_sync_fail(self, sync_execute: MagicMock):
        """ should fail if the remote sync was not successful """

        sync_execute.return_value = Response().fail().response

        support.create_project(self, 'pig')
        support.add_step(self, contents='print("hello!")')

        source_directory = (
            cauldron.project.get_internal_project().source_directory
        )

        opened_response = support.run_remote_command(
            'open "{}"'.format(source_directory)
        )
        self.assertTrue(opened_response.success)

        run_response = support.run_remote_command('run')
        self.assertTrue(run_response.failed)
