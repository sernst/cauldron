import os
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from cauldron.session.writing import file_io


@patch('os.path.exists')
@patch('os.chdir')
@patch('shutil.move')
@patch('subprocess.run')
@patch('time.sleep')
def test_move_failure(
        time_sleep: MagicMock,
        subprocess_run: MagicMock,
        shutil_move: MagicMock,
        os_chdir: MagicMock,
        path_exists: MagicMock,
):
    """Should fail to move the file by any means."""
    path_exists.return_value = True
    shutil_move.side_effect = FileExistsError
    subprocess_run.side_effect = [
        MagicMock(stdout=b'foo', returncode=0),
        MagicMock(stdout=b'foo', returncode=0),
        ValueError,
        ValueError,
        MagicMock(check_returncode=MagicMock(side_effect=ValueError))
    ]

    path = os.path.realpath(__file__)

    with pytest.raises(IOError):
        file_io.move(file_io.FILE_COPY_ENTRY(
            source=path,
            destination='{}.shouldnotexist'.format(path)
        ))

    assert 6 == time_sleep.call_count, """
        Expect to sleep on all 6 failed retry attempts.
        """
    assert 3 == shutil_move.call_count, """
        Expect 3 attempts to move the file with shutil.
        """
    assert 5 == subprocess_run.call_count, """
        Expect 3 attempts to move the file with git and two
        calls to determine that the source and output locations
        are both under the same git project.
        """
    assert 9 == os_chdir.call_count, """
        Expect 3 calls to probe git version control and
        then 6 calls during the git move attempts.
        """


@patch('os.utime')
@patch('os.path.exists')
@patch('os.chdir')
@patch('shutil.move')
@patch('subprocess.run')
@patch('time.sleep')
def test_move_git(
        time_sleep: MagicMock,
        subprocess_run: MagicMock,
        shutil_move: MagicMock,
        os_chdir: MagicMock,
        path_exists: MagicMock,
        utime: MagicMock,
):
    """Should move the file using git."""
    path_exists.return_value = True
    subprocess_run.side_effect = [
        MagicMock(stdout=b'bar', returncode=0),
        MagicMock(stdout=b'bar', returncode=0),
        ValueError,
        MagicMock()  # this attempt works
    ]

    path = os.path.realpath(__file__)
    file_io.move(file_io.FILE_COPY_ENTRY(
        source=path,
        destination='{}.shouldnotexist'.format(path)
    ))

    assert 1 == time_sleep.call_count, """
        Expect to sleep once a the first git move attempt.
        """
    assert 0 == shutil_move.call_count, """
        Expect no attempts to move the file with shutil.
        """
    assert 4 == subprocess_run.call_count, """
        Expect 2 attempts to move the file with git and two
        calls to determine that the source and output locations
        are both under the same git project.
        """
    assert 7 == os_chdir.call_count, """
        Expect 3 calls to probe git version control and
        then 4 more calls during the git move attempts.
        """
    assert 0 < utime.call_count, """
        Expect that the moved file gets touched to a new uptime so
        that cauldron can see that the file has changed.
        """


@patch('os.utime')
@patch('os.path.exists')
@patch('os.chdir')
@patch('shutil.move')
@patch('subprocess.run')
@patch('time.sleep')
def test_move_no_git(
        time_sleep: MagicMock,
        subprocess_run: MagicMock,
        shutil_move: MagicMock,
        os_chdir: MagicMock,
        path_exists: MagicMock,
        utime: MagicMock,
):
    """Should move the file with shutil.move."""
    path_exists.return_value = True
    shutil_move.side_effect = [ValueError, MagicMock()]
    subprocess_run.side_effect = [
        MagicMock(stdout=b'foo', returncode=0),
        MagicMock(stdout=b'bar', returncode=0),
    ]

    path = os.path.realpath(__file__)
    file_io.move(file_io.FILE_COPY_ENTRY(
        source=path,
        destination='{}.shouldnotexist'.format(path)
    ))

    assert 1 == time_sleep.call_count, """
        Expect to sleep once a the first shutil move attempt.
        """
    assert 2 == shutil_move.call_count, """
        Expect 2 attempts to move the file with shutil.
        """
    assert 2 == subprocess_run.call_count, """
        Expect 2 attempts to move the file with git and two
        calls to determine that the source and output locations
        are not under the same git project.
        """
    assert 3 == os_chdir.call_count, """
        Expect 3 calls to probe git version control.
        """
    assert 0 < utime.call_count, """
        Expect that the moved file gets touched to a new uptime so
        that cauldron can see that the file has changed.
        """
