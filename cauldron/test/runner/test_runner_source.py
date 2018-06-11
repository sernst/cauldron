from unittest.mock import patch

import cauldron as cd
from cauldron.environ.response import Response
from cauldron.runner import source
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestRunnerSource(scaffolds.ResultsTest):
    """ """

    def test_get_step_by_name(self):
        """ should retrieve the step from the step name string """

        support.create_project(self, 'washington')
        support.add_step(self)

        project = cd.project.get_internal_project()
        step = project.steps[0]

        result = source.get_step(project, step.filename)
        self.assertEqual(step, result)

    def test_get_missing_step(self):
        """ should get None for a fictional step name """

        support.create_project(self, 'george')
        support.add_step(self)

        project = cd.project.get_internal_project()
        self.assertIsNone(source.get_step(project, 'FICTIONAL-STEP'))

    def test_invalid_step_extension(self):
        """ should fail to execute step of unknown extension """

        support.create_project(self, 'thomas')
        support.add_step(self, 'TEST.fake')

        project = cd.project.get_internal_project()
        step = project.steps[0]
        result = source._execute_step(project, step)

        self.assertFalse(result['success'], False)

    def test_run_no_step(self):
        """ should fail to run a None step """

        support.create_project(self, 'jefferson')
        project = cd.project.get_internal_project()
        result = source.run_step(Response(), project, 'FAKE.STEP')
        self.assertFalse(result)

    @patch(
        'cauldron.runner.source.check_status',
        return_value=source.ERROR_STATUS
    )
    def test_run_error_status(self, *args):
        """ should fail to run a with an error status """

        support.create_project(self, 'john')
        support.add_step(self)
        project = cd.project.get_internal_project()
        step = project.steps[0]

        result = source.run_step(Response(), project, step)
        self.assertFalse(result)

    @patch(
        'cauldron.runner.source.check_status',
        return_value=source.SKIP_STATUS
    )
    def test_run_skip_status(self, *args):
        """ should succeed without running a with a skip status """

        support.create_project(self, 'adams')
        support.add_step(self)
        project = cd.project.get_internal_project()
        step = project.steps[0]

        result = source.run_step(Response(), project, step)
        self.assertTrue(result)

    def test_run_step_execution_error(self):
        """ should fail when running a step that fails to execute """

        support.create_project(self, 'quincy')
        support.add_step(self)
        project = cd.project.get_internal_project()
        step = project.steps[0]

        package = 'cauldron.runner.source._execute_step'
        with patch(package, side_effect=RuntimeError('Not Good!')):
            result = source.run_step(Response(), project, step)

        self.assertFalse(result)

    def test_status_of_muted_step(self):
        """ should have a skip status if the step is muted """

        support.create_project(self, 'madison')
        support.add_step(self)
        project = cd.project.get_internal_project()
        step = project.steps[0]
        step.is_muted = True

        status = source.check_status(Response(), project, step)
        self.assertEqual(status, source.SKIP_STATUS)

    def test_status_of_missing_step_file(self):
        """ should have an error status if the step has no file """

        support.create_project(self, 'james')
        support.add_step(self)
        project = cd.project.get_internal_project()
        step = project.steps[0]

        with patch('os.path.exists', return_value=False):
            status = source.check_status(Response(), project, step)
        self.assertEqual(status, source.ERROR_STATUS)

    def test_status_of_clean_step(self):
        """ should have an skip status if the step is not dirty """

        support.create_project(self, 'monroe')
        support.add_step(self)
        project = cd.project.get_internal_project()
        step = project.steps[0]
        step.is_dirty = lambda: False

        status = source.check_status(Response(), project, step)
        self.assertEqual(status, source.SKIP_STATUS)
