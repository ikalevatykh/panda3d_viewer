"""This module contains a viewer application process proxy."""

import multiprocessing as mp
import threading as th

from .viewer_errors import ViewerClosedError, ViewerError

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
        self._host_queue = mp.Queue()
        self._proc_queue = mp.Queue()

        self.start()
        try:
            reply = self._proc_queue.get(timeout=2.0)
            if isinstance(reply, Exception):
                raise reply
        except mp.queues.Empty:
            raise ViewerError('Cannot start the viewer')

    def __getattr__(self, name):
        """Redirect method calls to the sub-process.

        Arguments:
            name {str} -- attribute name

        Returns:
            callable -- an application method wrapper
        """
        def _send(*args, **kwargs):
            self._host_queue.put((name, args, kwargs))
            reply = self._proc_queue.get(block=True, timeout=2.0)
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
            self._proc_queue.put(None)
            running = True

            def _exec():
                while running:
                    try:
                        name, args, kwargs = self._host_queue.get(timeout=0.1)
                        reply = getattr(app, name)(*args, **kwargs)
                        self._proc_queue.put(reply)
                    except mp.queues.Empty:
                        continue
                    except Exception as error:
                        self._proc_queue.put(error)

            executor = th.Thread(target=_exec)
            executor.start()
            app.run()

            running = False
            executor.join()
            raise ViewerClosedError('User closed the main window')
        except Exception as error:
            self._proc_queue.put(error)
