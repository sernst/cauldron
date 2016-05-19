import os
import shutil
import webbrowser
import typing
from datetime import datetime

from cauldron import environ
from cauldron.session.project import Project
from cauldron.cli import query


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
        return

    entries = []
    for item in snapshots:
        entries.append(' * {id}\n   {url}\n'.format(
            id=item['name'],
            url=item['url']
        ))

    environ.log([
        'Existing Snapshots:',
        '-------------------'
    ] + entries,
        whitespace=1
    )


def create_snapshot(project: Project, *args: typing.List[str]):
    """

    :param project:
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

    environ.log(
        """
        Snapshot URL:
        -------------

          * {}
        """.format(url),
        whitespace=1
    )

    webbrowser.open(url)


def remove_snapshot(project: Project, *args: typing.List[str]):
    """

    :param project:
    :param args:
    :return:
    """

    if len(args) < 1 or not args[0]:
        snapshot_name = get_snapshot_listing(project)[-1]['name']
    else:
        snapshot_name = args[0]

    environ.log(
        """
        Are you sure you want to remove the snapshot "{}"?
        """.format(snapshot_name)
    )

    if not query.confirm('Confirm Deletion', False):
        environ.log(
            """
            [ABORTED]: "{}" was not removed
            """.format(snapshot_name)
        )
        return

    if not environ.systems.remove(project.snapshot_path(snapshot_name)):
        environ.log(
            """
            [ERROR]: Unable to delete snapshot "{}" at this time
            """.format(snapshot_name)
        )
        return

    environ.log(
        """
        [SUCCESS]: Snapshot "{}" was removed
        """.format(snapshot_name)
    )
    return
