import asyncio
import threading
import uuid
from datetime import datetime


class ThreadAbortError(Exception):
    """
    A custom exception type that can be used to interrupt running threads and
    be handled differently than other types of exceptions. The assumption
    when handling this type of exception is that the user intentionally aborted
    the running of the step and so an error display should not be presented.
    """

    pass


class CauldronThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        """Create a new Cauldron Thread"""

        super(CauldronThread, self).__init__(*args, **kwargs)

        self.abort = False
        self.context = None
        self.daemon = True
        self.uid = str(uuid.uuid4())
        self.command = None
        self.parser = None
        self.kwargs = None
        self.result = None
        self.response = None
        self.is_executing = False
        self.exception = None
        self.logs = []
        self._loop = None
        self.completed_at = None  # datetime
        self._has_started = False

    @property
    def is_running(self) -> bool:
        """Specifies whether or not the thread is running"""
        return (
            self._has_started and
            self.is_alive() or
            self.completed_at is None or
            (datetime.utcnow() - self.completed_at).total_seconds() < 0.5
        )

    def run(self):
        """
        Executes the Cauldron command in a thread to prevent long-running
        computations from locking the main Cauldron thread, which is needed
        to serve and print status information.
        """

        async def run_command():
            try:
                self.result = self.command(
                    context=self.context,
                    **self.kwargs
                )
            except Exception as error:
                self.exception = error
                print(error)
                import traceback
                traceback.print_exc()
                import sys
                self.context.response.fail(
                    code='COMMAND_EXECUTION_ERROR',
                    message='Failed to execute command due to internal error',
                    error=error
                ).console(
                    whitespace=1
                )

        self._has_started = True
        self._loop = asyncio.new_event_loop()
        self._loop.run_until_complete(run_command())
        self._loop.close()
        self._loop = None
        self.completed_at = datetime.utcnow()

    def abort_running(self) -> bool:
        """
        Executes a hard abort by shutting down the event loop in this thread
        in which the running command was operating. This is carried out using
        the asyncio library to prevent the stopped execution from destabilizing
        the Python environment.
        """

        if not self._loop:
            return False

        try:
            self._loop.stop()
            return True
        except Exception:
            return False
        finally:
            self.completed_at = datetime.utcnow()


def abort_thread():
    """
    This function checks to see if the user has indicated that they want the
    currently running execution to stop prematurely by marking the running
    thread as aborted. It only applies to operations that are run within
    CauldronThreads and not the main thread.
    """

    thread = threading.current_thread()

    if not isinstance(thread, CauldronThread):
        return

    if thread.is_executing and thread.abort:
        raise ThreadAbortError('User Aborted Execution')
