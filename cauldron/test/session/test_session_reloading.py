from datetime import datetime
from email.mime import text as mime_text
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import cauldron as cd
from cauldron.session import reloading
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support.messages import Message


class TestSessionReloading(scaffolds.ResultsTest):
    """Test suite for the reloading module"""

    def test_watch_bad_argument(self):
        """Should not reload a module"""
        self.assertFalse(
            reloading.refresh(datetime, force=True),
            Message('Should not reload not a module')
        )

    def test_watch_good_argument(self):
        """Should reload the specified package/subpackage"""
        self.assertTrue(
            reloading.refresh('datetime', force=True),
            Message('Should reload the datetime module')
        )

    def test_watch_not_needed(self):
        """Don't reload modules that haven't changed."""
        support.create_project(self, 'betty')
        support.add_step(self)
        project = cd.project.get_internal_project()
        project.current_step = project.steps[0]

        self.assertFalse(
            reloading.refresh(mime_text),
            Message('Expect no reload if the step has not been run before.')
        )

        support.run_command('run')
        project.current_step = project.steps[0]

        self.assertFalse(
            reloading.refresh(mime_text),
            Message('Expect no reload if module has not changed recently.')
        )

    def test_watch_recursive(self):
        """Should reload the email module."""
        self.assertTrue(
            reloading.refresh('email', recursive=True, force=True),
            Message('Expected email module to be reloaded.')
        )

    def test_get_module_name(self):
        """Should get the module name from the name of its spec."""
        target = MagicMock()
        target.__spec__ = MagicMock()
        target.__spec__.name = 'hello'
        self.assertEqual('hello', reloading.get_module_name(target))

    def test_get_module_name_alternate(self):
        """
        Should get the module name from its dunder name if the spec name
        does not exist.
        """
        target = Mock(['__name__'])
        target.__name__ = 'hello'
        self.assertEqual('hello', reloading.get_module_name(target))

    @patch('cauldron.session.reloading.os.path')
    @patch('cauldron.session.reloading.importlib.reload')
    def test_do_reload_error(self, reload: MagicMock, os_path: MagicMock):
        """Should fail to import the specified module and so return False."""
        target = MagicMock()
        target.__file__ = None
        target.__path__ = ['fake']
        os_path.getmtime.return_value = 10
        reload.side_effect = ImportError('FAKE')
        self.assertFalse(reloading.do_reload(target, 0))
        self.assertEqual(1, reload.call_count)

    @patch('cauldron.session.reloading.os.path')
    @patch('cauldron.session.reloading.importlib.reload')
    def test_do_reload(self, reload: MagicMock, os_path: MagicMock):
        """Should import the specified module and return True."""
        target = MagicMock()
        target.__file__ = 'fake'
        os_path.getmtime.return_value = 10
        self.assertTrue(reloading.do_reload(target, 0))
        self.assertEqual(1, reload.call_count)

    @patch('cauldron.session.reloading.os.path')
    @patch('cauldron.session.reloading.importlib.reload')
    def test_do_reload_skip(self, reload: MagicMock, os_path: MagicMock):
        """
        Should skip reloading the specified module because it hasn't been
        modified and return False.
        """
        target = MagicMock()
        target.__file__ = 'fake'
        os_path.getmtime.return_value = 0
        self.assertFalse(reloading.do_reload(target, 10))
        self.assertEqual(0, reload.call_count)

    def test_reload_children_module(self):
        """Should abort as False for a module that has no children."""
        target = Mock()
        reloading.reload_children(target, 10)
