import json
import os

from cauldron import environ


def get_project_source_path(path: str) -> str:
    """
    Converts the given path into a project source path, to the cauldron.json
    file. If the path already points to a cauldron.json file, the path is
    returned without modification.

    :param path:
        The path to convert into a project source path
    """

    path = environ.paths.clean(path)

    if not path.endswith('cauldron.json'):
        return os.path.join(path, 'cauldron.json')

    return path


def load_project_definition(path: str) -> dict:
    """
    Load the cauldron.json project definition file for the given path. The
    path can be either a source path to the cauldron.json file or the source
    directory where a cauldron.json file resides.

    :param path:
        The source path or directory where the definition file will be loaded
    """

    source_path = get_project_source_path(path)
    if not os.path.exists(source_path):
        raise FileNotFoundError('Missing project file: {}'.format(source_path))

    with open(source_path, 'r') as f:
        out = json.load(f)

    project_folder = os.path.split(os.path.dirname(source_path))[-1]
    if 'id' not in out or not out['id']:
        out['id'] = project_folder

    return out
