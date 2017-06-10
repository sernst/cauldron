import asyncio
import threading
import uuid


class ThreadAbortError(Exception):
    pass


class CauldronThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        """ """

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

    def run(self):
        """ """

        async def run_command():
            try:
                self.result = self.command(
                    context=self.context,
                    **self.kwargs
                )
            except Exception as error:
                self.exception = error
                print(error)
                self.context.response.fail(
                    code='COMMAND_EXECUTION_ERROR',
                    message='Failed to execute command due to internal error',
                    error=error
                ).console(
                    whitespace=1
                )
            # self._loop.stop()

        self._loop = asyncio.new_event_loop()
        # self._loop.call_soon(run_command)
        # self._loop.run_forever()
        self._loop.run_until_complete(run_command())
        self._loop.close()
        self._loop = None

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


def abort_thread():
    """
    This function checks to see if the user has indicated that they want the
    currently running execution to stop prematurely by marking the running
    thread as aborted. It only applies to operations that are run within
    CauldronThreads and not the main thread.

    :return:
    """

    thread = threading.current_thread()

    if not isinstance(thread, CauldronThread):
        return

    if thread.is_executing and thread.abort:
        raise ThreadAbortError('User Aborted Execution')
