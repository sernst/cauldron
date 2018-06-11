import os
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron.environ.response import Response
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.cli.commands import export


class TestExport(scaffolds.ResultsTest):
    """

    """

    def test_exporting(self):
        """ should successfully export project """

        support.run_command('open @examples:pyplot')
        support.run_command('run')

        path = self.get_temp_path('exporting')
        folder_name = 'exported-results'
        r = support.run_command('export "{}" --directory="{}"'.format(
            path, folder_name
        ))
        self.assertFalse(r.failed, 'should not have failed')

        directory = os.path.join(path, folder_name)
        self.assertTrue(
            os.path.exists(directory) and os.path.isdir(directory)
        )

    def test_with_args(self):
        """ should successfully export project """

        support.create_project(self, 'venus')
        support.run_command('run')

        path = self.get_temp_path('venus-exporting')
        out_path = os.path.join(path, 'venus')

        r = support.run_command('export "{}" --force'.format(path))
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(out_path) and os.path.isdir(out_path))

        r = support.run_command('export "{}" --force'.format(path))
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(out_path) and os.path.isdir(out_path))

        r = support.run_command('export "{}"'.format(path))
        self.assertTrue(r.failed, 'should have failed')
        self.assertEqual(r.errors[0].code, 'ALREADY_EXISTS')

    def test_appending(self):
        """ should successfully append project export """

        support.create_project(self, 'mars')
        support.run_command('run')

        path = self.get_temp_path('mars-exporting')
        out_path = os.path.join(path, 'mars')

        r = support.run_command('export "{}"'.format(path))
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(out_path) and os.path.isdir(out_path))

        project = cauldron.project.get_internal_project()

        os.makedirs(os.path.join(
            project.results_path,
            'copy_me_during_append'
        ))

        r = support.run_command('export "{}" --append'.format(path))
        self.assertFalse(r.failed, 'should not have failed')
        self.assertTrue(os.path.exists(out_path) and os.path.isdir(out_path))

    def test_no_args(self):
        """ should fail if no path argument """

        support.create_project(self, 'mercury')

        r = export.execute(
            context=cli.make_command_context(export.NAME),
            path=''
        )
        self.assertTrue(r.failed)
        self.assertEqual(r.errors[0].code, 'MISSING_PATH_ARG')

    def test_autocomplete_flags(self):
        """ """

        result = support.autocomplete('export --f')
        self.assertEqual(result, ['force'])

        result = support.autocomplete('export -')
        self.assertGreater(len(result), 2)

    def test_autocomplete(self):
        """ """

        directory = os.path.dirname(os.path.realpath(__file__))
        result = support.autocomplete('export {}'.format(directory))
        self.assertIsNotNone(result)

    def test_autocomplete_empty(self):
        """ """

        directory = os.path.dirname(os.path.realpath(__file__))
        result = support.autocomplete('export fake ')
        self.assertIsNotNone(result)
