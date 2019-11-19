from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.ui import statuses


def test_merge_local_state_no_project():
    """Should merge local state into a remote status response."""
    remote_status = {'data': {}}
    response = statuses.merge_local_state(remote_status, False)

    assert 'hash' in response, 'Expect hash to be set locally.'

    expected_keys = {'view', 'remote', 'project'}
    assert expected_keys == set(response['data'].keys()), """
        Expect the specified keys to be set.
        """


@patch('os.path.exists')
@patch('os.path.getmtime')
def test_merge_local_state(
        getmtime: MagicMock,
        path_exists: MagicMock
):
    """Should merge local state into a remote status response."""
    getmtime.side_effect = [-1000, FileNotFoundError]
    path_exists.side_effect = [True, False]

    project_data = {
        'steps': [
            # This step will not be modified because there's no status info.
            {'remote_source_path': 'foo', 'status': {}},
            {'remote_source_path': 'bar', 'status': {'name': 'bar'}},
            {'remote_source_path': 'baz', 'status': {'name': 'bax'}},
        ]
    }
    remote_status = {'data': {'project': project_data}}
    response = statuses.merge_local_state(remote_status, True)

    assert response['hash'].startswith('forced-'), """
        Expect force local state to have a forced hash.
        """

    steps = response['data']['project']['steps']
    dirty_values = [s['status'].get('is_dirty') for s in steps]
    assert [None, False, True] == dirty_values, """
        Expect first step to be None because status is empty,
        second to be False because is exists and is not recently 
        modified, and third to be True because the local file does
        not exist.
        """
