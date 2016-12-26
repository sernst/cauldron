
TESTING = 'testing'

SINGLE_RUN = 'single_run'

INTERACTIVE = 'interactive'

_current_modes = []


def has(mode_id: str) -> bool:
    return bool(mode_id in _current_modes)


def add(mode_id: str):
    if mode_id not in _current_modes:
        _current_modes.append(mode_id)

    return _current_modes.copy()


def remove(mode_id: str) -> bool:
    if mode_id not in _current_modes:
        return False

    _current_modes.remove(mode_id)
    return True


class ExposedModes:

    @staticmethod
    def is_interactive() -> bool:
        return has(INTERACTIVE)

    @staticmethod
    def is_test() -> bool:
        return has(TESTING)

    @staticmethod
    def is_single_run() -> bool:
        return has(SINGLE_RUN)

