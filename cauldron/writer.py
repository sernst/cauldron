import json
import time
import typing


def attempt_file_write(
        path: str,
        contents: typing.Union[str, bytes],
        mode: str = 'w'
) -> typing.Union[None, Exception]:
    """
    Attempts to write the specified contents to a file and returns None if
    successful, or the raised exception if writing failed.
    
    :param path:
        The path to the file that will be written
    :param contents:
        The contents of the file to write
    :param mode:
        The mode in which the file will be opened when written
    :return:
        None if the write operation succeeded. Otherwise, the exception that
        was raised by the failed write action.
    """

    try:
        with open(path, mode) as f:
            f.write(contents)
        return None
    except Exception as error:
        return error


def write_file(
        path: str,
        contents,
        mode: str = 'w',
        retry_count: int = 3
) -> typing.Tuple[bool, typing.Union[None, Exception]]:
    """
    Writes the specified contents to a file, with retry attempts if the write
    operation fails. This is useful to prevent OS related write collisions with
    files that are regularly written to and read from quickly.
    
    :param path:
        The path to the file that will be written
    :param contents:
        The contents of the file to write
    :param mode:
        The mode in which the file will be opened when written
    :param retry_count:
        The number of attempts to make before giving up and returning a
        failed write.
    :return:
        Returns two arguments. The first is a boolean specifying whether or
        not the write operation succeeded. The second is the error result, which
        is None if the write operation succeeded. Otherwise, it will be the 
        exception that was raised by the last failed write attempt.
    """

    error = None
    for i in range(retry_count):
        error = attempt_file_write(path, contents, mode)
        if error is None:
            return True, None
        time.sleep(0.2)

    return False, error


def attempt_json_write(
        path: str,
        contents: dict,
        mode: str = 'w'
) -> typing.Union[None, Exception]:
    """
    Attempts to write the specified JSON content to file.
    
    :param path: 
        The path to the file where the JSON serialized content will be written.
    :param contents: 
        The JSON data to write to the file
    :param mode: 
        The mode used to open the file where the content will be written.
    :return: 
        None if the write operation succeeded. Otherwise, the exception that
        was raised by the failed write operation.
    """

    try:
        with open(path, mode) as f:
            json.dump(contents, f)
        return None
    except Exception as error:
        return error


def write_json_file(
        path: str,
        contents: dict,
        mode: str = 'w',
        retry_count: int = 3
) -> typing.Tuple[bool, typing.Union[None, Exception]]:
    """
    Writes the specified dictionary to a file as a JSON-serialized string, 
    with retry attempts if the write operation fails. This is useful to prevent 
    OS related write collisions with files that are regularly written to and 
    read from quickly.
    
    :param path:
        The path to the file that will be written
    :param contents:
        The contents of the file to write
    :param mode:
        The mode in which the file will be opened when written
    :param retry_count:
        The number of attempts to make before giving up and returning a
        failed write.
    :return:
        Returns two arguments. The first is a boolean specifying whether or
        not the write operation succeeded. The second is the error result, which
        is None if the write operation succeeded. Otherwise, it will be the 
        exception that was raised by the last failed write attempt.
    """

    error = None
    for i in range(retry_count):
        error = attempt_json_write(path, contents, mode)
        if error is None:
            return True, None
        time.sleep(0.2)

    return False, error
