import importlib
import os
import sys
import types
import typing

from cauldron import session


def get_module(name: str) -> typing.Union[types.ModuleType, None]:
    """
    Retrieves the loaded module for the given module name or returns None if
    no such module has been loaded.

    :param name:
        The name of the module to be retrieved
    :return:
        Either the loaded module with the specified name, or None if no such
        module has been imported.
    """
    return sys.modules.get(name)


def get_module_name(module: types.ModuleType) -> str:
    """
    Returns the name of the specified module by looking up its name in
    multiple ways to prevent incompatibility issues.

    :param module:
        A module object for which to retrieve the name.
    """
    try:
        return module.__spec__.name
    except AttributeError:
        return module.__name__


def do_reload(module: types.ModuleType, newer_than: int) -> bool:
    """
    Executes the reload of the specified module if the source file that it was
    loaded from was updated more recently than the specified time

    :param module:
        A module object to be reloaded
    :param newer_than:
        The time in seconds since epoch that should be used to determine if
        the module needs to be reloaded. If the module source was modified
        more recently than this time, the module will be refreshed.
    :return:
        Whether or not the module was reloaded
    """
    path = getattr(module, '__file__')
    directory = getattr(module, '__path__', [None])[0]

    if path is None and directory:
        path = os.path.join(directory, '__init__.py')

    last_modified = os.path.getmtime(path)

    if last_modified < newer_than:
        return False

    try:
        importlib.reload(module)
        return True
    except ImportError:
        return False


def reload_children(parent_module: types.ModuleType, newer_than: int) -> bool:
    """
    Reloads all imported children of the specified parent module object

    :param parent_module:
        A module object whose children should be refreshed if their
        currently loaded versions are out of date.
    :param newer_than:
        An integer time in seconds for comparison. Any children modules that
        were modified more recently than this time will be reloaded.
    :return:
        Whether or not any children were reloaded
    """
    if not hasattr(parent_module, '__path__'):
        return False

    parent_name = get_module_name(parent_module)

    children = filter(
        lambda item: item[0].startswith(parent_name),
        sys.modules.items()
    )

    return any([do_reload(item[1], newer_than) for item in children])


def reload_module(
        module: typing.Union[str, types.ModuleType],
        recursive: bool,
        force: bool
) -> bool:
    """
    Reloads the specified module, which can either be a module object or
    a string name of a module. Will not reload a module that has not been
    imported

    :param module:
        A module object or string module name that should be refreshed if its
        currently loaded version is out of date or the action is forced.
    :param recursive:
        When true, any imported sub-modules of this module will also be
        refreshed if they have been updated.
    :param force:
        When true, all modules will be refreshed even if it doesn't appear
        that they have been updated.
    :return:
    """

    if isinstance(module, str):
        module = get_module(module)

    if module is None or not isinstance(module, types.ModuleType):
        return False

    try:
        step = session.project.get_internal_project().current_step
        modified = step.last_modified if step else None
    except AttributeError:
        modified = 0

    if modified is None:
        # If the step has no modified time it hasn't been run yet and
        # a reload won't be needed
        return False

    newer_than = modified if not force and modified else 0

    if recursive:
        children_reloaded = reload_children(module, newer_than)
    else:
        children_reloaded = False
    reloaded = do_reload(module, newer_than)

    return reloaded or children_reloaded


def refresh(
        *modules: typing.Union[str, types.ModuleType],
        recursive: bool = False,
        force: bool = False
) -> bool:
    """
    Checks the specified module or modules for changes and reloads them if
    they have been changed since the module was first imported or last
    refreshed.

    :param modules:
        One or more module objects that should be refreshed if they the
        currently loaded versions are out of date. The package name for
        modules can also be used.
    :param recursive:
        When true, any imported sub-modules of this module will also be
        refreshed if they have been updated.
    :param force:
        When true, all modules will be refreshed even if it doesn't appear
        that they have been updated.
    :return:
        True or False depending on whether any modules were refreshed by this
        call.
    """

    out = []
    for module in modules:
        out.append(reload_module(module, recursive, force))

    return any(out)
