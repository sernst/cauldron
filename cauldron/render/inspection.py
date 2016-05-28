import json
from cauldron import templating


def render_tree(inspected_data: dict):
    """

    :param inspected_data:
    :return:
    """

    def to_jstree_node(d: dict) -> dict:
        children = d.get('structure', [])
        if isinstance(children, (list, tuple)):
            children = [to_jstree_node(x) for x in children]
        else:
            children = []

        return dict(
            text='{} ({})'.format(d['key'], d['type']),
            children=children
        )

    data = [to_jstree_node(v) for v in inspected_data['structure']]

    return templating.render_template('tree.html', data=data)


def inspect_data(source_key: str = None, source=None) -> dict:
    """

    :param source_key:
    :param source:
    :return:
    """

    if isinstance(source, dict):
        out = {
            'type': 'dict',
            'key': source_key,
            'structure': []
        }

        for key, value in source.items():
            out['structure'].append(inspect_data(key, value))
        return out

    if isinstance(source, (list, tuple)):
        return {
            'type': 'list',
            'length': len(source),
            'key': source_key,
            'structure': inspect_data(None, source[0])
        }

    if isinstance(source, str):
        return {'type': 'str', 'key': source_key, 'structure': None}

    if isinstance(source, (float, int)):
        return {'type': 'number', 'key': source_key, 'structure': None}

    if isinstance(source, bool):
        return {'type': 'bool', 'key': source_key, 'structure': None}

    return {'type': 'None', 'key': source_key, 'structure': None}


def echo_inspection_data(
        source: dict,
        indent: int,
        entries: list = None
) -> list:
    """

    :return:
    """

    if entries is None:
        entries = []

    prefix = '  ' * max(0, indent)
    key = source.get('key')
    structure = source.get('structure')
    source_type = source.get('type')

    if structure and source_type == 'list':
        item_type = structure.get('type')
        if item_type != 'list':
            source_type += ' {}'.format(item_type)
            structure = structure.get('structure')
        source_type += '[{}]'.format(source.get('length', 0))

    if indent >= 0:
        entries.append('{prefix}*{key} {type}'.format(
            prefix=prefix,
            key=' {}:'.format(key) if key else '',
            type=source_type
        ))

    if structure is None:
        return entries

    if isinstance(structure, str):
        entries[-1] + ' {}'.format(structure)
        return entries

    if isinstance(structure, dict):
        echo_inspection_data(structure, indent + 1, entries)
        return entries

    if isinstance(structure, (list, tuple)):
        for entry in structure:
            echo_inspection_data(entry, indent + 1, entries)
        return entries


def inspect_json_structure(path: str) -> dict:
    """
    Opens the JSON file at the specified path and returns a dictionary
    representation of its structure.

    :param path:
        The path to the JSON file to be inspected
    """

    with open(path, 'r+') as f:
        data = json.load(f)

    return inspect_data(source=data)


def echo_json_structure(path: str) -> str:
    """
    Opens the JSON file at the specified path and returns a string
    representation of its structure, including the data types of the constituent
    elements

    :param path:
        The source path to the JSON file
    """

    out = []
    echo_inspection_data(inspect_json_structure(path), -1, out)
    return '\n'.join(out)
