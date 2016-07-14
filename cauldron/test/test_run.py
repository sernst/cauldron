from cauldron import environ
from cauldron.cli import commander
from cauldron.test.support import scaffolds
from cauldron.test import support


class TestRun(scaffolds.ResultsTest):

    def test_run_example(self):
        """
        """

        support.open_project(self, '@examples:hello_text')

        r = environ.Response()
        commander.execute('run', '', r)

        self.assertFalse(r.failed)
        support.run_command('close')

    def test_run_step_example(self):
        """
        """

        support.open_project(self, '@examples:hello_cauldron')

        r = environ.Response()
        commander.execute('run', '.', r)

        self.assertFalse(r.failed)
        support.run_command('close')

    def test_run_in_parts(self):
        """
        """

        support.open_project(self, '@examples:hello_cauldron')

        r = environ.Response()
        commander.execute('run', 'create_data.py', r)
        self.assertFalse(r.failed)

        r = environ.Response()
        commander.execute('run', 'plot_data.py', r)
        self.assertFalse(r.failed)
        support.run_command('close')

    def test_run_bokeh(self):
        """
        """

        support.open_project(self, '@examples:bokeh')

        r = environ.Response()
        commander.execute('run', '', r)

        self.assertFalse(r.failed)
        support.run_command('close')
