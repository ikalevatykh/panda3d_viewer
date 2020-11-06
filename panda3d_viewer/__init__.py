"""This package contains Viewer, a simpe and efficient cross-platform Panda3D based 3D viewer."""

from .viewer import Viewer
from .viewer_config import ViewerConfig
from .viewer_errors import ViewerClosedError, ViewerError

__all__ = ('Viewer', 'ViewerConfig', 'ViewerError', 'ViewerClosedError')

__version__ = '0.3.1'
