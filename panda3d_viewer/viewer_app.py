"""This module contains ViewerApp, an application framework.

ViewerApp responsible for opening a graphical display,
setting up input devices and creating the scene graph.
"""

from datetime import datetime
import numpy as np

from panda3d.core import Vec3, Vec4, Quat, Mat4, BitMask32
from panda3d.core import GeomNode, TextNode
from panda3d.core import AmbientLight, DirectionalLight, Spotlight
from panda3d.core import Material
from panda3d.core import AntialiasAttrib, CullFaceAttrib, TransparencyAttrib, LightRampAttrib
from panda3d.core import PNMImage, Fog
from panda3d.core import loadPrcFileData

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText

from . import geometry

__all__ = ('ViewerApp')


class ViewerApp(ShowBase):
    """A Panda3D based application."""

    LightMask = BitMask32(1)

    def __init__(self, config):
        """Open a window, setup a scene.

        Arguments:
            config {ViewerConfig} -- viewer configuration
        """
        # disable audio by default
        config.set_value('audio-active', False)
        config.set_value('audio-library-name', 'null')
        config.set_value('audio-music-active', False)
        config.set_value('audio-sfx-active', False)
        # hide debug prints
        config.set_value('print-pipe-types', False)

        # load config before base init
        loadPrcFileData('', str(config))

        ShowBase.__init__(self)

        self.render.set_shader_auto()
        self.render.set_antialias(AntialiasAttrib.MAuto)

        self._camera_defaults = [(4.0, -4.0, 1.5), (0, 0, 0.5)]
        self.reset_camera(*self._camera_defaults)

        self._spotlight = self.config.GetBool('enable-spotlight', False)
        self._shadow_size = self.config.GetInt('shadow-buffer-size', 1024)
        self._lights = [
            self._make_light_ambient((0.2, 0.2, 0.2)),
            self._make_light_direct(
                1, (0.6, 0.8, 0.8), pos=(8.0, 8.0, 10.0)),
            self._make_light_direct(
                2, (0.8, 0.6, 0.8), pos=(8.0, -8.0, 10.0)),
            self._make_light_direct(
                3, (0.8, 0.8, 0.6), pos=(-8.0, 8.0, 10.0)),
            self._make_light_direct(
                4, (0.6, 0.6, 0.8), pos=(-8.0, -8.0, 10.0)),
        ]
        self._lights_mask = [True, True, True, False, False]
        self.enable_lights(self.config.GetBool('enable-lights', True))
        self.enable_shadow(self.config.GetBool('enable-shadow', False))
        self.enable_hdr(self.config.GetBool('enable-hdr', False))

        self._fog = self._make_fog()
        self.enable_fog(self.config.GetBool('enable-fog', False))

        self._axes = self._make_axes()
        self.show_axes(self.config.GetBool('show-axes', True))

        self._grid = self._make_grid()
        self.show_grid(self.config.GetBool('show-grid', True))

        self._floor = self._make_floor()
        self.show_floor(self.config.GetBool('show-floor', False))

        self._scene_root = self.render.attach_new_node('scene_root')
        self._groups = {}

        if self.windowType == 'onscreen':
            self._help_label = None
            self.trackball.node().set_forward_scale(
                self.config.GetFloat('trackball-scale', 0.01))
            self._setup_shortcuts()

    def step(self):
        """Execute one main loop step."""
        self.task_mgr.step()

    def join(self):
        """Run the application until the main window closes."""
        self.run()

    def stop(self):
        """Stop the application.

        Interrupts the application loop (run() function)
        """
        self.task_mgr.stop()

    def userExit(self):
        """User closed the main window."""
        self.stop()

    def append_group(self, root_path, remove_if_exists=True):
        """Append a root node for a group of nodes.

        Arguments:
            root_path {str} -- path to the group's root node

        Keyword Arguments:
            remove_if_exists {bool} -- remove group with root_path if exists (default: {True})
        """
        if remove_if_exists and root_path in self._groups:
            self.remove_group(root_path)

        root = self._scene_root
        for name in root_path.split('/'):
            root = root.attach_new_node(name)

        self._groups[root_path] = root

    def remove_group(self, root_path):
        """Remove a group of nodes.

        Arguments:
            root_path {str} -- path to the group's root node
        """
        self._groups.pop(root_path).removeNode()

    def show_group(self, root_path, show):
        """Turn a node group rendering on or off.

        Arguments:
            root_path {str} -- path to the group's root node
            show {bool} -- flag
        """
        root = self._groups[root_path]
        if show:
            root.show()
        else:
            root.hide()

    def move_nodes(self, root_path, name_pose_dict):
        """Set a pose for nodes within a group.

        Arguments:
            root_path {str} -- path to the group's root node
            name_pose_dict {dict} -- {node_name : (pos, quat)} dictionary
        """
        root = self._groups[root_path]
        for node in root.getChildren():
            if node.name in name_pose_dict:
                pos, quat = name_pose_dict[node.name]
                node.set_pos_quat(Vec3(*pos), Quat(*quat))

    def append_mesh(self, root_path, name, mesh_path, scale):
        """Append a mesh node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            mesh_path {str} -- path to the mesh file on disk
            scale {Vec3} -- mesh scale
        """
        root = self._groups[root_path]
        node = root.attach_new_node(name)
        node.set_scale(Vec3(*scale))
        if sum([s < 0 for s in scale]) % 2 != 0:
            # reverse the cull order in case of negative scale values
            node.set_attrib(CullFaceAttrib.make_reverse())
        mesh = self.loader.loadModel(mesh_path)
        mesh.reparent_to(node)
        if mesh_path.lower().endswith('.dae'):
            # converting from Y-up to Z-up axes when import from dae
            mesh.set_mat(Mat4.yToZUpMat())

    def append_capsule(self, root_path, name, radius, length):
        """Append a capsule primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            radius {flaot} -- capsule radius
            length {flaot} -- capsule length
        """
        geom = GeomNode(name)
        geom.add_geom(geometry.make_capsule(radius, length))
        root = self._groups[root_path]
        root.attach_new_node(geom)

    def append_cylinder(self, root_path, name, radius, length):
        """Append a cylinder primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            radius {flaot} -- cylinder radius
            length {flaot} -- cylinder length
        """
        geom = GeomNode(name)
        geom.add_geom(geometry.make_cylinder())
        root = self._groups[root_path]
        node = root.attach_new_node(geom)
        node.set_scale(Vec3(radius, radius, length))

    def append_box(self, root_path, name, size):
        """Append a box primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            size {Vec3} -- box size
        """
        geom = GeomNode(name)
        geom.add_geom(geometry.make_box())
        root = self._groups[root_path]
        node = root.attach_new_node(geom)
        node.set_scale(Vec3(*size))

    def append_plane(self, root_path, name, size):
        """Append a plane primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            size {Vec2} -- plane x,y size
        """
        geom = GeomNode(name)
        geom.add_geom(geometry.make_plane(size=size))
        root = self._groups[root_path]
        return root.attach_new_node(geom)

    def append_sphere(self, root_path, name, radius):
        """Append a sphere primitive node to the group.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            radius {flaot} -- sphere radius
        """
        geom = GeomNode(name)
        geom.add_geom(geometry.make_sphere())
        root = self._groups[root_path]
        node = root.attach_new_node(geom)
        node.set_scale(Vec3(radius, radius, radius))

    def set_material(self, root_path, name, color_rgba, texture_path=''):
        """Override material of a node.

        Arguments:
            root_path {str} -- path to the group's root node
            name {str} -- node name within a group
            color {Vec4} -- color RGBA

        Keyword Arguments:
            texture_path {str} -- path to the texture file on disk (default: {''})
        """
        node = self._groups[root_path].find(name)
        node.set_color(Vec4(*color_rgba))

        material = Material()
        material.set_ambient(Vec4(*color_rgba))
        material.set_diffuse(Vec4(*color_rgba))
        material.set_specular(Vec3(1, 1, 1))
        material.set_roughness(0.4)
        node.set_material(material, 1)

        if color_rgba[3] < 1:
            node.set_transparency(TransparencyAttrib.M_alpha)

        if texture_path:
            texture = self.loader.load_texture(texture_path)
            node.set_texture(texture)

    def reset_camera(self, pos, look_at):
        """Reset camera position.

        Arguments:
            pos {Vec3} -- camera position
            look_at {Vec3} -- camera target point
        """
        self.camera.set_pos(Vec3(*pos))
        self.camera.look_at(Vec3(*look_at))

        if self.windowType == 'onscreen':
            # update mouse control according to the camera position
            cam_mat = Mat4(self.camera.get_mat())
            cam_mat.invert_in_place()
            self.mouseInterfaceNode.set_mat(cam_mat)

    def enable_lights(self, enable):
        """Turn lighting on or off.

        Arguments:
            enable {bool} -- flag
        """
        for light, mask in zip(self._lights, self._lights_mask):
            if enable and mask:
                self.render.set_light(light)
            else:
                self.render.clear_light(light)
        self._lights_enabled = enable

    def enable_light(self, index, enable):
        """Turn a light on or off.

        Arguments:
            index {int} -- light index
            enable {bool} -- flag
        """
        self._lights_mask[index] = enable
        self.enable_lights(self._lights_enabled)

    def enable_shadow(self, enable):
        """Turn shadows rendering on or off.

        Arguments:
            enable {bool} -- flag
        """
        for light in self._lights:
            if not light.node().is_ambient_light():
                light.node().set_shadow_caster(enable)
        # self.render.set_depth_offset(1 if enable else 0)
        self._shadow_enabled = enable

    def enable_hdr(self, enable):
        """Turn HDR effect on or off.

        Arguments:
            enable {bool} -- flag
        """
        if enable:
            self.render.set_attrib(LightRampAttrib.makeHdr0())
        else:
            self.render.set_attrib(LightRampAttrib.makeDefault())
        self._hdr_enabled = enable

    def enable_fog(self, enable):
        """Turn fog rendering on or off.

        Arguments:
            enable {bool} -- flag
        """
        if enable:
            self.render.set_fog(self._fog)
        else:
            self.render.clear_fog()

    def show_axes(self, show):
        """Turn the axes rendering on or off.

        Arguments:
            show {bool} -- flag
        """
        if show:
            self._axes.show()
        else:
            self._axes.hide()

    def show_grid(self, show):
        """Turn the grid rendering on or off.

        Arguments:
            show {bool} -- flag
        """
        if show:
            self._grid.show()
        else:
            self._grid.hide()

    def show_floor(self, show):
        """Turn the floor rendering on or off.

        Arguments:
            show {bool} -- flag
        """
        if show:
            self._floor.show()
        else:
            self._floor.hide()

    def set_background_color(self, color_rgb):
        """Set the window background color.

        Arguments:
            color_rgb {tuple} -- RGB color value
        """
        self.win.set_clear_color(Vec3(*color_rgb))
        self._fog.set_color(Vec3(*color_rgb))

    def save_screenshot(self, filename=None):
        """Capture a screenshot from the main window and write image to disk.

        Keyword Arguments:
            filename {str} -- filename (including extension) to save image (default: {auto})

        Returns:
            bool -- success flag
        """
        if filename is None:
            template = 'screenshot-%Y-%m-%d-%H-%M-%S.png'
            filename = datetime.now().strftime(template)
        image = PNMImage()
        if not self.win.get_screenshot(image):
            return False
        if filename.lower().endswith('.png'):
            # remove alpha channel when export to png
            image.remove_alpha()
        if not image.write(filename):
            return False
        return True

    def get_screenshot(self, requested_format='BGRA'):
        """Capture and return a screenshot from offscreen buffer.

        Keyword Arguments:
            requested_format {str} -- image channels, e.g. RGB, BGR (default: {'BGRA'})

        Returns:
            ndarray -- image as uint8 numpy array (height, width, num_channels)
        """
        texture = self.win.get_screenshot()
        if texture is None:
            return None
        xsize = texture.get_x_size()
        ysize = texture.get_y_size()
        dsize = len(requested_format)
        image = texture.get_ram_image_as(requested_format)
        array = np.asarray(image).reshape((ysize, xsize, dsize))
        return np.flipud(array)

    def _make_light_ambient(self, color):
        light = AmbientLight('Ambient Light')
        light.set_color(Vec3(*color))
        return self.render.attach_new_node(light)

    def _make_light_direct(self, index, color, pos, target=(0, 0, 0)):
        if self._spotlight:
            light = Spotlight('Spotlight {:02d}'.format(index))
        else:
            light = DirectionalLight('Directional Light{:02d}'.format(index))
        light.set_color(Vec3(*color))
        light.set_camera_mask(self.LightMask)
        light.set_shadow_buffer_size(
            (self._shadow_size, self._shadow_size))
        lens = light.get_lens()
        lens.set_film_size(5.5, 5.5)
        lens.set_near_far(10, 30)
        node = self.render.attach_new_node(light)
        node.set_pos(*pos)
        node.look_at(*target)
        return node

    def _make_fog(self):
        fog = Fog('fog')
        fog.set_mode(Fog.MExponentialSquared)
        fog.set_color(self.win.get_clear_color())
        fog.set_exp_density(0.1)
        return fog

    def _make_axes(self):
        model = GeomNode('axes')
        model.add_geom(geometry.make_axes())
        node = self.render.attach_new_node(model)
        node.set_light_off()
        node.set_render_mode_wireframe()
        node.set_render_mode_thickness(4)
        node.set_antialias(AntialiasAttrib.MLine)
        node.hide(self.LightMask)
        return node

    def _make_grid(self):
        model = GeomNode('grid')
        model.add_geom(geometry.make_grid())
        node = self.render.attach_new_node(model)
        node.set_light_off()
        node.set_render_mode_wireframe()
        node.set_antialias(AntialiasAttrib.MLine)
        node.hide(self.LightMask)
        return node

    def _make_floor(self):
        model = GeomNode('floor')
        model.add_geom(geometry.make_plane(size=(10, 10)))
        node = self.render.attach_new_node(model)
        node.set_color(Vec4(0.3, 0.3, 0.3, 1))
        material = Material()
        material.set_ambient(Vec4(0, 0, 0, 1))
        material.set_diffuse(Vec4(0.3, 0.3, 0.3, 1))
        material.set_specular(Vec3(1, 1, 1))
        material.set_roughness(0.8)
        node.set_material(material, 1)
        return node

    def _toggle_fps(self):
        self.set_frame_rate_meter(self.frameRateMeter is None)

    def _toggle_help(self):
        if self._help_label is None:
            self._help_label = self._make_help_label()
        else:
            self._help_label.removeNode()
            self._help_label = None

    def _setup_shortcuts(self):
        self.accept('space', self.save_screenshot)
        self.accept('escape', self.stop)
        self.accept('f1', self._toggle_help)
        self.accept('a', lambda: self.show_axes(self._axes.is_hidden()))
        self.accept('d', lambda: self.enable_hdr(not self._hdr_enabled))
        self.accept('g', lambda: self.show_grid(self._grid.is_hidden()))
        self.accept('h', self._toggle_help)
        self.accept('f', self._toggle_fps)
        self.accept('l', lambda: self.enable_lights(not self._lights_enabled))
        self.accept('o', lambda: self.enable_fog(not self.render.has_fog()))
        self.accept('q', self.stop)
        self.accept('p', lambda: self.show_floor(self._floor.is_hidden()))
        self.accept('r', self.reset_camera, self._camera_defaults)
        self.accept('s', lambda: self.enable_shadow(not self._shadow_enabled))
        self.accept('t', self.toggle_texture)
        self.accept('w', self.toggle_wireframe)

    def _make_help_label(self):

        def section(title, items):
            return '{}:\n'.format(title) + \
                '\n'.join((' {}:\t{}'.format(l, k) for l, k in items))

        keyboard = (
            ("Show help", "F1, h"),
            ("Quit window", "Escape, q"),
            ("Screenshot", "Space"),
            ("Toggle axes", "a"),
            ("Toggle HDR", "d"),
            ("Toggle grid", "g"),
            ("Toggle fps meter", "f"),
            ("Toggle lighting", "l"),
            ("Toggle fog", "o"),
            ("Toggle plane", "p"),
            ("Reset camera", "r"),
            ("Toggle shadows", "s"),
            ("Toggle texture", "t"),
            ("Toggle wireframe", "w"),
        )
        mouse = (
            ("Move", "LMB"),
            ("Scale", "RMB, Ctrl+LMB"),
            ("Rotate", "LMB+RMB, Alt+LMB"),
            ("Tilt", "Alt+Ctrl+LMB")
        )
        text = '\n\n'.join((
            section("Keyboard shortcuts", keyboard),
            section("Mouse control", mouse)
        ))

        return OnscreenText(text=text,
                            parent=self.a2dTopLeft,
                            align=TextNode.ALeft,
                            style=1,
                            bg=(0.1, 0.1, 0.1, 0.5),
                            fg=(1, 1, 0.5, 0.7),
                            shadow=(0, 0, 0, .4),
                            pos=(0.06, -0.1),
                            scale=.05)
