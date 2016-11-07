from cauldron import environ
from cauldron import templating


def render_tree(inspected_data: dict):
    """

    :param inspected_data:
    :return:
    """

    environ.abort_thread()

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

    environ.abort_thread()

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
