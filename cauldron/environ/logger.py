import typing
from textwrap import dedent
from textwrap import indent

from cauldron.environ import paths


def header(
        text: str,
        bar_char: str = '=',
        whitespace: int = 0,
        whitespace_top: int = 1,
        whitespace_bottom: int = 0,
        trace: bool = True,
        file_path: str = None,
        append_to_file: bool = True
) -> str:
    """

    :param text:
    :param bar_char:
    :param whitespace:
    :param whitespace_top:
    :param whitespace_bottom:
    :param trace:
    :param file_path:
    :param append_to_file:
    :return:
    """

    return log(
        '{bar}\n{text}\n{bar}'.format(bar=bar_char * len(text), text=text),
        whitespace=whitespace,
        whitespace_top=whitespace_top,
        whitespace_bottom=whitespace_bottom,
        trace=trace,
        file_path=file_path,
        append_to_file=append_to_file
    )


def blanks(
        line_count: int = 1,
        trace: bool = True,
        file_path: str = None,
        append_to_file: bool = True
) -> str:
    """

    :param line_count:
    :param trace:
    :param file_path:
    :param append_to_file:
    :return:
    """

    return log(
        '',
        whitespace_bottom=line_count,
        trace=trace,
        file_path=file_path,
        append_to_file=append_to_file
    )


def log(
        message: typing.Union[str, typing.List[str]],
        whitespace: int = 0,
        whitespace_top: int = 0,
        whitespace_bottom: int = 0,
        trace: bool = True,
        file_path: str = None,
        append_to_file: bool = True,
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
    :param trace:
        Whether or not to trace the output to the console
    :param file_path:
        A path to a logging file where the output should be written
    :param append_to_file:
        Whether or not the log entry should be overwritten or appended to the
        log file specified in the file_path argument
    :param kwargs:
    """

    m = add_to_message(message)
    for key, value in kwargs.items():
        m.append('{key}: {value}'.format(key=key, value=value))

    pre_whitespace = int(max(whitespace, whitespace_top))
    post_whitespace = int(max(whitespace, whitespace_bottom))

    if pre_whitespace:
        m.insert(0, max(0, pre_whitespace - 1) * '\n')
    if post_whitespace:
        m.append(max(0, post_whitespace - 1) * '\n')

    message = '\n'.join(m)
    if trace:
        print(message)
    if file_path:
        file_path = paths.clean(file_path)
        with open(file_path, 'a+' if append_to_file else 'w+') as f:
            f.write('{}\n'.format(message))
    return message


def add_to_message(data, indent_level=0) -> list:
    """ Adds data to the message object """

    m = []

    if isinstance(data, str):
        m.append(indent(
            dedent(data.strip('\n')).strip(),
            indent_level * '  '
        ))
        return m

    for line in data:
        if isinstance(line, str):
            m += add_to_message(line, indent_level)
        else:
            m += add_to_message(line, indent_level + 1)
    return m
