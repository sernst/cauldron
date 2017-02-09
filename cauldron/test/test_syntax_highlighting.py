from unittest import TestCase
from pygments.lexers.python import Python3Lexer
from pygments.lexers.python import PythonLexer
from cauldron.render import syntax_highlighting


class TestSyntaxHighlighting(TestCase):

    def test_source(self):
        """ should retrieve python lexer by source """

        with open(__file__, 'r') as f:
            contents = f.read()

        lexer = syntax_highlighting.fetch_lexer(contents)
        self.assertIsInstance(lexer, PythonLexer)

    def test_language_python3(self):
        """ should retrieve python 3 lexer by language """

        lexer = syntax_highlighting.fetch_lexer('', 'python3')
        self.assertIsInstance(lexer, Python3Lexer)

    def test_filename_python(self):
        """ should retrieve python lexer by filename """

        lexer = syntax_highlighting.fetch_lexer('', 'fake', 'test.py')
        self.assertIsInstance(lexer, PythonLexer)

    def test_mime_type_python(self):
        """ should retrieve python lexer by filename """

        lexer = syntax_highlighting.fetch_lexer(
            '',
            mime_type='application/x-python'
        )
        self.assertIsInstance(lexer, PythonLexer)

    def test_unknown_language(self):
        """ should retrieve a default lexer for an unknown language """
        lexer = syntax_highlighting.fetch_lexer('', 'lkjasdlkjsad')
        self.assertIsNotNone(lexer)

    def test_unknown_everything(self):
        """ should retrieve a default lexer for an unknown language """
        lexer = syntax_highlighting.fetch_lexer(
            source='asdlkasdj',
            language='lkjasdlkjsad',
            filename='test.qweoihwq',
            mime_type='fictional/lasdlkjad'
        )
        self.assertIsNotNone(lexer)
