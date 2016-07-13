from cauldron import environ
from cauldron.cli import commander
from cauldron.test.support import scaffolds


def create_project(
        tester: scaffolds.ResultsTest,
        name: str,
        path: str = None,
        **kwargs
) -> 'environ.Response':
    """

    :param tester:
    :param name:
    :param path:
    :param kwargs:
    :return:
    """

    if path is None:
        path = tester.get_temp_path('projects')

    r = environ.Response()

    args = [name, path]
    for key, value in kwargs.items():
        args.append('--{}="{}"'.format(key, value))
    args = ' '.join([a for a in args if a and len(a) > 0])

    commander.execute('create', args, r)

    return r


def open_project(
        tester: scaffolds.ResultsTest,
        path: str
) -> 'environ.Response':
    """

    :param tester:
    :param path:
    :return:
    """

    r = environ.Response()
    commander.execute('open', path, r)
    return r

