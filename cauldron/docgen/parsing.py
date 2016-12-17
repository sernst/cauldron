import typing
import functools
import inspect


def get_doc_lines(target: typing.Callable) -> list:
    """

    :param target:
    :return:
    """

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

    code = target.__code__
    annotations = getattr(target, '__annotations__', {})
    has_args = code.co_flags & inspect.CO_VARARGS
    has_kwargs = code.co_flags & inspect.CO_VARKEYWORDS
    arg_count = (
        code.co_argcount +
        (1 if has_args else 0) +
        (1 if has_kwargs else 0)
    )
    arg_names = list(code.co_varnames[:arg_count])

    if len(arg_names) > 0 and arg_names[0] in ['self', 'cls']:
        arg_count -= 1
        arg_names.pop(0)

    def get_optional_data(name):
        defaults = target.__defaults__
        try:
            index = arg_names.index(name)
            default_index = index - (len(arg_names) - len(defaults))
        except:
            default_index = -1

        if default_index < 0:
            return {'optional': False}

        return {'optional': True, 'default': str(defaults[default_index])}

    def arg_type_to_string(arg_type) -> str:
        if hasattr(arg_type, '__union_params__'):
            return ', '.join([
                arg_type_to_string(item)
                for item in arg_type.__union_params__
            ])

        try:
            return arg_type.__name__
        except:
            return arg_type

    def create_empty_argument(name) -> dict:
        out = dict(
            name=name,
            index=arg_names.index(name),
            description='',
            type=arg_type_to_string(annotations.get(name, 'Any'))
        )
        out.update(get_optional_data(name))
        return out

    def create_argument(argument_line: str) -> dict:
        name, docstring = argument_line.split(' ', 1)[-1].split(':', 1)
        out = create_empty_argument(name)
        out['description'] = docstring
        return out

    arg_docs = list(map(
        create_argument,
        filter(lambda line: line.startswith(':param'), lines)
    ))

    def get_arg_data(name: str) -> dict:
        for doc in arg_docs:
            if doc['name'] == name:
                return doc

        return create_empty_argument(name)

    return list([get_arg_data(name) for name in arg_names])


def function(target: typing.Callable):
    """

    :param target:
    :return:
    """

    if not hasattr(target, '__code__'):
        return None

    lines = get_doc_lines(target)
    docs = filter(lambda line: not line.startswith(':'), lines)
    params = parse_params(target, lines)

    return dict(
        name=getattr(target, '__name__'),
        doc=' '.join(docs),
        params=params
    )


def container(target) -> dict:
    """

    :param target:
    :return:
    """

    function_names = filter(lambda name: not name.startswith('_'), dir(target))

    return dict(
        name=getattr(target, '__name__'),
        functions=list(filter(
            lambda data: (data is not None),
            [function(getattr(target, name)) for name in function_names]
        ))
    )
