import datetime
import glob
import hashlib
import json
import os
import textwrap
import time
import typing
from collections import defaultdict


class ProjectSpecsReader:

    def __init__(self):
        self._load_index = 0
        self._specs = []

    @property
    def specs(self):
        return self._specs + []

    def add(self, path: str, **kwargs) -> 'ProjectSpecsReader':
        if not path.endswith('cauldron.json'):
            path = os.path.join(path, 'cauldron.json')

        if not os.path.exists(path):
            # Do nothing if the project does not exist.
            return self

        spec = get_project_info(path)
        spec.update(index=len(self._specs), **kwargs)
        self._specs.append(spec)
        return self

    def add_recursive(
            self,
            recursive_root_path: str,
            **kwargs
    ) -> 'ProjectSpecsReader':
        glob_path = os.path.join(recursive_root_path, '**', 'cauldron.json')
        paths = list(sorted(glob.iglob(glob_path, recursive=True)))
        for path in paths:
            self.add(path, **kwargs)
        return self

    def group_by(
            self,
            key: str
    ) -> typing.Dict[typing.Any, typing.List[dict]]:
        groups = defaultdict(list)
        for spec in self._specs:
            value = spec.get(key)
            groups[value].append(spec)
        return groups


def to_display(project: dict) -> str:
    """
    Converts a project information dictionary object into a disply-ready
    string representation for use in console output.
    """
    p = project
    return '{i}) {name} ({count:,.0f} steps)\n   {dir}\n   {time}\n'.format(
        name=p.get('title', p.get('name', 'Unnamed Project')),
        count=len(p.get('steps', [])),
        dir=p.get('directory', {}).get('short', 'Unknown location'),
        time=p.get('modified', {}).get('elapsed', 'Unknown Age'),
        i=p.get('index', -1) + 1
    )


def to_display_list(projects: typing.List[dict]) -> str:
    """
    Converts a list of project information dictionaries into a
    display listing for console display.
    """
    results = [to_display(p) for p in projects]
    return textwrap.indent('\n'.join(results), '   ')


def format_times(unix_timestamp: float) -> typing.Dict[str, typing.Any]:
    """
    Creates a dictionary that contains differently formatted times
    for the given unix_timestamp value, which are useful in different
    situations. The returned keys are:

        - timestamp: value of the unix timestamp argument.
        - iso: ISO 8601 formatted datetime.
        - display: human readable format of the timestamp.
        - elapsed: human readable delta between the value and now.

    :param unix_timestamp:
        A unix epoch timestamp representing the number of seconds
        since the start of the epoch.
    """
    date_time = datetime.datetime.fromtimestamp(unix_timestamp)
    display = (
        date_time
        .strftime('%B %d, %Y at %I:%M%p')
        .replace(' 0', ' ')
        .replace('AM', 'am')
        .replace('PM', 'pm')
    )

    delta = int(time.time() - unix_timestamp)
    if delta > (3600 * 24 * 365 * 2):
        elapsed = '{:,.0f} years ago'.format(delta/ (365 * 24 * 3600))
    elif delta > (3600 * 24 * 365):
        elapsed = '1 year ago'
    elif delta > (3600 * 24 * 7 * 4):
        elapsed = '{:,.0f} weeks ago'.format(delta / (7 * 24 * 3600))
    elif delta > (3600 * 48):
        elapsed = '{:,.0f} days ago'.format(delta / (24 * 3600))
    elif delta > (3600 * 2):
        elapsed = '{:,.0f} hours ago'.format(delta / 3600)
    elif delta > (60 * 2):
        elapsed = '{:,.0f} minutes ago'.format(delta / 60)
    else:
        elapsed = 'just now'

    return {
        'timestamp': unix_timestamp,
        'iso': date_time.isoformat(),
        'display': display,
        'elapsed': elapsed
    }


def get_project_info(path: str) -> typing.Optional[dict]:
    """
    Returns the parsed contents of the ``cauldron.json`` file at the
    specified path location. The path can be either a directory
    containing a ``cauldron.json`` file or the path to a ``cauldron.json``
    file. A ``None`` value will be returned if no such file exists at
    the given location.
    """
    if not path.endswith('cauldron.json'):
        path = os.path.join(path, 'cauldron.json')

    if not os.path.exists(path):
        return None

    try:
        with open(path) as fp:
            contents = json.load(fp)

        directory = os.path.dirname(path)
        if len(directory) > 40:
            short = '{}...{}'.format(directory[:12], directory[-21:])
        else:
            short = directory

        contents.update(
            uid=hashlib.md5(path.encode()).hexdigest(),
            modified=format_times(os.path.getmtime(path)),
            directory={
                'absolute': directory,
                'short': short
            }
        )
        return contents
    except Exception:
        return None
