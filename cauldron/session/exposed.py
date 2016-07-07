import typing

from cauldron.session import projects
from cauldron.session.caching import SharedCache
from cauldron.session import report


class ExposedProject(object):
    """
    A simplified form of the project for exposure to Cauldron users. A
    single exposed project is created when the Cauldron library is first
    imported and that exposed project is accessible from the cauldron
    root module.
    """

    def __init__(self):
        self._project = None

    @property
    def internal_project(self) -> projects.Project:
        """

        :return:
        """

        return self._project

    @property
    def display(self) -> report.Report:
        """

        :return:
        """

        if not self._project or not self._project.current_step:
            return None
        return self._project.current_step.report

    @property
    def shared(self) -> SharedCache:
        """

        :return:
        """

        if not self._project:
            return None
        return self._project.shared

    @property
    def settings(self) -> SharedCache:
        """

        :return:
        """

        if not self._project:
            return None
        return self._project.settings

    @property
    def title(self) -> str:
        """

        :return:
        """

        if not self._project:
            return None
        return self._project.title

    @title.setter
    def title(self, value: str):
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


