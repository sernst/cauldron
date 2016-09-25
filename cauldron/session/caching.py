import typing
from cauldron import environ


class SharedCache(object):
    """

    """

    def __init__(self):
        self._shared_cache_data = dict()

    def clear(self):
        """

        :return:
        """

        environ.abort_thread()

        self._shared_cache_data = dict()
        return self

    def put(self, *args, **kwargs):
        """

        :param kwargs:
        :return:
        """

        environ.abort_thread()

        index = 0
        while index < (len(args) - 1):
            key = args[index]
            value = args[index + 1]
            self._shared_cache_data[key] = value
            index += 2

        for key, value in kwargs.items():
            if value is None and key in self._shared_cache_data:
                del self._shared_cache_data[key]
            else:
                self._shared_cache_data[key] = value

        return self

    def grab(
            self,
            *keys: typing.List[str],
            default_value=None
    ) -> typing.Tuple:
        """

        :param keys:
        :param default_value:
        :return:
        """

        return tuple([self.fetch(k, default_value) for k in keys])

    def fetch(self, key: typing.Union[str, None], default_value=None):
        """

        :param key:
        :param default_value:
        :return:
        """

        environ.abort_thread()

        if key is None:
            return self._shared_cache_data

        return self._shared_cache_data.get(key, default_value)

    def __getitem__(self, item):
        environ.abort_thread()

        return self._shared_cache_data.get(item)

    def __getattr__(self, item):
        environ.abort_thread()

        if item.startswith('_'):
            return None

        return self._shared_cache_data.get(item)

    def __setitem__(self, key, value):
        environ.abort_thread()

        self._shared_cache_data[key] = value

    def __setattr__(self, key, value):
        environ.abort_thread()

        if key.startswith('_'):
            super(SharedCache, self).__setattr__(key, value)
        else:
            self._shared_cache_data[key] = value
