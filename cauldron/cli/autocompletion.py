import os
import typing


from cauldron import environ

def matches(value: str, *args: typing.Tuple[str], prefix: str = None) -> list:
    """

    :param value:
    :param args:
    :param prefix:
    :return:
    """

    if prefix:
        args = ['{}{}'.format(prefix, x) for x in args]

    return [
        item for item in args
        if item.startswith(value)
    ]


def matches_paths(
        value: str,
        paths: typing.Union[str, typing.List[str]],
        prefix: str = None,
        include_files: bool = True,
        include_dirs: bool = True,
        absolute: bool = False
) -> list:
    """

    :param value:
    :param paths:
    :param prefix:
    :return:
    """

    if isinstance(paths, str):
        paths = [paths]

    items = []
    for p in paths:
        p = environ.paths.clean(p)
        for item in list(os.listdir(p)):
            item_path = os.path.join(p, item)
            if not include_dirs and os.path.isdir(item_path):
                continue
            elif not include_files and os.path.isfile(item_path):
                continue
            items.append(item_path if absolute else item)

    return matches(
        value,
        *items,
        prefix=prefix
    )
