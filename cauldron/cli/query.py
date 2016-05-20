import re
import typing

from cauldron import environ


def confirm(question: str, default: bool = True) -> bool:
    """
    Requests confirmation of the specified question and returns that result

    :param question:
        The question to print to the console for the confirmation
    :param default:
        The default value if the user hits enter without entering a value
    """

    result = input('{question} [{yes}/{no}]:'.format(
        question=question,
        yes='(Y)' if default else 'Y',
        no='N' if default else '(N)'
    ))

    if not result:
        return default

    if result[0].lower() in ['y', 't', '1']:
        return True
    return False


def choice(
        title: str,
        prompt: str,
        choices: list,
        default_index: int = None
) -> typing.Tuple[int, str]:
    """

    :param title:
    :param prompt:
    :param choices:
    :param default_index:
    :return:
    """

    entries = []
    for index in range(len(choices)):
        entries.append('[{index}]: {value}'.format(
            index=index + 1,
            value=choices[index]
        ))

    entries.insert(0, '')
    entries.insert(
        0,
        '{bar}\n{title}\n{bar}'.format(title=title, bar='-' * len(title))
    )
    environ.log(entries, whitespace=1)

    default = ''
    if default_index is not None:
        default = ' [{}]'.format(1 + max(0, min(len(choices), default_index)))

    while True:
        result = input('{question}{default}:'.format(
            question=prompt,
            default=default
        ))

        result = re.compile('[^0-9]*').sub('', result)
        if len(result) == 0:
            if default_index is None:
                continue

            result = default_index
        else:
            result = max(0, min(int(result) - 1, len(choices)))

        return result, choices[result]
