import typing
import functools
from cauldron.docgen.params import parse as parse_params
from cauldron.docgen.function_returns import parse as parse_returns
import inspect
import textwrap


def get_docstring(target) -> str:
    """
    Retrieves the documentation string from the target object and returns it
    after removing insignificant whitespace

    :param target:
        The object for which the doc string should be retrieved
    :return:
        The cleaned documentation string for the target. If no doc string
        exists an empty string will be returned instead.
    """

    raw = getattr(target, '__doc__')

    if raw is None:
        return ''

    return textwrap.dedent(raw)


def get_doc_entries(target: typing.Callable) -> list:
    """
    Gets the lines of documentation from the given target, which are formatted
    so that each line is a documentation entry.

    :param target:
    :return:
        A list of strings containing the documentation block entries
    """

    raw = get_docstring(target)

    if not raw:
        return []

    raw_lines = [
        line.strip()
        for line in raw.replace('\r', '').split('\n')
    ]

    def compactify(compacted: list, entry: str) -> list:
        chars = entry.strip()

        if not chars:
            return compacted

        if len(compacted) < 1 or chars.startswith(':'):
            compacted.append(entry.rstrip())
        else:
            compacted[-1] = '{}\n{}'.format(compacted[-1], entry.rstrip())

        return compacted

    return [
        textwrap.dedent(block).strip()
        for block in functools.reduce(compactify, raw_lines, [])
    ]


def parse_function(
        name: str,
        target: typing.Callable
) -> typing.Union[None, dict]:
    """
    Parses the documentation for a function, which is specified by the name of
    the function and the function itself.

    :param name:
        Name of the function to parse
    :param target:
        The function to parse into documentation
    :return:
        A dictionary containing documentation for the specified function, or
        None if the target was not a function.
    """

    if not hasattr(target, '__code__'):
        return None

    lines = get_doc_entries(target)
    docs = ' '.join(filter(lambda line: not line.startswith(':'), lines))
    params = parse_params(target, lines)
    returns = parse_returns(target, lines)

    return dict(
        name=getattr(target, '__name__'),
        doc=docs,
        params=params,
        returns=returns
    )


def variable(name: str, target: property) -> typing.Union[None, dict]:
    """
    :param name:
    :param target:
    :return:
    """

    if hasattr(target, 'fget'):
        doc = parse_function(name, target.fget)
        if doc:
            doc['read_only'] = bool(target.fset is None)
            return doc

    return dict(
        name=name,
        description=get_docstring(target)
    )


def class_doc(name: str, target) -> typing.Union[None, dict]:

    if not inspect.isclass(target):
        return None

    return dict(
        name=target.__name__,
        description=get_docstring(target)
    )


def container(target) -> dict:
    """

    :param target:
    :return:
    """

    names = list(filter(lambda name: not name.startswith('_'), dir(target)))

    def not_none(data) -> bool:
        return bool(data is not None)

    def fetch_docs(callback, *skip_names):
        return [
            callback(n, getattr(target, n))
            for n in names
            if n not in skip_names
        ]

    functions = list(filter(not_none, fetch_docs(parse_function)))
    func_names = [doc['name'] for doc in functions]

    classes = list(filter(not_none, fetch_docs(class_doc, *func_names)))
    class_names = [doc['name'] for doc in classes]

    variables = list(filter(
        not_none,
        fetch_docs(variable, *(func_names + class_names))
    ))

    return dict(
        name=getattr(target, '__name__'),
        description=get_docstring(target),
        functions=functions,
        variables=variables,
        classes=classes
    )
