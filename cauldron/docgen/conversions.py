def arg_type_to_string(arg_type) -> str:
    """
    Converts the argument type to a string

    :param arg_type:
    :return:
        String representation of the argument type. Multiple return types are
        turned into a comma delimited list of type names
    """

    union_params = (
        getattr(arg_type, '__union_params__', None) or
        getattr(arg_type, '__args__', None)
    )

    if union_params and isinstance(union_params, (list, tuple)):
        return ', '.join([arg_type_to_string(item) for item in union_params])

    try:
        return arg_type.__name__
    except AttributeError:
        return '{}'.format(arg_type)
