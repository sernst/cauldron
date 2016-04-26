import os
import typing
import json
import shutil

from cauldron import environ
from cauldron import templating
from cauldron.session.caching import SharedCache
from cauldron.reporting.report import Report


class ExposedProject(object):

    def __init__(self):
        self._project = None

    @property
    def internal_project(self) -> 'Project':
        return self._project

    @property
    def display(self) -> Report:
        return self._project.current_step

    @property
    def shared(self) -> SharedCache:
        return self._project.shared

    @property
    def settings(self) -> SharedCache:
        return self._project.settings

    def load(self, project: typing.Union['Project', None]):
        self._project = project


class Project(object):

    def __init__(
            self,
            source_path: str,
            results_path: str = None,
            identifier: str = None,
            shared: typing.Union[dict, SharedCache] = None
    ):
        """
        :param source_path:
        :param results_path:
            [optional] The path where the results files for the project will
            be saved. If omitted, the default global results path will be
            used.
        :param identifier:
            [optional] The project unique identifier. If omitted, the
            identifier will be loaded from the settings file, or assigned
        :param shared:
            [optional] The shared data cache used to store
        """

        source_path = environ.paths.clean(source_path)
        if os.path.isfile(source_path):
            source_path = os.path.dirname(source_path)
        self.source_path = source_path

        settings = load_project_settings(self.source_path)

        self.id = identifier if identifier else settings.get('id', 'unknown')
        self.steps = []
        self._results_path = results_path
        self._current_step = None

        def as_shared_cache(source):
            if source is None:
                return SharedCache()
            if not hasattr(source, 'fetch'):
                return SharedCache().put(**source)
            return source

        self.settings = as_shared_cache(settings)
        self.shared = as_shared_cache(shared)

        for step_name in self.settings.steps:
            self.steps.append(Report(step_name))

    @property
    def current_step(self) -> Report:
        if self._current_step:
            return self._current_step
        return self.steps[0]

    @current_step.setter
    def current_step(self, value: typing.Union[Report, None]):
        self._current_step = value

    @property
    def results_path(self):
        if self._results_path:
            return self._results_path

        if self.settings and self.settings['path_results']:
            return self.settings['path_results']

        return environ.configs.make_path(
            'results',
            override_key='results_path'
        )

    @results_path.setter
    def results_path(self, value):
        self._results_path = environ.paths.clean(value)

    @property
    def url(self):
        """
        Returns the URL that will open this project results file in the browser
        :return:
        """

        if not self.results_path:
            return None

        return 'file://{path}?id={id}'.format(
            path=os.path.join(self.results_path, 'report.html'),
            id=self.id
        )

    @property
    def directory(self):
        """
        Returns the directory where the project results files will be written
        :return:
        """

        if not self.results_path:
            return None

        return os.path.join(self.results_path, 'reports', self.id)

    def refresh(self):
        """

        :return:
        """
        self.settings.clear().put(**load_project_settings(self.source_path))

    def write(self) -> str:
        """

        :return:
        """

        if os.path.exists(self.directory):
            try:
                shutil.rmtree(self.directory)
            except Exception:
                try:
                    shutil.rmtree(self.directory)
                except Exception:
                    return None

        os.makedirs(self.directory)

        body = []
        data = {}
        files = {}
        for step in self.steps:
            body += step.body
            data.update(step.data.fetch(None))
            files.update(step.files.fetch(None))

        report_path = os.path.join(self.directory, 'results.js')
        with open(report_path, 'w+') as f:
            f.write(templating.render_template(
                'report.js.template',
                DATA=json.dumps({
                    'data': data,
                    'settings': self.settings.fetch(None),
                    'body': '\n'.join(body)
                })
            ))

        for filename, contents in files.items():
            file_path = os.path.join(self.directory, filename)
            with open(file_path, 'w+') as f:
                f.write(contents)

        return self.url


def load_project_settings(path: str) -> dict:
    """

    :param path:
    :return:
    """

    path = environ.paths.clean(path)
    if os.path.isdir(path):
        path = os.path.join(path, 'cauldron.json')
    if not os.path.exists(path):
        raise FileNotFoundError(
            'No project file found at: {}'.format(path)
        )
    with open(path, 'r+') as f:
        out = json.load(f)

    project_folder = os.path.split(os.path.dirname(path))[-1]
    if 'id' not in out or not out['id']:
        out['id'] = project_folder

    return out
