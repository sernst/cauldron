from cauldron.session.definitions import FileDefinition
from cauldron.test.support import scaffolds


class TestDefinitions(scaffolds.ResultsTest):
    """ """

    def test_empty_slug(self):
        """ """

        d = FileDefinition()
        d.folder = 'test'
        self.assertTrue(d.slug.startswith('test'))

    def test_remove_name(self):
        """ should remove name if set to None """

        d = FileDefinition()
        self.assertIsNotNone(d.name)
        d.name = 'some-name'
        d.name = None
        self.assertNotEqual(d.name, 'some-name')

    def test_remove_folder(self):
        """ should remove folder if set to None """

        d = FileDefinition()
        self.assertIsNone(d.folder)
        d.folder = 'some-name'
        d.folder = None
        self.assertNotEqual(d.folder, 'some-name')

    def test_remove_title(self):
        """ should remove title if set to None """

        d = FileDefinition()
        self.assertIsNotNone(d.title)
        d.title = 'some-name'
        d.title = None
        self.assertNotEqual(d.title, 'some-name')

    def test_serialize_simple(self):
        """ should serialize to string if only a name is set """

        d = FileDefinition()
        d.name = 'some-name'
        result = d.serialize()

        self.assertEqual(result, 'some-name')

    def test_serialize_advanced(self):
        """ should serialize to a dictionary if complex data """

        d = FileDefinition()
        d.name = 'some-name'
        d.title = 'some-title'
        result = d.serialize()

        self.assertIsInstance(result, dict)
        self.assertEqual(result['title'], 'some-title')
        self.assertIn(result['name'], 'some-name')

    def test_project_folder_string(self):
        """ should use project folder string if folder is not set """

        folder_name = 'some-folder'
        d = FileDefinition()
        d.project_folder = folder_name

        self.assertEqual(d.project_folder, folder_name)
        self.assertEqual(d.folder, folder_name)

    def test_project_folder_callable(self):
        """ should use project folder function if folder is not set """

        folder_name = 'some-folder'
        def get_project_folder():
            return folder_name

        d = FileDefinition()
        d.project_folder = get_project_folder

        self.assertEqual(d.folder, folder_name)
