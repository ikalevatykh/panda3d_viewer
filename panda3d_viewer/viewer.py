"""This module contains Viewer, a simpe and efficient cross-platform 3D viewer."""

from .viewer_config import ViewerConfig
from .viewer_errors import ViewerError


__all__ = ('Viewer')


class Viewer:
    """A Panda3D based viewer."""

    def __init__(self, window_title=None, window_type='onscreen', config=None):
        """Open a window, setup a scene.

        Keyword Arguments:
            window_title {str} -- window title (default: {'Viewer'})
            window_type {str} -- window type, one of onscreen, offscreen (default: {'onscreen'})
            config {ViewerConfig} -- viewer configuration (default: {None})
        """
        if config is None:
            config = ViewerConfig()
        if window_title is not None:
            config.set_window_title(window_title)

        config.set_value('window-type', window_type)
        self._window_type = window_type

        if window_type == 'onscreen':
            # run application asynchronously in a sub-process
            from .viewer_proxy import ViewerAppProxy
            self._app = ViewerAppProxy(config)
        elif window_type == 'offscreen':
            # start application in the main process
            from .viewer_app import ViewerApp
            self._app = ViewerApp(config)
        else:
            raise ViewerError('Unknown window type: {}'.format(window_type))

    def join(self):
        """Run the application until the user close the main window."""
        if self._window_type == 'onscreen':
            self._app.join()

    def stop(self):
        """Stop the application."""
        self._app.stop()

    def append_group(self, root_path, remove_if_exists=True):
        """Append a root node for a group of nodes.

        Arguments:
            root_path {str} -- path to the group's root node

        Keyword Arguments:
            remove_if_exists {bool} -- remove group with root_path if exists (default: {True})
        """
        self._app.append_group(root_path, remove_if_exists)

    def remove_group(self, root_path):
        """Remove a group of nodes.

        Arguments:
            root_path {str} -- path to the group's root node
        """
        self._app.remove_group(root_path)

    def show_group(self, root_path, show):
        """Turn a node group rendering on or off.

        Arguments:
            root_path {str} -- path to the group's root node
            show {bool} -- flag
        """
        self._app.show_group(root_path, show)

    def move_nodes(self, root_path, name_pose_dict):
        """Set a pose for nodes within a group.

        Arguments:
            root_path {str} -- path to the group's root node
            name_pose_dict {dict} -- {node_name : (pos, quat)} dictionary
        """
        self._app.move_nodes(root_path, name_pose_dict)

    def append_mesh(self, root_path, name, mesh_path, scale):
        """Append a mesh node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            mesh_path {str} -- path to the mesh file on disk
            scale {Vec3} -- mesh scale
        """
        self._app.append_mesh(root_path, name, mesh_path, scale)

    def append_capsule(self, root_path, name, radius, length):
        """Append a capsule primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            radius {flaot} -- capsule radius
            length {flaot} -- capsule length
        """
        self._app.append_capsule(root_path, name, radius, length)

    def append_cylinder(self, root_path, name, radius, length):
        """Append a cylinder primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            radius {flaot} -- cylinder radius
            length {flaot} -- cylinder length
        """
        self._app.append_cylinder(root_path, name, radius, length)

    def append_box(self, root_path, name, size):
        """Append a box primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            size {Vec3} -- box size
        """
        self._app.append_box(root_path, name, size)

    def append_plane(self, root_path, name, size):
        """Append a plane primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            size {Vec2} -- plane x,y size
        """
        self._app.append_plane(root_path, name, size)

    def append_sphere(self, root_path, name, radius):
        """Append a sphere primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            radius {flaot} -- sphere radius
        """
        self._app.append_sphere(root_path, name, radius)

    def set_material(self, root_path, name, color_rgba, texture_path=''):
        """Override material of a node.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            color {Vec4} -- color RGBA

        Keyword Arguments:
            texture_path {str} -- path to the texture file on disk (default: {''})
        """
        self._app.set_material(root_path, name, color_rgba, texture_path)

    def reset_camera(self, pos, look_at):
        """Reset camera position.

        Arguments:
            pos {Vec3} -- camera position
            look_at {Vec3} -- camera target point
        """
        self._app.reset_camera(pos, look_at)

    def enable_lights(self, enable):
        """Turn lighting on or off.

        Arguments:
            enable {bool} -- flag
        """
        self._app.enable_lights(enable)

    def enable_light(self, index, enable):
        """Turn a light on or off.

        Arguments:
            index {int} -- light index
            enable {bool} -- flag
        """
        self._app.enable_light(index, enable)

    def enable_shadow(self, enable):
        """Turn shadows rendering on or off.

        Arguments:
            enable {bool} -- flag
        """
        self._app.enable_shadow(enable)

    def enable_hdr(self, enable):
        """Turn HDR effect on or off.

        Arguments:
            enable {bool} -- flag
        """
        self._app.enable_hdr(enable)

    def enable_fog(self, enable):
        """Turn fog rendering on or off.

        Arguments:
            enable {bool} -- flag
        """
        self._app.enable_fog(enable)

    def show_axes(self, show):
        """Turn the axes rendering on or off.

        Arguments:
            show {bool} -- flag
        """
        self._app.show_axes(show)

    def show_grid(self, show):
        """Turn the grid rendering on or off.

        Arguments:
            show {bool} -- flag
        """
        self._app.show_grid(show)

    def show_floor(self, show):
        """Turn the floor rendering on or off.

        Arguments:
            show {bool} -- flag
        """
        self._app.show_floor(show)

    def set_background_color(self, color_rgb):
        """Set the window background color.

        Arguments:
            color_rgb {tuple} -- RGB color value
        """
        self._app.set_background_color(color_rgb)

    def save_screenshot(self, filename=None):
        """Capture a screenshot from the main window and write image to disk.

        Keyword Arguments:
            filename {str} -- filename (including extension) to save image (default: {auto})

        Returns:
            bool -- success flag
        """
        self._app.step()  # render
        return self._app.save_screenshot(filename)

    def get_screenshot(self, requested_format='BGRA'):
        """Capture and return a screenshot from offscreen buffer.

        Keyword Arguments:
            requested_format {str} -- image channels, e.g. RGB, BGR (default: {'BGRA'})

        Returns:
            ndarray -- image as uint8 numpy array (height, width, num_channels)
        """
        self._app.step()  # render
        return self._app.get_screenshot(requested_format)
