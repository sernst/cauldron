import typing
from textwrap import dedent


def log(
        message: typing.Union[str, typing.List[str]],
        whitespace: int = 0,
        whitespace_top: int = 0,
        whitespace_bottom: int = 0,
        **kwargs
) -> str:
    """
    Logs a message to the console with the formatting support beyond a simple
    print statement or logger statement.

    :param message:
        The primary log message for the entry
    :param whitespace:
        The number of lines of whitespace to append to the beginning and end
        of the log message when printed to the console
    :param whitespace_top:
        The number of lines of whitespace to append to the beginning only of
        the log message when printed to the console. If whitespace_top and
        whitespace are both specified, the larger of the two values will be
        used.
    :param whitespace_bottom:
        The number of lines of whitespace to append to the end of the log
        message when printed to the console. If whitespace_bottom and
        whitespace are both specified, the larger of hte two values will be
        used.
    :param kwargs:
    """

    m = add_to_message(message)
    for key, value in kwargs.items():
        m.append('{key}: {value}'.format(key=key, value=value))

    message = dedent('\n'.join(m).strip('\n')).strip()

    pre_whitespace = int(max(whitespace, whitespace_top))
    post_whitespace = int(max(whitespace, whitespace_bottom))

    if pre_whitespace:
        print(pre_whitespace * '\n')
    print(message)
    if post_whitespace:
        print(post_whitespace * '\n')

    return message


def add_to_message(data, indent_level=0):
    """ Adds data to the message object """

    m = []

    if isinstance(data, str):
        m.append('{}{}'.format(indent_level * '  ', data))
        return m

    for line in data:
        if isinstance(line, str):
            m += add_to_message(line, indent_level)
        else:
            m += add_to_message(line, indent_level + 1)
    return m
