import typing


class SharedCache(object):
    """

    """

    def __init__(self):
        self._shared_cache_data = dict()

    def clear(self):
        """

        :return:
        """
        self._shared_cache_data = dict()
        return self

    def put(self, *args, **kwargs):
        """

        :param kwargs:
        :return:
        """

        index = 0
        while index < (len(args) - 1):
            key = args[index]
            value = args[index + 1]
            self._shared_cache_data[key] = value
            index += 2

        for key, value in kwargs.items():
            self._shared_cache_data[key] = value

        return self

    def fetch(self, key: typing.Union[str, None], default_value=None):
        """

        :param key:
        :param default_value:
        :return:
        """

        if key is None:
            return self._shared_cache_data

        return self._shared_cache_data.get(key, default_value)

    def __getitem__(self, item):
        return self._shared_cache_data.get(item)

    def __getattr__(self, item):
        if item.startswith('_'):
            return None

        return self._shared_cache_data.get(item)

    def __setitem__(self, key, value):
        self._shared_cache_data[key] = value

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(SharedCache, self).__setattr__(key, value)
        else:
            self._shared_cache_data[key] = value
