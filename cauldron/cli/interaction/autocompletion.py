import os
import typing


from cauldron import environ


def matches(
        segment: str,
        value: str,
        *args: typing.Tuple[typing.Union[str, list, tuple]],
        prefix: str = None
) -> list:
    """

    :param segment:
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

    start_index = len(value) - len(segment)
    possible_matches = [
        x[start_index:] for x in items
        if x.startswith(value)
    ]

    return [x for x in possible_matches if x.startswith(segment)]


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
    path = environ.paths.clean(
        value.rstrip(os.sep) if len(value) > 1 else value
    )

    if len(segment) > 0 or not os.path.exists(path):
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
        elif include_files and os.path.isfile(item_path):
            out.append(item)

    return out


def match_in_path_list(segment: str, value: str, paths: typing.Iterable[str]):
    """

    :param segment:
    :param value:
    :param paths:
    :return:
    """

    pieces = value.replace('\\', '/').split('/')

    out = []
    for c in [x for x in paths if x.startswith(value)]:
        c_pieces = c.replace('\\', '/').split('/')
        index = len(pieces) - 1
        entry = c_pieces[index]

        if len(pieces) < len(c_pieces):
            entry += os.sep

        if entry not in out:
            out.append(entry)

    return [x for x in out if x.startswith(segment)]


def match_flags(
        segment: str,
        value: str,
        shorts: typing.List[str],
        longs: typing.List[str]
) -> list:
    """

    :param segment:
    :param value:
    :param shorts:
    :param longs:
    :return:
    """

    if value.startswith('--'):
        return [x for x in longs if x.startswith(segment)]

    out = [x for x in shorts if x.startswith(segment)]
    out.append('-')
    return out
