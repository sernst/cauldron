import functools
import hashlib
import json
import os
import time
import typing
from collections import namedtuple

from cauldron import environ
from cauldron.session import definitions as file_definitions
from cauldron.session import writing
from cauldron.session.caching import SharedCache
from cauldron.session.projects import definitions
from cauldron.session.projects import steps
from cauldron.session.report import Report

DEFAULT_SCHEME = 'S{{##}}-{{name}}.{{ext}}'

StopCondition = namedtuple('StopCondition', ['aborted', 'halt'])


class Project:
    """ """

    def __init__(
            self,
            source_directory: str,
            results_path: str = None,
            shared: typing.Union[dict, SharedCache] = None
    ):
        """
        :param source_directory:
        :param results_path:
            [optional] The path where the results files for the project will
            be saved. If omitted, the default global results path will be
            used.
        :param shared:
            [optional] The shared data cache used to store project data when
            run
        """

        source_directory = environ.paths.clean(source_directory)
        if os.path.isfile(source_directory):
            source_directory = os.path.dirname(source_directory)
        self.source_directory = source_directory

        self.steps = []  # type: typing.List[steps.ProjectStep]
        self._results_path = results_path  # type: str
        self._current_step = None  # type: steps.ProjectStep
        self.last_modified = None
        self.remote_source_directory = None  # type: str

        def as_shared_cache(source):
            if source and not hasattr(source, 'fetch'):
                return SharedCache().put(**source)
            return source or SharedCache()

        self.stop_condition = StopCondition(False, False)  # type: StopCondition
        self.shared = as_shared_cache(shared)
        self.settings = SharedCache()
        self.refresh()

    @property
    def uuid(self) -> str:
        """
        The unique identifier for the project among all other projects, which
        is based on a hashing of the project's source path to prevent naming
        collisions when storing project information from multiple projects in
        the same directory (e.g. common results directory).
        """

        return hashlib.sha1(self.source_path.encode()).hexdigest()

    @property
    def is_remote_project(self) -> bool:
        """Whether or not this project is remote"""
        project_path = environ.paths.clean(self.source_directory)
        return project_path.find('cd-remote-project') != -1

    @property
    def library_directories(self) -> typing.List[str]:
        """
        The list of directories to all of the library locations
        """
        def listify(value):
            return [value] if isinstance(value, str) else list(value)

        # If this is a project running remotely remove external library
        # folders as the remote shared libraries folder will contain all
        # of the necessary dependencies
        is_local_project = not self.is_remote_project
        folders = [
            f
            for f in listify(self.settings.fetch('library_folders', ['libs']))
            if is_local_project or not f.startswith('..')
        ]

        # Include the remote shared library folder as well
        folders.append('../__cauldron_shared_libs')

        # Include the project directory as well
        folders.append(self.source_directory)

        return [
            environ.paths.clean(os.path.join(self.source_directory, folder))
            for folder in folders
        ]

    @property
    def asset_directories(self):
        """ """

        def listify(value):
            return [value] if isinstance(value, str) else list(value)
        folders = listify(self.settings.fetch('asset_folders', ['assets']))

        return [
            environ.paths.clean(os.path.join(self.source_directory, folder))
            for folder in folders
        ]

    @property
    def has_error(self):
        """ """

        for s in self.steps:
            if s.error:
                return True
        return False

    @property
    def title(self) -> str:
        out = self.settings.fetch('title')
        if out:
            return out
        out = self.settings.fetch('name')
        if out:
            return out
        return self.id

    @title.setter
    def title(self, value: str):
        self.settings.title = value

    @property
    def id(self) -> str:
        return self.settings.fetch('id', 'unknown')

    @property
    def naming_scheme(self) -> str:
        return self.settings.fetch('naming_scheme', None)

    @naming_scheme.setter
    def naming_scheme(self, value: typing.Union[str, None]):
        self.settings.put(naming_scheme=value)

    @property
    def current_step(self) -> typing.Union['steps.ProjectStep', None]:
        if len(self.steps) < 1:
            return None

        step = self._current_step
        return step if step else self.steps[0]

    @current_step.setter
    def current_step(self, value: typing.Union[Report, None]):
        self._current_step = value

    @property
    def source_path(self) -> typing.Union[None, str]:
        directory = self.source_directory
        return os.path.join(directory, 'cauldron.json') if directory else None

    @property
    def results_path(self) -> str:
        """The path where the project results will be written"""

        def possible_paths():
            yield self._results_path
            yield self.settings.fetch('path_results')
            yield environ.configs.fetch('results_directory')
            yield environ.paths.results(self.uuid)

        return next(p for p in possible_paths() if p is not None)

    @results_path.setter
    def results_path(self, value: str):
        self._results_path = environ.paths.clean(value)

    @property
    def url(self) -> str:
        """
        Returns the URL that will open this project results file in the browser
        :return:
        """

        return 'file://{path}?id={id}'.format(
            path=os.path.join(self.results_path, 'project.html'),
            id=self.uuid
        )

    @property
    def baked_url(self) -> str:
        """
        Returns the URL that will open this project results file in the browser
        with the loading information baked into the file so that no URL
        parameters are needed to view it, which is needed on platforms like
        windows
        """

        return 'file://{path}'.format(
            path=os.path.join(self.results_path, 'display.html'),
            id=self.uuid
        )

    @property
    def output_directory(self) -> str:
        """
        Returns the directory where the project results files will be written
        """

        return os.path.join(self.results_path, 'reports', self.uuid, 'latest')

    @property
    def output_path(self) -> str:
        """
        Returns the full path to where the results.js file will be written
        :return:
        """

        return os.path.join(self.output_directory, 'results.js')

    def make_remote_url(self, host: str = None):
        """

        :param host:
        """

        if host:
            host = host.rstrip('/')
        else:
            host = ''

        return '{}/view/project.html?id={}'.format(host, self.uuid)

    def kernel_serialize(self):
        """ """

        return dict(
            uuid=self.uuid,
            stop_condition=self.stop_condition._asdict(),
            serial_time=time.time(),
            last_modified=self.last_modified,
            remote_source_directory=self.remote_source_directory,
            source_directory=self.source_directory,
            source_path=self.source_path,
            output_directory=self.output_directory,
            output_path=self.output_path,
            url=self.url,
            remote_slug=self.make_remote_url(),
            title=self.title,
            id=self.id,
            steps=[s.kernel_serialize() for s in self.steps],
            naming_scheme=self.naming_scheme
        )

    def refresh(self, force: bool = False) -> bool:
        """
        Loads the cauldron.json definition file for the project and populates
        the project with the loaded data. Any existing data will be overwritten,
        if the new definition file differs from the previous one.

        If the project has already loaded with the most recent version of the
        cauldron.json file, this method will return without making any changes
        to the project.

        :param force:
            If true the project will be refreshed even if the project file
            modified timestamp doesn't indicate that it needs to be refreshed.
        :return:
            Whether or not a refresh was needed and carried out
        """

        lm = self.last_modified
        is_newer = lm is not None and lm >= os.path.getmtime(self.source_path)
        if not force and is_newer:
            return False

        old_definition = self.settings.fetch(None)
        new_definition = definitions.load_project_definition(
            self.source_directory
        )

        if not force and old_definition == new_definition:
            return False

        self.settings.clear().put(**new_definition)

        old_step_definitions = old_definition.get('steps', [])
        new_step_definitions = new_definition.get('steps', [])

        if not force and old_step_definitions == new_step_definitions:
            return True

        old_steps = self.steps
        self.steps = []

        for step_data in new_step_definitions:
            matches = [s for s in old_step_definitions if s == step_data]
            if len(matches) > 0:
                index = old_step_definitions.index(matches[0])
                self.steps.append(old_steps[index])
            else:
                self.add_step(step_data)

        self.last_modified = time.time()
        return True

    def get_step(self, name: str) -> typing.Union['steps.ProjectStep', None]:
        """

        :param name:
        :return:
        """

        for s in self.steps:
            if s.definition.name == name:
                return s

        return None

    def get_step_by_reference_id(
            self,
            reference_id: str
    ) -> typing.Union['steps.ProjectStep', None]:
        """

        :param reference_id:
        :return:
        """

        for s in self.steps:
            if s.reference_id == reference_id:
                return s

        return None

    def index_of_step(self, name) -> typing.Union[int, None]:
        """

        :param name:
        :return:
        """

        name = name.strip('"')

        for index, s in enumerate(self.steps):
            if s.definition.name == name:
                return int(index)

        return None

    def add_step(
            self,
            step_data: typing.Union[str, dict],
            index: int = None
    ) -> typing.Union['steps.ProjectStep', None]:
        """

        :param step_data:
        :param index:
        :return:
        """

        fd = file_definitions.FileDefinition(
            data=step_data,
            project=self,
            project_folder=functools.partial(
                self.settings.fetch,
                'steps_folder'
            )
        )

        if not fd.name:
            self.last_modified = 0
            return None

        ps = steps.ProjectStep(self, fd)

        if index is None:
            self.steps.append(ps)
        else:
            if index < 0:
                index %= len(self.steps)
            self.steps.insert(index, ps)

            if fd.name.endswith('.py'):
                for i in range(self.steps.index(ps) + 1, len(self.steps)):
                    self.steps[i].mark_dirty(True)

        self.last_modified = time.time()
        return ps

    def remove_step(self, name) -> typing.Union['steps.ProjectStep', None]:
        """

        :param name:
        :return:
        """

        step = None

        for ps in self.steps:
            if ps.definition.name == name:
                step = ps
                break

        if step is None:
            return None

        if step.definition.name.endswith('.py'):
            for i in range(self.steps.index(step) + 1, len(self.steps)):
                self.steps[i].mark_dirty(True)

        self.steps.remove(step)
        return step

    def save(self, path: str = None):
        """

        :param path:
        :return:
        """

        if not path:
            path = self.source_path

        self.settings.put(
            steps=[ps.definition.serialize() for ps in self.steps]
        )

        data = self.settings.fetch(None)
        with open(path, 'w+') as f:
            json.dump(data, f, indent=2, sort_keys=True)

        self.last_modified = time.time()

    def write(self) -> str:
        """ """

        writing.save(self)
        return self.url

    def status(self) -> dict:

        return dict(
            id=self.id,
            steps=[s.status() for s in self.steps],
            stop_condition=self.stop_condition._asdict(),
            last_modified=self.last_modified,
            remote_slug=self.make_remote_url()
        )
