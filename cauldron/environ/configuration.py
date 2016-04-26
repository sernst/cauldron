import json
import json.decoder as json_decoder
import os
from collections import namedtuple

from cauldron.environ.logger import log
from cauldron.environ import paths


class Configuration(object):
    NO_VALUE = namedtuple('NO_VALUE_NT', [])()

    def __init__(self):
        self._session = {}
        self._persistent = None

    @property
    def session(self) -> dict:
        return self._session

    @property
    def persistent(self) -> dict:
        return self._persistent

    def fetch_all(self):
        out = {}
        out.update(**self.load().persistent)
        out.update(**self.session)
        return out

    def load(self):
        """

        :return:
        """

        if self.persistent is not None:
            return self

        self._persistent = {}

        path = os.path.expanduser('~/.cauldron/v1/configs.json')
        if not os.path.exists(path):
            return self

        try:
            with open(path, 'r+') as f:
                self.persistent.update(**json.load(f))
        except json_decoder.JSONDecodeError as err:
            log([
                '[ERROR]: Failed to decode json file',
                ['PATH: {}'.format(path),
                 'INFO: {}'.format(err.msg),
                 ['LINE: {}'.format(err.lineno),
                  'CHAR: {}'.format(err.colno)]]
            ])
        return self

    def fetch(
            self,
            key: str,
            default_value=None,
            use_session: bool = True,
            use_persistent: bool = True
    ):
        """

        :param key:
        :param default_value:
        :param use_session:
        :param use_persistent:
        :return:
        """

        if use_session:
            out = self.session.get(key, self.NO_VALUE)
            if out != self.NO_VALUE:
                return out
        if use_persistent:
            if not self.persistent:
                self.load()
            out = self.persistent.get(key, self.NO_VALUE)
            if out != self.NO_VALUE:
                return out

        return default_value

    def put(self, persists: bool = False, **kwargs):
        """

        :param persists:
        :return:
        """

        if persists:
            self.load().persistent.update(**kwargs)
        else:
            self.session.update(**kwargs)

    def remove(self, *args):
        """

        :param args:
        :return:
        """

        for key in args:
            if key in self.session:
                del self.session[key]
            if key in self.load().persistent:
                del self.persistent[key]

    def save(self) -> 'Configuration':
        """
        Saves the configuration settings object to the current user's home
        directory

        :return:
        """

        path = os.path.expanduser('~/.cauldron/v1/')
        if not os.path.exists(path):
            os.makedirs(path)

        path = os.path.join(path, 'configs.json')
        with open(path, 'w+') as f:
            json.dump(self.load().persistent, f)

        return self

    def make_path(self, *args, override_key: str = None):

        override_root_path = None
        if override_key is not None:
            override_root_path = self.fetch(override_key)

        if override_root_path:
            return paths.clean(os.path.join(override_root_path, *args))

        return paths.package(*args)
