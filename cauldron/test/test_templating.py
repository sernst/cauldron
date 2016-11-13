import unittest

from cauldron import templating
from cauldron import environ


class TestTemplating(unittest.TestCase):

    def test_id_filter(self):
        """
        """

        result = templating.render('{{ "test" | id }}')
        parts = result.split('-', 2)
        self.assertEqual(
            parts[0], 'cdi',
            msg='"{}" should start with "cdi"'.format(result)
        )
        self.assertEqual(
            parts[1], 'test',
            msg='"{}" should match the prefix'.format(result)
        )

    def test_latex_filter(self):
        """
        """

        result = templating.render('{{ "e = mc^2" | latex }}')
        self.assertNotEqual(result.find('katex'), -1, 'where is katex?')

    def test_render_template(self):
        """

        :return:
        """

        result = templating.render_template('unit_test.html', value='hello')
        self.assertEqual(result, 'hello')

    def test_render_file(self):
        """

        :return:
        """

        result = templating.render_file(
            environ.paths.package('resources', 'templates', 'unit_test.html'),
            value='hello'
        )
        self.assertEqual(result, 'hello')





