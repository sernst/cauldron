from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import mark
import cauldron
from cauldron import environ
from cauldron.test import support

lifecycle_fixture = support.make_project_lifecycle_fixture()


@patch('webbrowser.open')
def test_show_fail(
        web_browser_open: MagicMock,
        tester: support.ProjectLifecycleTester
):
    """Should fail to show when no project is opened."""
    response = support.run_command('show')
    assert support.has_error_code(response, 'NO_OPEN_PROJECT'), """
        Expect failure with no open project.
        """
    assert 0 == web_browser_open.call_count


@patch('webbrowser.open')
def test_show(
        web_browser_open: MagicMock,
        tester: support.ProjectLifecycleTester
):
    """Should show local project."""
    support.open_project(tester, '@examples:hello_cauldron')
    url = cauldron.project.get_internal_project().baked_url

    response = support.run_command('show')
    assert support.has_success_code(response, 'SHOWN'), """
        Expect show to run without error.
        """
    web_browser_open.assert_called_once_with(url)


@patch('webbrowser.open')
def test_show_remote(
        web_browser_open: MagicMock,
        tester: support.ProjectLifecycleTester
):
    """Should show remote url."""
    support.open_project(tester, '@examples:hello_cauldron')
    project = cauldron.project.get_internal_project()

    remote_connection = environ.RemoteConnection(
        url='http://my-fake.url',
        active=True
    )
    url = project.make_remote_url(remote_connection.url)

    response = support.run_remote_command(
        command='show',
        remote_connection=remote_connection
    )
    assert support.has_success_code(response, 'SHOWN'), """
        Expect show to run without error.
        """
    web_browser_open.assert_called_once_with(url)


@patch('subprocess.check_call')
@patch('cauldron.cli.commands.show.os')
@mark.parametrize('platform', ['darwin', 'linux2', 'win32'])
def test_show_files(
        os_module: MagicMock,
        check_call: MagicMock,
        platform: str,
        tester: support.ProjectLifecycleTester
):
    """Should show local project files."""
    support.open_project(tester, '@examples:hello_cauldron')

    with patch('sys.platform', new=platform):
        response = support.run_command('show files')

    assert support.has_success_code(response, 'SHOWN'), """
        Expect show to run without error.
        """
    assert 1 == (os_module.startfile.call_count + check_call.call_count)


@patch('subprocess.check_call')
@patch('cauldron.cli.commands.show.os')
@mark.parametrize('platform', ['darwin', 'linux2', 'win32'])
def test_show_files_remote(
        os_module: MagicMock,
        check_call: MagicMock,
        platform: str,
        tester: support.ProjectLifecycleTester
):
    """Should show local project files."""
    support.open_project(tester, '@examples:hello_cauldron')

    with patch('sys.platform', new=platform):
        response = support.run_remote_command('show files')

    assert support.has_success_code(response, 'SHOWN'), """
        Expect show to run without error.
        """
    assert 1 == (os_module.startfile.call_count + check_call.call_count)
