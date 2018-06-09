import os
import sys
import threading
import traceback
import typing
from textwrap import dedent
from textwrap import indent

from cauldron.environ import paths

_logging_paths = []


def add_output_path(path: str = None) -> str:
    """
    Adds the specified path to the output logging paths if it is not
    already in the listed paths.

    :param path:
        The path to add to the logging output paths. If the path is empty
        or no path is given, the current working directory will be used
        instead.
    """
    cleaned = paths.clean(path or os.getcwd())
    if cleaned not in _logging_paths:
        _logging_paths.append(cleaned)
    return cleaned


def remove_output_path(path: str = None) -> str:
    """
    Removes the specified path from the output logging paths if it is
    in the listed paths.

    :param path:
        The path to remove from the logging output paths. If the path is empty
        or no path is given, the current working directory will be used
        instead.
    """
    cleaned = paths.clean(path or os.getcwd())
    if cleaned in _logging_paths:
        _logging_paths.remove(path)
    return cleaned


def header(
        text: str,
        level: int = 1,
        whitespace: int = 0,
        whitespace_top: int = 1,
        whitespace_bottom: int = 0,
        trace: bool = True,
        file_path: str = None,
        append_to_file: bool = True,
        indent_by: int = 0
) -> str:
    """

    :param text:
    :param level:
    :param whitespace:
    :param whitespace_top:
    :param whitespace_bottom:
    :param trace:
    :param file_path:
    :param append_to_file:
    :param indent_by:
    :return:
    """
    if level == 0:
        message = text
    elif level < 3:
        char = ('=' if level == 1 else '-')
        message = '{bar}\n{indent}  {text}  {indent}\n{bar}'.format(
            bar=char * (len(text) + 8),
            indent='::',
            text=text
        )
    elif level < 5:
        message = '{text}\n{bar}'.format(
            bar=('=' if level == 3 else '-') * len(text),
            text=text
        )
    elif level < 7:
        message = '{bar} {text} {bar}'.format(
            bar=('=' if level == 5 else '-') * 3,
            text=text
        )
    else:
        message = text

    return log(
        message,
        whitespace=whitespace,
        whitespace_top=whitespace_top,
        whitespace_bottom=whitespace_bottom,
        trace=trace,
        file_path=file_path,
        append_to_file=append_to_file,
        indent_by=indent_by
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
        whitespace_bottom=max(0, line_count - 1),
        trace=trace,
        file_path=file_path,
        append_to_file=append_to_file
    )


def log(
        message: typing.Union[str, typing.List[str]],
        whitespace: int = 0,
        whitespace_top: int = 0,
        whitespace_bottom: int = 0,
        indent_by: int = 0,
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
    :param indent_by:
        The number of spaces that each line of text should be indented
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

    message = indent('\n'.join(m), ' ' * indent_by)
    raw(
        message=message,
        trace=trace,
        file_path=file_path,
        append_to_file=append_to_file
    )
    return message


def raw(
        message: str,
        trace: bool = True,
        file_path: str = None,
        append_to_file: bool = True
):
    """

    :param message:
    :param trace:
    :param file_path:
    :param append_to_file:
    :return:
    """

    if trace:
        print(message)

    # Store the logged information as an entry in the current thread if the
    # thread has as logs variable for such storage. These logs are used to
    # store logs in CauldronThreads, which are then transmitted from kernels
    # to Cauldron interfaces for display feedback
    if hasattr(threading.current_thread(), 'logs'):
        threading.current_thread().logs.append(message)

    def write_file(write_path: str):
        mode = 'a' if append_to_file and os.path.exists(write_path) else 'w'
        with open(paths.clean(write_path), mode) as f:
            f.write('{}\n'.format(message))

    file_paths = list(set([p for p in (_logging_paths + [file_path]) if p]))
    for path in file_paths:
        write_file(path)


def add_to_message(data, indent_level=0) -> list:
    """Adds data to the message object"""
    message = []

    if isinstance(data, str):
        message.append(indent(
            dedent(data.strip('\n')).strip(),
            indent_level * '  '
        ))
        return message

    for line in data:
        offset = 0 if isinstance(line, str) else 1
        message += add_to_message(line, indent_level + offset)
    return message


def get_error_stack() -> typing.List[dict]:
    frames = traceback.extract_tb(sys.exc_info()[-1])

    stack = []
    for frame in frames:
        filename = frame.filename
        location = frame.name

        if location == '<module>':
            location = None
        elif location:
            location = location.split('__cauldron_shared_libs')[-1]

        stack.append(dict(
            filename=filename,
            location=location,
            line_number=frame.lineno,
            line=frame.line
        ))

    return stack
