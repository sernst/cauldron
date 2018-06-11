import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestStepsInsert(scaffolds.ResultsTest):
    """ """

    def test_before(self):
        """ should properly rename default filenames """

        support.create_project(self, 'candice')
        support.add_step(self)
        support.add_step(self, position='0')

        project = cauldron.project.get_internal_project()
        steps = project.steps

        self.assertTrue(steps[0].filename.startswith('S01'))
        self.assertTrue(steps[1].filename.startswith('S02'))

    def test_multiple_file_types(self):
        """ should properly rename default filenames """

        support.create_project(self, 'candy')
        support.add_step(self)
        support.add_step(self, name='.md', position='0')

        project = cauldron.project.get_internal_project()
        steps = project.steps

        self.assertTrue(steps[0].filename.startswith('S01'))
        self.assertTrue(steps[1].filename.startswith('S02'))

    def test_multiple_file_types_many(self):
        """ should properly rename default filenames """

        support.create_project(self, 'candy')
        support.add_step(self)
        support.add_step(self)
        support.add_step(self)
        support.add_step(self, name='.md', position='0')

        project = cauldron.project.get_internal_project()
        steps = project.steps

        self.assertTrue(steps[0].filename.startswith('S01'))
        self.assertTrue(steps[1].filename.startswith('S02'))
        self.assertTrue(steps[2].filename.startswith('S03'))
        self.assertTrue(steps[3].filename.startswith('S04'))

    def test_multiple_file_types_named(self):
        """ should properly rename customized filenames """

        support.create_project(self, 'candera')
        support.add_step(self, name='A')
        support.add_step(self, name='B')
        support.add_step(self, name='C')
        support.add_step(self, name='D.md', position='0')

        project = cauldron.project.get_internal_project()
        steps = project.steps

        self.assertTrue(steps[0].filename.startswith('S01-D'))
        self.assertTrue(steps[1].filename.startswith('S02'))
        self.assertTrue(steps[2].filename.startswith('S03'))
        self.assertTrue(steps[3].filename.startswith('S04'))
