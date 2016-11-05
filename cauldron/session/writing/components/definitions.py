import functools
import typing
from collections import namedtuple

COMPONENT = namedtuple('COMPONENT', ['includes', 'files'])
WEB_INCLUDE = namedtuple('WEB_INCLUDE', ['name', 'src'])


def merge_components(
        *components: typing.List[typing.Union[list, tuple, COMPONENT]]
) -> COMPONENT:
    """
    Merges multiple COMPONENT instances into a single one by merging the
    lists of includes and files. Has support for elements of the components
    arguments list to be lists or tuples of COMPONENT instances as well.

    :param components:
    :return:
    """

    flat_components = functools.reduce(flatten_reducer, components, [])
    return COMPONENT(
        includes=functools.reduce(
            functools.partial(combine_lists_reducer, 'includes'),
            flat_components,
            []
        ),
        files=functools.reduce(
            functools.partial(combine_lists_reducer, 'files'),
            flat_components,
            []
        )
    )


def flatten_reducer(
        flattened_list: list,
        entry: typing.Union[list, tuple, COMPONENT]
) -> list:
    """
    Flattens a list of COMPONENT instances to remove any lists or tuples
    of COMPONENTS contained within the list

    :param flattened_list:
        The existing flattened list that has been populated from previous
        calls of this reducer function
    :param entry:
        An entry to be reduced. Either a COMPONENT instance or a list/tuple
        of COMPONENT instances
    :return:
        The flattened list with the entry flatly added to it
    """

    if hasattr(entry, 'includes') and hasattr(entry, 'files'):
        flattened_list.append(entry)
    elif entry:
        flattened_list.extend(entry)
    return flattened_list


def combine_lists_reducer(
        key: str,
        merged_list: list,
        component: COMPONENT
) -> list:
    """
    Reducer function to combine the lists for the specified key into a
    single, flat list

    :param key:
        The key on the COMPONENT instances to operate upon
    :param merged_list:
        The accumulated list of values populated by previous calls to this
        reducer function
    :param component:
        The COMPONENT instance from which to append values to the
        merged_list
    :return:
        The updated merged_list with the values for the COMPONENT added
        onto it
    """

    merged_list.extend(getattr(component, key))
    return merged_list
