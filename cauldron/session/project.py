import json
import os
import sys
import time
import typing

from cauldron import environ
from cauldron import render
from cauldron import templating
from cauldron.reporting.report import Report
from cauldron.session.caching import SharedCache


class ExposedProject(object):
    """
    A simplified form of the project for exposure to the Cauldron users.
    """

    def __init__(self):
        self._project = None

    @property
    def internal_project(self) -> 'Project':
        return self._project

    @property
    def display(self) -> Report:
        if not self._project or not self._project.current_step:
            return None
        return self._project.current_step.report

    @property
    def shared(self) -> SharedCache:
        if not self._project:
            return None
        return self._project.shared

    @property
    def settings(self) -> SharedCache:
        return self._project.settings

    def load(self, project: typing.Union['Project', None]):
        self._project = project


class ProjectStep(object):
    """
    A computational step within the project, which contains data and
    functionality related specifically to that step as well as a reference to
    the project itself.
    """

    def __init__(
            self,
            project: 'Project' = None,
            report: Report = None
    ):
        self.project = project
        self.report = report
        self.last_modified = None
        self.code = None

    @property
    def id(self) -> str:
        if not self.report:
            return None
        return self.report.id

    @property
    def index(self) -> int:
        if not self.project:
            return -1
        return self.project.steps.index(self)

    @property
    def source_path(self) -> str:
        if not self.project or not self.report:
            return None
        return os.path.join(self.project.source_directory, self.id)

    def is_dirty(self):
        """

        :return:
        """
        if self.last_modified is None:
            return True
        p = self.source_path
        if not p:
            return False
        return os.path.getmtime(p) >= self.last_modified


class Project(object):

    def __init__(
            self,
            source_directory: str,
            results_path: str = None,
            identifier: str = None,
            shared: typing.Union[dict, SharedCache] = None
    ):
        """
        :param source_directory:
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

        source_directory = environ.paths.clean(source_directory)
        if os.path.isfile(source_directory):
            source_directory = os.path.dirname(source_directory)
        self.source_directory = source_directory

        self.steps = []
        self._results_path = results_path
        self._current_step = None
        self.last_modified = None

        def as_shared_cache(source):
            if source is None:
                return SharedCache()
            if not hasattr(source, 'fetch'):
                return SharedCache().put(**source)
            return source

        self.shared = as_shared_cache(shared)
        self.settings = SharedCache()
        self.refresh()

    @property
    def title(self) -> str:
        if self.settings:
            out = self.settings.fetch('title')
            if out:
                return out
            out = self.settings.fetch('name')
            if out:
                return out
            return self.id

        return 'unknown-project'

    @property
    def id(self) -> str:
        if self.settings:
            return self.settings.fetch('id', 'unknown')
        return 'unknown'

    @property
    def current_step(self) -> Report:
        if self._current_step:
            return self._current_step
        return self.steps[0]

    @current_step.setter
    def current_step(self, value: typing.Union[Report, None]):
        self._current_step = value

    @property
    def source_path(self) -> str:
        if not self.source_directory:
            return None
        return os.path.join(self.source_directory, 'cauldron.json')

    @property
    def results_path(self) -> str:
        if self._results_path:
            return self._results_path

        if self.settings and self.settings['path_results']:
            return self.settings['path_results']

        return environ.configs.make_path(
            'results',
            override_key='results_path'
        )

    @results_path.setter
    def results_path(self, value: str):
        self._results_path = environ.paths.clean(value)

    @property
    def url(self) -> str:
        """
        Returns the URL that will open this project results file in the browser
        :return:
        """

        if not self.results_path:
            return None

        return 'file://{path}?id={id}'.format(
            path=os.path.join(self.results_path, 'project.html'),
            id=self.id
        )

    @property
    def output_directory(self) -> str:
        """
        Returns the directory where the project results files will be written
        :return:
        """

        if not self.results_path:
            return None

        return os.path.join(self.results_path, 'reports', self.id, 'latest')

    @property
    def output_path(self) -> str:
        """
        Returns the full path to where the results.js file will be written
        :return:
        """

        if not self.results_path:
            return None

        return os.path.join(self.output_directory, 'results.js')

    def snapshot_path(self, *args: typing.Tuple[str]) -> str:
        """

        :param args:
        :return:
        """

        if not self.results_path:
            return None

        return os.path.join(self.output_directory, '..', 'snapshots', *args)

    def snapshot_url(self, snapshot_name: str) -> str:
        """

        :param snapshot_name:
        :return:
        """

        return '{}&sid={}'.format(self.url, snapshot_name)

    def refresh(self) -> bool:
        """
        Loads the cauldron.json configuration file for the project and populates
        the project with the loaded data. Any existing data will be overwritten,
        including previously stored ProjectSteps.

        If the project has already loaded with the most recent version of the
        cauldron.json file, this method will return without making any changes
        to the project.

        :return:
            Whether or not a refresh was needed and carried out
        """

        lm = self.last_modified
        if lm is not None and lm >= os.path.getmtime(self.source_path):
            return False

        self.settings.clear().put(
            **load_project_settings(self.source_directory)
        )

        path = self.settings.fetch('results_path')
        if path:
            self.results_path = environ.paths.clean(
                os.path.join(self.source_directory, path)
            )

        python_paths = self.settings.fetch('python_paths', [])
        if isinstance(python_paths, str):
            python_paths = [python_paths]
        for path in python_paths:
            path = environ.paths.clean(
                os.path.join(self.source_directory, path)
            )
            if path not in sys.path:
                sys.path.append(path)

        self.steps = []
        steps_folder = self.settings.fetch('steps_folder')
        for step_data in self.settings.steps:
            if isinstance(step_data, str):
                step_data = dict(name=step_data)
            step_path = step_data.get('name')

            if step_path is None:
                environ.log(
                    """
                    [ERROR]: No name was found for the step:
                        {}
                    """.format(step_data)
                )
                self.last_modified = 0
                return True

            if steps_folder:
                step_path = os.path.join(steps_folder, step_path)
            self.steps.append(ProjectStep(
                report=Report(step_path, project=self, **step_data),
                project=self
            ))

        self.last_modified = time.time()
        return True

    def write(self) -> str:
        """

        :return:
        """

        environ.systems.remove(self.output_directory)
        os.makedirs(self.output_directory)

        body = []
        data = {}
        files = {}
        for step in self.steps:
            report = step.report
            code = render.code(step.code, filename=step.id) if step.code else ''
            body.append(templating.render_template(
                'step-body.html',
                code=code,
                body=''.join(report.body),
                id=report.id,
                title=report.title,
                summary=report.summary
            ))
            data.update(report.data.fetch(None))
            files.update(report.files.fetch(None))

        with open(self.output_path, 'w+') as f:
            f.write(templating.render_template(
                'report.js.template',
                DATA=json.dumps({
                    'data': data,
                    'settings': self.settings.fetch(None),
                    'body': '\n'.join(body)
                })
            ))

        for filename, contents in files.items():
            file_path = os.path.join(self.output_directory, filename)
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
