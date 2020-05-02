"""
This package contains Viewer, a simpe and efficient
cross-platform 3D viewer based on Panda3D.
"""

__version__ = '0.2.0'

from .viewer import Viewer
from .viewer_config import ViewerConfig
from .viewer_errors import ViewerError, ViewerClosedError


__all__ = ('Viewer', 'ViewerConfig', 'ViewerError', 'ViewerClosedError')
