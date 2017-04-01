import json
import time
import typing


def attempt_file_write(
        path: str,
        contents,
        mode: str
) -> typing.Union[None, Exception]:
    """ """
    try:
        with open(path, mode) as f:
            f.write(contents)
    except Exception as error:
        return error

    return None


def write_file(
        path: str,
        contents,
        mode: str = 'w',
        retry_count: int = 3
) -> typing.Tuple[bool, typing.Union[None, Exception]]:
    """ """

    error = None
    for i in range(retry_count):
        error = attempt_file_write(path, contents, mode)
        if error is None:
            return True, None
        time.sleep(0.2)

    return False, error


def attempt_json_write(
        path: str,
        contents,
        mode: str
) -> typing.Union[None, Exception]:
    """ """
    try:
        with open(path, mode) as f:
            json.dump(contents, f)
    except Exception as error:
        return error

    return None


def write_json_file(
        path: str,
        contents,
        mode: str = 'w',
        retry_count: int = 3
) -> typing.Tuple[bool, typing.Union[None, Exception]]:
    """ """

    error = None
    for i in range(retry_count):
        error = attempt_json_write(path, contents, mode)
        if error is None:
            return True, None
        time.sleep(0.2)

    return False, error
