from collections.abc import Callable
from multiprocessing import Process


class ViewerAppProxy(Process):
    def __init__(self, *args: object, **kwargs: object) -> None: ...
    def __getattr__(self, name: str) -> Callable[..., object]: ...
    def run(self) -> None: ...

__all__ = ("ViewerAppProxy",)
