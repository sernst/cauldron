import cauldron as cd
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestRunnerMarkdownFile(scaffolds.ResultsTest):
    """ """

    def test_run_markdown(self):
        """ should render markdown """

        support.create_project(self, 'salem')
        support.add_step(self, 'test.md', contents='This is markdown')
        response = support.run_command('run -f')
        self.assertFalse(response.failed, 'should have failed')

        step = cd.project.internal_project.steps[0]
        self.assertFalse(step.is_dirty())

        support.run_command('close')

    def test_invalid_markdown(self):
        """ should fail with a jinja error """

        support.create_project(self, 'des-moines')
        support.add_step(
            self,
            'test.md',
            contents='# Hello {{ missing_variable + "12" }}'
        )
        response = support.run_command('run -f')
        self.assertTrue(response.failed)
