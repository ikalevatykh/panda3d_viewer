"""This module contains ViewerConfig - a viewer's configuration storage."""

__all__ = ('ViewerConfig')


class ViewerConfig:
    """Viewer configuration."""

    def __init__(self, **kwargs):
        """Construct an empty configuration and populate from @kwargs."""
        self._setings_map = {}

        # disable audio by default
        self.set_value('audio-active', False)
        self.set_value('audio-library-name', 'null')
        self.set_value('audio-music-active', False)
        self.set_value('audio-sfx-active', False)
        # hide debug/warning prints
        self.set_value('print-pipe-types', False)
        self.set_value('notify-level', 'error')

        if 'win_size' in kwargs:
            self.set_window_size(*kwargs.pop('win_size'))
        if 'antialiasing' in kwargs:
            self.enable_antialiasing(True, kwargs.pop('antialiasing'))
        for key, value in kwargs.items():
            self.set_value(key, value)

    def __str__(self):
        """Return settings as a plain text.

        Returns:
            str -- text representation
        """
        lines = ('{} {}'.format(key, value)
                 for key, value in self._setings_map.items())
        return '\n'.join(lines)

    def set_value(self, key, value):
        """Set common setting value.

        Arguments:
            key {str} -- setting name
            value {Any} -- setting value
        """
        key = key.replace('_', '-').lower()
        if isinstance(value, bool):
            value = 1 if value else 0
        self._setings_map[key] = str(value)

    def set_window_type(self, window_type):
        """Set window type.

        Arguments:
            window_type {str} -- one of onscreen, offscreen, none
        """
        self.set_value('window-type', window_type)

    def set_window_title(self, title):
        """Set window title.

        Arguments:
            title {str} -- title string
        """
        self.set_value('window-title', title)

    def set_window_size(self, width, height):
        """Set window size.

        Arguments:
            width {int} -- window width
            height {int} -- window height
        """
        self.set_value('win-size', '{} {}'.format(width, height))

    def set_window_fixed(self, fixed):
        """Disable window resizing.

        Arguments:
            fixed {bool} -- window fixed flag
        """
        self.set_value('win-fixed-size', fixed)

    def set_scene_scale(self, scale):
        """Set scene scale factor.

        Arguments:
            scale {float} -- scale factor for all geometries into the scene
        """
        self.set_value('scene-scale', scale)

    def enable_antialiasing(self, enable, multisamples):
        """Enable antialiasing.

        Arguments:
            enable {bool} -- flag
            multisamples {int} -- MSAA multisamples 2..16 (use 0 to disable)
        """
        self.set_value('framebuffer-multisample', enable)
        self.set_value('multisamples', multisamples)

    def enable_lights(self, enable):
        """Enable lightning.

        Arguments:
            enable {bool} -- flag
        """
        self.set_value('enable-lights', enable)

    def enable_spotlight(self, enable):
        """Use spotlights by default.

        Arguments:
            enable {bool} -- flag
        """
        self.set_value('enable-spotlight', enable)

    def enable_shadow(self, enable):
        """Enable shadows.

        Arguments:
            enable {bool} -- flag
        """
        self.set_value('enable-shadow', enable)

    def enable_hdr(self, enable):
        """Enable HDR effect.

        Arguments:
            enable {bool} -- flag
        """
        self.set_value('enable-hdr', enable)

    def enable_fog(self, enable):
        """Enable fog.

        Arguments:
            enable {bool} -- flag
        """
        self.set_value('enable-fog', enable)

    def show_axes(self, show):
        """Show axes.

        Arguments:
            show {bool} -- flag
        """
        self.set_value('show-axes', show)

    def show_grid(self, show):
        """Show grid.

        Arguments:
            show {bool} -- flag
        """
        self.set_value('show-grid', show)

    def show_floor(self, show):
        """Show floor plane.

        Arguments:
            show {bool} -- flag
        """
        self.set_value('show-floor', show)

    def set_model_cache(self, cache_dir, cache_textures=True):
        """Set model cache parameters.

        Arguments:
            cache_dir {str} -- path to the cache folder on disk
            cache_textures {bool} -- enable textures caching
        """
        self.set_value('model-cache-dir', cache_dir)
        self.set_value('model-cache-textures', cache_textures)
