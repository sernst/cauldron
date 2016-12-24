import json
import json.decoder as json_decoder
import os
from collections import namedtuple

from cauldron.environ.logger import log
from cauldron.environ import paths


class Configuration(object):
    NO_VALUE = namedtuple('NO_VALUE_NT', [])()

    def __init__(self, source_path: str = None):
        self._session = {}
        self._persistent = None
        self._source_path = (
            os.path.expanduser('~/.cauldron/v1/configs.json')
            if not source_path else
            source_path
        )

    @property
    def path(self) -> str:
        return self._source_path

    @property
    def session(self) -> dict:
        return self._session

    @property
    def persistent(self) -> dict:
        return self._persistent if self._persistent != self.NO_VALUE else None

    def fetch_all(self):
        out = {}
        out.update(**self.load().persistent)
        out.update(**self.session)
        return out

    def load(self, source_path: str = None):
        """

        :return:
        """

        if self.persistent is not None:
            return self

        path = source_path if source_path else self._source_path
        if not os.path.exists(path):
            self._persistent = {}
            return self

        try:
            with open(path, 'r+') as f:
                contents = f.read()
            if contents:
                self._persistent = json.loads(contents)
        except json_decoder.JSONDecodeError as err:
            if self._persistent == self.NO_VALUE:
                return self

            self._persistent = self.NO_VALUE
            log(
                """
                [ERROR]: Failed to decode json file
                  PATH: {path}
                  INFO: {msg}
                    LINE: {line}
                    CHAR: {char}
                """.format(
                    path=path,
                    msg=err.msg,
                    line=err.lineno,
                    char=err.colno
                )
            )
        return self

    def fetch_session(self, key: str, default_value=None):
        """

        :param key:
        :param default_value:
        :return:
        """

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

    def remove(self, *args, include_persists: bool = True):
        """

        :param args:
        :param include_persists:
        :return:
        """

        for key in args:
            if key in self.session:
                del self.session[key]
            if include_persists and key in self.load().persistent:
                del self.persistent[key]

    def save(self) -> 'Configuration':
        """
        Saves the configuration settings object to the current user's home
        directory

        :return:
        """

        data = self.load().persistent
        if data is None:
            return self

        directory = os.path.dirname(self._source_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        path = self._source_path
        with open(path, 'w+') as f:
            json.dump(data, f)

        return self

    def make_path(self, *args, override_key: str = None):

        override_root_path = None
        if override_key is not None:
            override_root_path = self.fetch(override_key)

        if override_root_path:
            return paths.clean(os.path.join(override_root_path, *args))

        return paths.package(*args)
