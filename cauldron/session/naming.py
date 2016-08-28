import os
import re


def split_filename(name: str) -> dict:
    """

    :param name:
    :return:
    """

    filename = os.path.basename(name)
    parts = filename.rsplit('.', 1)

    return dict(
        index=None,
        name=parts[0],
        extension=parts[1] if len(parts) > 1 else None
    )


def explode_filename(name: str, scheme: str) -> dict:
    """
    Removes any path components from the input filename and returns a
    dictionary containing the name of the file without extension and the
    extension (if an extension exists)

    :param name:
    :param scheme:
    :return:
    """

    if not scheme:
        return split_filename(name)

    replacements = {
        'name': '(?P<name>.*)',
        'ext': '(?P<extension>.+)$',
        'index': '(?P<index>[0-9]{{{length}}})'
    }

    scheme_pattern = '^'

    offset = 0
    while offset < len(scheme):
        char = scheme[offset]
        next_char = scheme[offset + 1] if (offset + 1) < len(scheme) else None

        if char in '.()^$?*+\[]|':
            scheme_pattern += '\\{}'.format(char)
            offset += 1
            continue

        if char != '{':
            scheme_pattern += char
            offset += 1
            continue

        if next_char != '{':
            scheme_pattern += char
            offset += 1
            continue

        end_index = scheme.find('}}', offset)

        contents = scheme[offset:end_index].strip('{}').lower()

        if contents in replacements:
            scheme_pattern += replacements[contents]
        elif contents == ('#' * len(contents)):
            scheme_pattern += replacements['index'].format(length=len(contents))
        else:
            scheme_pattern += '{{{}}}'.format(contents)

        offset = end_index + 2

    match = re.compile(scheme_pattern).match(name)

    if not match:
        return split_filename(name)

    index = match.group('index')
    index = int(index) if index else None

    return dict(
        index=index - 1,
        name=match.group('name'),
        extension=match.group('extension')
    )


def assemble_filename(
        name: str,
        scheme: str,
        extension: str = None,
        index: int = None
) -> str:
    """

    :param name:
    :param scheme:
    :param extension:
    :param index:
    :return:
    """

    if not name:
        name = ''

    if not extension:
        extension = 'py'

    if index is None:
        index = 0

    if not scheme:
        return '{}.{}'.format(name, extension)

    out = scheme

    pattern = re.compile('{{(?P<count>[#]+)}}')
    match = pattern.search(scheme)

    if match:
        out = '{before}{replace}{after}'.format(
            before=out[:match.start()],
            replace='{}'.format(index + 1).zfill(len(match.group('count'))),
            after=out[match.end():]
        )

    replacements = {
        '{{name}}': name,
        '{{ext}}': extension
    }

    for pattern, value in replacements.items():
        out = out.replace(pattern, value)

    parts = split_filename(out)

    if not name:
        parts['name'] = parts['name'].rstrip('-_: ')

    return '{}.{}'.format(parts['name'].strip(), parts['extension'])
