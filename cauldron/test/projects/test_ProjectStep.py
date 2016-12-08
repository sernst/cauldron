from cauldron.session import projects
from cauldron.test.support import scaffolds


class TestProjectStep(scaffolds.ResultsTest):
    """

    """

    def test_no_project_defaults(self):
        """
        A ProjectStep without a Project reference should properly default
        its properties and values
        """

        ps = projects.ProjectStep()

        self.assertEqual(ps.index, -1)
        self.assertEqual(ps.web_includes, [])
        self.assertIsNone(ps.source_path)

    def test_is_dirty_branches(self):
        """
        ProjectStep should remain dirty until it has been properly
        initialized and run
        """

        ps = projects.ProjectStep()

        self.assertTrue(ps.is_dirty(), 'always starts dirty')

        ps._is_dirty = False
        self.assertTrue(ps.is_dirty(), 'dirty because not modified is None')

        ps.last_modified = 1
        self.assertFalse(ps.is_dirty(), 'not dirty without a valid source path')
