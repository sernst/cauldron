import json
import os
import typing
from collections import namedtuple

from cauldron import environ
from cauldron.session import projects
from cauldron.session.writing import file_io
from cauldron.session.writing import components

STEP_DATA = namedtuple('STEP_DATA', [
    'name',
    'status',
    'has_error',
    'body',
    'data',
    'includes',
    'cauldron_version',
    'file_writes'
])


def create_data(step: 'projects.ProjectStep') -> STEP_DATA:
    """
    Creates the data object that stores the step information in the notebook
    results JavaScript file.

    :param step:
        Project step for which to create the data
    :return:
        Step data tuple containing scaffold data structure for the step output.
        The dictionary must then be populated with data from the step to
        correctly reflect the current state of the step.

        This is essentially a "blank" step dictionary, which is what the step
        would look like if it had not yet run
    """

    return STEP_DATA(
        name=step.definition.name,
        status=step.status(),
        has_error=False,
        body=None,
        data=dict(),
        includes=[],
        cauldron_version=list(environ.version_info),
        file_writes=[]
    )


def get_cached_data(
        step: 'projects.ProjectStep'
) -> typing.Union[None, STEP_DATA]:
    """
    Attempts to load and return the cached step data for the specified step. If
    not cached data exists, or the cached data is corrupt, a None value is
    returned instead.

    :param step:
        The step for which the cached data should be loaded

    :return:
        Either a step data structure containing the cached step data or None
        if no cached data exists for the step
    """

    cache_path = step.report.results_cache_path
    if not os.path.exists(cache_path):
        return None

    out = create_data(step)

    try:
        with open(cache_path, 'r') as f:
            cached_data = json.load(f)
    except Exception:
        return None

    file_writes = [
        file_io.entry_from_dict(fw)
        for fw in cached_data['file_writes']
    ]

    return out \
        ._replace(**cached_data) \
        ._replace(file_writes=file_writes)


def make_cache_write_entry(
        step: 'projects.ProjectStep',
        step_data: STEP_DATA
) -> file_io.FILE_WRITE_ENTRY:
    """

    :param step:
    :param step_data:
    :return:
    """

    cache_path = step.report.results_cache_path
    if not cache_path:
        return None

    storable_step_data = step_data \
        ._replace(file_writes=[fw._asdict() for fw in step_data.file_writes]) \
        ._asdict()

    return file_io.FILE_WRITE_ENTRY(
        path=environ.paths.clean(cache_path),
        contents=json.dumps(storable_step_data)
    )


def populate_data(step: 'projects.ProjectStep') -> STEP_DATA:
    """

    :param step:
    :return:
    """

    step_data = create_data(step)
    report = step.report

    component = components.get(step)

    includes = step_data.includes.copy()
    includes.extend([include._asdict() for include in component.includes])

    file_writes = step_data.file_writes.copy()
    file_writes.extend(component.files)

    return step_data._replace(
        has_error=step.error,
        body=step.get_dom(),
        data=(
            step_data.data
            .copy()
            .update(report.data.fetch(None))
        ),
        includes=includes,
        file_writes=file_writes
    )


def serialize(step: 'projects.ProjectStep') -> STEP_DATA:
    """

    :param step:
    :return:
    """

    def disable_caching():
        return step.is_running or step.last_modified or step.error

    cached = None if disable_caching() else get_cached_data(step)
    if cached:
        return cached

    if step.is_muted:
        return create_data(step)

    step_data = populate_data(step)

    # Add cache of step data to the file writes list
    file_writes = step_data.file_writes.copy()
    file_writes.append(make_cache_write_entry(step, step_data))

    return step_data._replace(file_writes=file_writes)
