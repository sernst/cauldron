import typing
import inspect
from cauldron.docgen import conversions


def get_args_index(target) -> int:
    """
    Returns the index of the "*args" parameter if such a parameter exists in
    the function arguments or -1 otherwise.

    :param target:
        The target function for which the args index should be determined
    :return:
        The arguments index if it exists or -1 if not
    """

    code = target.__code__

    if not bool(code.co_flags & inspect.CO_VARARGS):
        return -1

    return code.co_argcount + code.co_kwonlyargcount


def get_kwargs_index(target) -> int:
    """
    Returns the index of the "**kwargs" parameter if such a parameter exists in
    the function arguments or -1 otherwise.

    :param target:
        The target function for which the kwargs index should be determined
    :return:
        The keyword arguments index if it exists or -1 if not
    """

    code = target.__code__

    if not bool(code.co_flags & inspect.CO_VARKEYWORDS):
        return -1

    return (
        code.co_argcount +
        code.co_kwonlyargcount +
        (1 if code.co_flags & inspect.CO_VARARGS else 0)
    )


def get_arg_names(target) -> typing.List[str]:
    """
    Gets the list of named arguments for the target function

    :param target:
        Function for which the argument names will be retrieved
    """

    code = getattr(target, '__code__')

    if code is None:
        return []

    arg_count = code.co_argcount
    kwarg_count = code.co_kwonlyargcount
    args_index = get_args_index(target)
    kwargs_index = get_kwargs_index(target)

    arg_names = list(code.co_varnames[:arg_count])
    if args_index != -1:
        arg_names.append(code.co_varnames[args_index])
    arg_names += list(code.co_varnames[arg_count:(arg_count + kwarg_count)])
    if kwargs_index != -1:
        arg_names.append(code.co_varnames[kwargs_index])
    if len(arg_names) > 0 and arg_names[0] in ['self', 'cls']:
        arg_count -= 1
        arg_names.pop(0)

    return arg_names


def create_argument(target, name, description: str = '') -> dict:
    """
    Creates a dictionary representation of the parameter

    :param target:
        The function object in which the parameter resides
    :param name:
        The name of the parameter
    :param description:
        The documentation description for the parameter
    """

    arg_names = get_arg_names(target)
    annotations = getattr(target, '__annotations__', {})

    out = dict(
        name=name,
        index=arg_names.index(name),
        description=description,
        type=conversions.arg_type_to_string(annotations.get(name, 'Any'))
    )
    out.update(get_optional_data(target, name, arg_names))
    return out


def explode_line(argument_line: str) -> typing.Tuple[str, str]:
    """
    Returns a tuple containing the parameter name and the description parsed
    from the given argument line
    """

    parts = tuple(argument_line.split(' ', 1)[-1].split(':', 1))
    return parts if len(parts) > 1 else (parts[0], '')


def get_optional_data(target, name, arg_names):
    """

    :param target:
    :param name:
    :param arg_names:
    :return:
    """

    defaults = target.__defaults__
    args_index = get_args_index(target)
    kwargs_index = get_kwargs_index(target)
    offset = (kwargs_index != -1) + (args_index != -1)
    index = arg_names.index(name)

    try:
        default_index = index - (len(arg_names) - len(defaults) - offset)
    except Exception:
        default_index = -1

    if index == kwargs_index:
        return {'optional': True, 'default': 'dict'}

    if default_index < 0:
        return {'optional': False}

    return {'optional': True, 'default': str(defaults[default_index])}


def parse(target, lines: list) -> list:
    """

    :param target:
    :param lines:
    :return:
    """

    arg_docs = list(map(
        lambda line: create_argument(target, *explode_line(line)),
        filter(lambda line: line.startswith(':param'), lines)
    ))

    def get_arg_data(name: str) -> dict:
        args = dict([(doc['name'], doc) for doc in arg_docs])
        data = args.get(name)
        return data if data is not None else create_argument(target, name)

    return list([get_arg_data(name) for name in get_arg_names(target)])
