import typing
import functools


def get_doc_lines(target: typing.Callable) -> list:
    raw = getattr(target, '__doc__')

    if not raw:
        return []

    raw_lines = [
        line.strip()
        for line in raw.strip().replace('\r', '').split('\n')
    ]

    def compactify(compacted: list, entry: str) -> list:
        if not entry:
            return compacted

        if len(compacted) < 1 or entry.startswith(':'):
            compacted.append(entry)
        else:
            compacted[-1] = '{} {}'.format(compacted[-1], entry)

        return compacted

    return list(functools.reduce(compactify, raw_lines, []))


def parse_params(target, lines: list) -> list:
    """

    :param target:
    :param lines:
    :return:
    """

    annotations = getattr(target, '__annotations__', {})

    def create_argument(argument_line: str) -> dict:
        name, docstring = argument_line.split(' ', 1)[-1].split(':', 1)
        return dict(
            name=name,
            description=docstring,
            type=annotations.get(name, 'any')
        )

    return list(map(
        create_argument,
        filter(lambda line: line.startswith(':param'), lines)
    ))


def function(target: typing.Callable):
    """

    :param target:
    :return:
    """

    lines = get_doc_lines(target)
    docs = filter(lambda line: not line.startswith(':'), lines)
    params = parse_params(target, lines)

    return dict(
        name=getattr(target, '__name__'),
        doc=' '.join(docs),
        params=params
    )


def module(target) -> dict:
    """

    :param target:
    :return:
    """

    function_names = filter(lambda name: not name.startswith('_'), dir(target))

    return dict(
        name=getattr(target, '__name__'),
        functions=[function(getattr(target, name)) for name in function_names]
    )
