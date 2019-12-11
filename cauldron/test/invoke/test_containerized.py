from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.test.invoke import utils as invoke_utils


@patch('cauldron.invoke.containerized.subprocess.run')
def test_run_containerized_ui_with_remote(
        subprocess_run: MagicMock,
):
    """
    Should run ui command without error using the mocked data and command
    line arguments to assemble the command to be executed as expected.
    """
    subprocess_run.return_value.returncode = 0

    return_code = invoke_utils.run_command(
        'uidocker --remote=foo@foo.com:1234 --ssh-key=bar'
    )

    assert return_code == 0

    cmd = subprocess_run.call_args[0][0]
    assert '1234:8899' in cmd, """
        Expect the custom 1234 port to be mapped to the internal UI port.
        """
    assert '--remote=foo@foo.com:1234' in cmd, """
        Expect the remote flag to include the DNS host name and 
        custom assigned port.
        """


@patch('cauldron.invoke.containerized.subprocess.run')
def test_run_containerized_ui_local(
        subprocess_run: MagicMock,
):
    """
    Should run ui command without error using the mocked data and command
    line arguments to assemble the command to be executed as expected.
    """
    subprocess_run.return_value.returncode = 0

    return_code = invoke_utils.run_command('uidocker --port=1234')

    assert return_code == 0

    cmd = subprocess_run.call_args[0][0]
    assert '1234:8899' in cmd, """
        Expect the custom 1234 port to be mapped to the internal UI port.
        """
    assert '--remote' not in ' '.join(cmd), """
        Expect no remote flag to be set when no remote flag in the
        invocation.
        """
