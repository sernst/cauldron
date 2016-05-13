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

    items = []
    for a in args:
        if isinstance(a, str):
            items.append(a)
        else:
            items += list(a)

    if prefix:
        items = ['{}{}'.format(prefix, x) for x in items]

    return [
        item for item in items
        if item.startswith(value)
    ]


def match_path(
        segment: str,
        value: str,
        include_files: bool = True,
        include_folders: bool = True
) -> list:
    """

    :param segment:
    :param value:
    :param include_files:
    :param include_folders:
    :return:
    """

    segment = segment.strip(os.sep)
    path = environ.paths.clean(value.rstrip(os.sep))

    if not os.path.exists(path):
        # The path doesn't exist, assume that the value is an incomplete path
        # and grab the path to the containing directory instead
        path = os.path.dirname(path)

    if not os.path.exists(path):
        return []
    if not os.path.isdir(path):
        return []

    items = [x for x in os.listdir(path) if x.startswith(segment)]
    out = []

    for item in items:
        item_path = os.path.join(path, item)
        if include_folders and os.path.isdir(item_path):
            out.append('{}{}'.format(item, os.sep))
            continue

        if include_files and os.path.isfile(item_path):
            out.append(item)

    return out


def match_in_path_list(segment: str, value: str, paths: typing.Iterable[str]):
    """

    :param segment:
    :param value:
    :param paths:
    :return:
    """

    prefix = value[:-len(segment)]
    return [x[:-len(prefix)] for x in paths if x.startswith(value)]
