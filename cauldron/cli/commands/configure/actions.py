import typing

from cauldron import environ


def remove_key(key: str, persists: bool = True):
    """
    Removes the specified key from the cauldron configs if the key exists

    :param key:
        The key in the cauldron configs object to remove
    :param persists:
    """

    environ.configs.remove(key, include_persists=persists)
    environ.configs.save()

    environ.log(
        '[REMOVED]: "{}" from configuration settings'.format(key)
    )


def set_key(key: str, value: typing.List[str], persists: bool = True):
    """
    Removes the specified key from the cauldron configs if the key exists

    :param key:
        The key in the cauldron configs object to remove
    :param value:
    :param persists:
    """

    if key.endswith('_path') or key.endswith('_paths'):
        for index in range(len(value)):
            value[index] = environ.paths.clean(value[index])

    if len(value) == 1:
        value = value[0]

    environ.configs.put(**{key: value}, persists=persists)
    environ.configs.save()
    environ.log('[SET]: "{}" to "{}"'.format(key, value))


def echo_key(key: str):
    """

    :param key:
    :return:
    """

    value = environ.configs.fetch(key)

    if value is None:
        environ.log('[MISSING]: No "{}" key was found'.format(key))
        return

    environ.log('[VALUE]: "{}" = {}'.format(key, value))


def echo_all():
    """

    :return:
    """

    out = ['Current Configuration:']
    for key, value in environ.configs.fetch_all().items():
        out.append('  * {key}: {value}'.format(key=key, value=value))

    environ.log('\n'.join(out))
