
TESTING = 'testing'

SINGLE_RUN = 'single_run'

INTERACTIVE = 'interactive'

_current_modes = []


def has(mode_id: str) -> bool:
    """
    Returns whether or not the specified mode identifier is currently active
    or not.
    """

    return bool(mode_id in _current_modes)


def add(mode_id: str) -> list:
    """
    Adds the specified mode identifier to the list of active modes and returns
    a copy of the currently active modes list.
    """

    if not has(mode_id):
        _current_modes.append(mode_id)
    return _current_modes.copy()


def remove(mode_id: str) -> bool:
    """
    Removes the specified mode identifier from the active modes and returns
    whether or not a remove operation was carried out. If the mode identifier
    is not in the currently active modes, it does need to be removed.
    """

    had_mode = has(mode_id)

    if had_mode:
        _current_modes.remove(mode_id)

    return had_mode


class ExposedModes:
    """ Exposed class for checking the status of the currently active modes """

    INTERACTIVE = INTERACTIVE
    TESTING = TESTING
    SINGLE_RUN = SINGLE_RUN

    @staticmethod
    def has_mode(mode_id) -> bool:
        return has(mode_id)

    @staticmethod
    def is_interactive() -> bool:
        return has(INTERACTIVE)

    @staticmethod
    def is_test() -> bool:
        return has(TESTING)

    @staticmethod
    def is_single_run() -> bool:
        return has(SINGLE_RUN)
