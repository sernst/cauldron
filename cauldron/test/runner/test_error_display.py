import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message


class TestPrinting(scaffolds.ResultsTest):

    def test_solo_error(self):
        """ should display an error """

        response = support.create_project(self, 'bismark')
        self.assertFalse(
            response.failed,
            Message('should have created project', response=response)
        )

        code = 'x = 1 + "abcdefg"'

        support.add_step(self, contents=code)

        response = support.run_command('run -f')
        self.assertTrue(
            response.failed,
            Message('should have failed', response=response)
        )

        project = cauldron.project.get_internal_project()

        self.assertTrue(
            project.steps[0].dom.find('cd-CodeError') > 0,
            'should have included error dom'
        )

        self.assertTrue(
            project.steps[0].dom.find('abcdefg') > 0,
            'should have included error line of code'
        )

    def test_standard_error(self):
        """ should include standard error output """

        response = support.create_project(self, 'bozeman')
        self.assertFalse(
            response.failed,
            Message('should have created project', response=response)
        )

        error_string = 'This is a standard error test'

        code = '\n'.join([
            'import sys',
            'sys.stderr.write("{}")'.format(error_string)
        ])

        support.add_step(self, contents=code)

        response = support.run_command('run -f')
        self.assertFalse(
            response.failed,
            Message('should have run step', response=response)
        )

        project = cauldron.project.get_internal_project()

        self.assertTrue(
            project.steps[0].dom.find(error_string) > 0,
            'should have included error string'
        )

        self.assertTrue(
            project.steps[0].dom.find('cd-StdErr') > 0,
            'should have included StdErr dom'
        )
