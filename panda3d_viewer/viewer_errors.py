"""This module contains viewer exceptions."""

__all__ = ('ViewerError', 'ViewerClosedError')


class ViewerError(Exception):
    """Base class for all viewer exceptions."""


class ViewerClosedError(ViewerError):
    """Raised when a method is called in a closed viewer."""
