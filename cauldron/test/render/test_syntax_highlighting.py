from unittest import TestCase

from pygments.lexers.python import Python3Lexer

from cauldron.render import syntax_highlighting

# Pygments has recently introduced Python2Lexer and made
# PythonLexer the Python3Lexer. For maximum compatibility
# of the test, the assertions will allow any of the lexers
# to be used.
# https://pygments.org/docs/lexers/#pygments.lexers.python.Python2Lexer
PYTHON_LEXER_CLASS_NAMES = [
    'Python2Lexer',
    'PythonLexer',
    'Python3Lexer'
]


class TestSyntaxHighlighting(TestCase):

    def test_source(self):
        """Should retrieve python lexer by source."""
        with open(__file__, 'r') as f:
            contents = f.read()

        lexer = syntax_highlighting.fetch_lexer(contents)
        self.assertIn(lexer.__class__.__name__, PYTHON_LEXER_CLASS_NAMES)

    def test_language_python3(self):
        """Should retrieve python 3 lexer by language."""
        lexer = syntax_highlighting.fetch_lexer('', 'python3')
        self.assertIsInstance(lexer, Python3Lexer)

    def test_filename_python(self):
        """Should retrieve python lexer by filename."""
        lexer = syntax_highlighting.fetch_lexer('', 'fake', 'test.py')
        self.assertIn(lexer.__class__.__name__, PYTHON_LEXER_CLASS_NAMES)

    def test_mime_type_python(self):
        """Should retrieve python lexer by filename."""
        lexer = syntax_highlighting.fetch_lexer(
            '',
            mime_type='application/x-python'
        )
        self.assertIn(lexer.__class__.__name__, PYTHON_LEXER_CLASS_NAMES)

    def test_unknown_language(self):
        """Should retrieve a default lexer for an unknown language."""
        lexer = syntax_highlighting.fetch_lexer('', 'lkjasdlkjsad')
        self.assertIsNotNone(lexer)

    def test_unknown_everything(self):
        """Should retrieve a default lexer for an unknown language."""
        lexer = syntax_highlighting.fetch_lexer(
            source='asdlkasdj',
            language='lkjasdlkjsad',
            filename='test.qweoihwq',
            mime_type='fictional/lasdlkjad'
        )
        self.assertIsNotNone(lexer)
