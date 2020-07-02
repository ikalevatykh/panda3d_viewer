"""This module contains a viewer application process proxy."""

import multiprocessing as mp

from .viewer_errors import ViewerClosedError

__all__ = ('ViewerAppProxy')


class ViewerAppProxy(mp.Process):
    """A viewer application process proxy.

    Run a viewer application in a separate process to
    use it in an asynchronous way.
    """

    def __init__(self, *args, **kwargs):
        """Start an application in a sub-process."""
        mp.Process.__init__(self)
        self._args = args
        self._kwargs = kwargs
        self._host_conn, self._proc_conn = mp.Pipe()
        self.daemon = True
        self.start()
        reply = self._host_conn.recv()
        if isinstance(reply, Exception):
            raise reply

    def __getattr__(self, name):
        """Redirect method calls to the sub-process.

        Arguments:
            name {str} -- attribute name

        Returns:
            callable -- an application method wrapper
        """
        def _send(*args, **kwargs):
            self._host_conn.send((name, args, kwargs))
            reply = self._host_conn.recv()
            if isinstance(reply, Exception):
                raise reply
            return reply

        return _send

    def run(self):
        """Run the application in a sub-process."""
        try:
            # import here to prevent Panda3D from loading in the host process
            from .viewer_app import ViewerApp

            app = ViewerApp(*self._args, **self._kwargs)
            self._proc_conn.send(None)

            def _execute(task):
                for _ in range(100):
                    if not self._proc_conn.poll(0.001):
                        break
                    name, args, kwargs = self._proc_conn.recv()
                    if name == 'step':
                        self._proc_conn.send(None)
                        break  # let the manager to execute other tasks
                    try:
                        reply = getattr(app, name)(*args, **kwargs)
                        self._proc_conn.send(reply)
                    except Exception as error:
                        self._proc_conn.send(error)
                return task.cont

            app.task_mgr.add(_execute, "Communication task", -50)
            app.run()
        except Exception as error:
            self._proc_conn.send(error)
        else:
            self._proc_conn.send(ViewerClosedError(
                'User closed the main window'))
        # read the rest to prevent the host process from being blocked
        if self._proc_conn.poll(0.05):
            self._proc_conn.recv()
