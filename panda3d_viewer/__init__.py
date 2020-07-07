"""
This package contains Viewer, a simpe and efficient cross-platform 3D viewer
based on Panda3D.
"""

from .viewer import Viewer
from .viewer_config import ViewerConfig
from .viewer_errors import ViewerClosedError, ViewerError

__all__ = ('Viewer', 'ViewerConfig', 'ViewerError', 'ViewerClosedError')

__version__ = '0.3.0'
