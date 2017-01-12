import typing
from cauldron import environ


class SharedCache(object):
    """
    A class that serves as a container for storing data by key but is
    accessible using dot notation instead of dictionary notation. Also contains
    additional functions for handling multiple variables at once.
    """

    def __init__(self):
        self._shared_cache_data = dict()

    def clear(self) -> 'SharedCache':
        """
        Clears all of the variables currently stored in this cache
        """

        environ.abort_thread()

        self._shared_cache_data = dict()
        return self

    def put(self, *args, **kwargs) -> 'SharedCache':
        """
        Adds one or more variables to the cache.

        :param args:
            Variables can be specified by two consecutive arguments where the
            first argument is a key and the second one the corresponding value.
            For example:

            ```
            put('a', 1, 'b', False)
            ```

            would add two variables to the cache where the value of _a_ would
            be 1 and the value of _b_ would be False.
        :param kwargs:
            Keyword arguments to be added to the cache, which are name value
            pairs like standard keyword named arguments in Python. For example:

            ```
            put(a=1, b=False)
            ```

            would add two variables to the cache where the value of _a_ would
            be 1 and the value of _b_ would be False.
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
        Returns a tuple containing multiple values from the cache specified by
        the keys arguments

        :param keys:
            One or more variable names stored in the cache that should be
            returned by the grab function. The order of these arguments are
            preserved by the returned tuple.
        :param default_value:
            If one or more of the keys is not found within the cache, this
            value will be returned as the missing value.
        :return:
            A tuple containing values for each of the keys specified in the
            arguments
        """

        return tuple([self.fetch(k, default_value) for k in keys])

    def fetch(self, key: typing.Union[str, None], default_value=None):
        """
        Retrieves the value of the specified variable from the cache

        :param key:
            The name of the variable for which the value should be returned
        :param default_value:
            The value to return if the variable does not exist in the cache
        :return:
            The value of the specified key if it exists in the cache or the
            default_Value if it does not
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
