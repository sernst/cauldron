import typing
from cauldron.docgen import conversions


def parse(target, lines: typing.List[str]) -> typing.Union[None, dict]:
    """

    :param target:
    :param lines:
    :return:
    """

    annotations = getattr(target, '__annotations__')
    annotations = annotations if annotations is not None else {}
    arg_type = annotations.get('return')
    return_type = (
        None
        if arg_type is None else
        conversions.arg_type_to_string(arg_type)
    )

    description = ' '.join([
        line[1:].split(':', 1)[-1].strip()
        for line in filter(lambda line: line.startswith(':return'), lines)
    ]).strip()

    return dict(
        type=return_type,
        description=description
    )
