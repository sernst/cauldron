import typing
import json
import json.decoder as json_decoder
import os
from collections import namedtuple

from cauldron.environ import paths
from cauldron.environ.logger import log


class Configuration(object):
    """
    Manages configuration settings for both session and persistent
    storage cases in a combined fashion.
    """

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
        """Path to the persistent configuration file."""
        return self._source_path

    @property
    def session(self) -> dict:
        """
        Current session configuration values, which will not persist
        into future sessions. They will be garbage collected when the
        running Cauldron process ends. This returns a copy of the
        session variables object and should not be modified directly.
        """
        return self._session.copy()

    @property
    def persistent(self) -> dict:
        """
        Currently loaded persistent storage values. These values were
        loaded from the persistent configuration file. This returns a
        copy of the session variables object and should not be
        modified directly.
        """
        return self._persistent if self._persistent != self.NO_VALUE else None

    def fetch_all(self) -> typing.Dict[str, typing.Any]:
        """
        Returns a dictionary containing all of the configuration
        settings as a merging of the session and persistent values.
        Where there are overlaps, session values override persistent
        ones.
        """
        return {**self.load()._persistent, **self._session}

    def load(self, source_path: str = None) -> 'Configuration':
        """..."""
        path = source_path if source_path else self._source_path
        if not os.path.exists(path):
            self._persistent = {}
            return self

        try:
            with open(path, 'r') as f:
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

    def fetch(
            self,
            key: str,
            default_value=None,
            use_session: bool = True,
            use_persistent: bool = True
    ) -> typing.Any:
        """

        :param key:
        :param default_value:
        :param use_session:
        :param use_persistent:
        :return:
        """
        if use_session:
            out = self._session.get(key, self.NO_VALUE)
            if out != self.NO_VALUE:
                return out
        if use_persistent:
            if not self.persistent:
                self.load()
            out = self._persistent.get(key, self.NO_VALUE)
            if out != self.NO_VALUE:
                return out

        return default_value

    def put(self, persists: bool = False, **kwargs) -> 'Configuration':
        """..."""
        if persists:
            self.load()._persistent.update(**kwargs)
            self.save()
        else:
            self._session.update(**kwargs)

        return self

    def remove(self, *args, include_persists: bool = True) -> 'Configuration':
        """

        :param args:
        :param include_persists:
        :return:
        """
        for key in args:
            if key in self._session:
                del self._session[key]
            if include_persists and key in self.load()._persistent:
                del self._persistent[key]

        return self

    def save(self) -> 'Configuration':
        """
        Saves the configuration settings object to the current user's home
        directory.
        """
        data = self._persistent
        if data is None:
            return self

        directory = os.path.dirname(self._source_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        path = self._source_path
        with open(path, 'w+') as f:
            json.dump(data, f)

        return self

    def make_path(self, *args, override_key: str = None) -> str:
        """..."""
        override_root_path = None
        if override_key is not None:
            override_root_path = self.fetch(override_key)

        if override_root_path:
            return paths.clean(os.path.join(override_root_path, *args))

        return paths.package(*args)
