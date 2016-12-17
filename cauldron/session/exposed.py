import os
import typing

from cauldron.session import projects
from cauldron.session.caching import SharedCache
from cauldron.session import report
from cauldron import environ
from cauldron.runner.python_file import UserAbortError
from cauldron.cli import threads


class ExposedProject(object):
    """
    A simplified form of the project for exposure to Cauldron users. A
    single exposed project is created when the Cauldron library is first
    imported and that exposed project is accessible from the cauldron
    root module.
    """

    def __init__(self):
        self._project = None  # type: projects.Project

    @property
    def internal_project(self) -> projects.Project:
        """

        :return:
        """

        return self._project

    @property
    def display(self) -> typing.Union[None, report.Report]:
        """

        :return:
        """

        if not self._project or not self._project.current_step:
            return None
        return self._project.current_step.report

    @property
    def shared(self) -> typing.Union[None, SharedCache]:
        """

        :return:
        """

        if not self._project:
            return None
        return self._project.shared

    @property
    def settings(self) -> typing.Union[None, SharedCache]:
        """

        :return:
        """

        if not self._project:
            return None
        return self._project.settings

    @property
    def title(self) -> typing.Union[None, str]:
        """

        :return:
        """

        if not self._project:
            return None
        return self._project.title

    @title.setter
    def title(self, value: typing.Union[None, str]):
        """

        :param value:
        :return:
        """

        if not self._project:
            raise RuntimeError('Failed to assign title to an unloaded project')
        self._project.title = value

    def load(self, project: typing.Union[projects.Project, None]):
        """

        :param project:
        :return:
        """

        self._project = project

    def unload(self):
        """

        :return:
        """

        self._project = None

    def path(self, *args: typing.List[str]) -> typing.Union[None, str]:
        """
        Creates an absolute path in the project source directory from the
        relative path components.

        :param args:
            Relative components for creating a path within the project source
            directory
        :return:
            An absolute path to the specified file or directory within the
            project source directory.
        """

        if not self._project:
            return None

        return environ.paths.clean(os.path.join(
            self._project.source_directory,
            *args
        ))


class ExposedStep(object):
    """

    """

    @property
    def _step(self):
        """
        Internal access to the source step. Should not be used outside
        of Cauldron development.

        :return:
        """

        import cauldron
        try:
            return cauldron.project.internal_project.current_step
        except Exception:
            return None

    def stop(self):
        """
        Stops the execution of the current step immediately without raising
        an error. Use this to abort the step running process if you want
        to return early.
        """

        step = self._step
        if step:
            raise UserAbortError()

    def breathe(self):
        """
        Checks the current execution state for the running step and responds
        to any changes in that state. Particular useful for checking to see
        if a step has been aborted by the user during long-running executions.
        """

        if self._step:
            threads.abort_thread()
