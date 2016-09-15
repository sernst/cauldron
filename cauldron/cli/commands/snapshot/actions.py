import os
import shutil
import typing
import webbrowser
from datetime import datetime

from cauldron import environ
from cauldron.session.projects import Project
from cauldron.cli.interaction import query


def get_snapshot_listing(project: Project):
    """

    :param project:
    :return:
    """

    snapshots_directory = project.snapshot_path()
    if not os.path.exists(snapshots_directory):
        return []

    out = []
    for item in os.listdir(snapshots_directory):
        item_path = os.path.join(snapshots_directory, item)

        results_path = os.path.join(item_path, 'results.js')
        if not os.path.exists(results_path):
            continue

        out.append(dict(
            name=item,
            url=project.snapshot_url(item),
            directory=item_path,
            last_modified=os.path.getmtime(results_path)
        ))

    out = sorted(out, key=lambda x: x['last_modified'])
    return out


def list_snapshots(project: Project):
    """

    :param project:
    :return:
    """

    snapshots = get_snapshot_listing(project)

    if not snapshots:
        environ.log('No snapshots found')
        return None

    entries = []
    for item in snapshots:
        entries.append('* {}'.format(item['name']))

    environ.log_header('EXISTING SNAPSHOTS')
    environ.log(entries, whitespace_bottom=1, indent_by=3)


def create_snapshot(
        project: Project,
        *args: typing.List[str],
        show: bool = True
):
    """

    :param project:
    :param show:
    :return:
    """

    if len(args) < 1:
        snapshot_name = datetime.now().strftime('%Y%b%d-%H-%M-%S')
    else:
        snapshot_name = args[0]

    snapshot_directory = project.snapshot_path()
    if not os.path.exists(snapshot_directory):
        os.makedirs(snapshot_directory)

    snapshot_name = snapshot_name.replace(' ', '-')
    snapshot_directory = project.snapshot_path(snapshot_name)
    environ.systems.remove(snapshot_directory)

    shutil.copytree(project.output_directory, snapshot_directory)

    url = project.snapshot_url(snapshot_name)

    environ.log_header('Snapshot URL', 5)
    environ.log(
        '* {}'.format(url),
        whitespace_bottom=1,
        indent_by=2
    )

    if show:
        webbrowser.open(url)


def remove_snapshot(
        project: Project,
        *args: typing.List[str]
):
    """

    :param project:
    :param args:
    :return:
    """

    if len(args) < 1 or not args[0].strip():
        environ.log(
            """
            Are you sure you want to remove all snapshots in this project?
            """)

        if not query.confirm('Confirm Delete All', False):
            environ.log(
                '[ABORTED]: No snapshots were deleted',
                whitespace=1
            )
            return

        if not environ.systems.remove(project.snapshot_path()):
            environ.log(
                '[ERROR]: Failed to delete snapshots',
                whitespace=1
            )
            return

        environ.log(
            '[SUCCESS]: All snapshots have been removed',
            whitespace=1
        )
        return

    snapshot_name = args[0]

    environ.log(
        """
        Are you sure you want to remove the snapshot "{}"?
        """.format(snapshot_name),
        whitespace=1
    )

    if not query.confirm('Confirm Deletion', False):
        environ.log(
            """
            [ABORTED]: "{}" was not removed
            """.format(snapshot_name),
            whitespace=1
        )
        return

    if not environ.systems.remove(project.snapshot_path(snapshot_name)):
        environ.log(
            """
            [ERROR]: Unable to delete snapshot "{}" at this time
            """.format(snapshot_name),
            whitespace=1
        )
        return

    environ.log(
        """
        [SUCCESS]: Snapshot "{}" was removed
        """.format(snapshot_name),
        whitespace=1
    )
    return


def open_snapshot(project: Project, name: str) -> dict:
    """

    :param project:
    :param name:
    :return:
    """

    snapshots_directory = project.snapshot_path()
    if not os.path.exists(snapshots_directory):
        return None

    item_path = os.path.join(snapshots_directory, name)
    results_path = os.path.join(item_path, 'results.js')

    if not os.path.exists(results_path):
        return None

    return dict(
        name=name,
        url=project.snapshot_url(name),
        directory=item_path,
        last_modified=os.path.getmtime(results_path)
    )
