import os
import sys

from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message
from cauldron.session import naming
from cauldron.session import projects


class TestNaming(scaffolds.ResultsTest):
    """

    """

    def test_default(self):
        name = naming.find_default_filename(['1.py', '2.py'])
        self.assertEqual(name, '3')

    def test_explode(self):
        name = 'S02-name.py'
        # spec: {location: S01.py | name: namer.py | type: py}
        result = naming.explode_filename(name, projects.DEFAULT_SCHEME)
        self.assertEqual(result['name'], 'name')
        self.assertEqual(result['index'], 1)
        self.assertEqual(result['extension'], 'py')

    def test_explode_misaligned(self):
        # spec: {location: S01.py | name: namer.py | type: py}
        result = naming.explode_filename('namer.py', projects.DEFAULT_SCHEME)
        self.assertEqual(result['name'], 'namer')
        self.assertIsNone(result['index'], 0)
        self.assertEqual(result['extension'], 'py')

    def test_assemble(self):
        parts = naming.explode_filename('namer.py', projects.DEFAULT_SCHEME)
        result = naming.assemble_filename(
            scheme=projects.DEFAULT_SCHEME,
            **parts
        )
        self.assertTrue(result.endswith('namer.py'))
