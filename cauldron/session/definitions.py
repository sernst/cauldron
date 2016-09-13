import os
import typing
import warnings

from cauldron import environ
from cauldron.session import projects


class FileDefinition(object):
    """

    """

    def __init__(
            self,
            data: typing.Union[dict, str]=None,
            project: 'projects.Project' = None,
            project_folder: typing.Union[typing.Callable, str]=None
    ):
        """

        :param data:
        :param project:
        """

        self.project = project
        self.project_folder = project_folder
        if isinstance(data, str):
            self.data = {'name': data}
        else:
            self.data = data

    @property
    def slug(self):
        folder = self.folder
        if not folder:
            return self.name
        return os.path.join(folder, self.name)

    @property
    def name(self):
        if 'name' not in self.data or not self.data['name']:
            return 'invalid-file-name'

        return self.data.get('name')

    @name.setter
    def name(self, value: str):
        if value is None:
            self.remove('name')
            return

        self.data['name'] = value

    @property
    def folder(self) -> str:
        """
        The folder, relative to the project source_directory, where the file
        resides

        :return:
        """

        if 'folder' in self.data:
            return self.data.get('folder')
        elif self.project_folder:
            if callable(self.project_folder):
                return self.project_folder()
            else:
                return self.project_folder
        return None

    @folder.setter
    def folder(self, value: str):
        if value is None:
            self.remove('folder')
            return

        self.data['folder'] = value

    @property
    def title(self) -> str:
        return self.data.get('title', self.data.get('name'))

    @title.setter
    def title(self, value: str):
        if value is None:
            self.remove('title')
            return

        self.data['title'] = value

    def remove(self, key):
        """

        :param key:
        :return:
        """

        if key in self.data:
            del self.data[key]

    def get(self, key, default_value=None):
        """

        :param key:
        :param default_value:
        :return:
        """

        if hasattr(self, key):
            warnings.warn(
                message='FileDefinition has a "{}" attribute'.format(key),
                category=DeprecationWarning
            )
        return self.data.get(key, default_value)

    def serialize(self) -> typing.Union[dict, str]:
        """

        :return:
        """

        out = dict()
        for k, v in self.data.items():
            if v is not None:
                out[k] = v

        keys = list(out.keys())
        if len(keys) == 1 and keys[0] == 'name':
            return self.name

        return out
