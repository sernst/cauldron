from cauldron import environ
from cauldron.session.projects import specio


def get_recent_projects() -> specio.ProjectSpecsReader:
    """
    Loads contextual and configuration information for all projects
    in the recent project paths persistent environment setting. Each
    item in the returned list is a loaded ``cauldron.json`` file for
    an entry in that recent project path list that has been enriched
    with information about that project (e.g. modified timestamp) that
    can be used for the display of that project. Any paths that are
    found to no longer exist will be ignored and excluded from the
    returned list of results.
    """
    paths = environ.configs.fetch('recent_paths', [])
    specs = specio.ProjectSpecsReader()

    for path in paths:
        specs.add(path)

    return specs
