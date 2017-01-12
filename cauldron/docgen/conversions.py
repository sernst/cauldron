

def arg_type_to_string(arg_type) -> str:
    """
    Converts the argument type to a string

    :param arg_type:
    :return:
        String representation of the argument type. Multiple return types are
        turned into a comma delimited list of type names
    """

    if hasattr(arg_type, '__union_params__'):
        return ', '.join([
            arg_type_to_string(item)
            for item in arg_type.__union_params__
        ])

    try:
        return arg_type.__name__
    except:
        return arg_type
