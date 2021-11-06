#!python
#
# Worldpixel
# authors: A. Kiipli
#
# Now its taking shape!
# User can delete voxels and reveal them by turning off parents spawned variable.
# Next steps involve advancements to animation and means to generate these animation
# files. Pretty evolved business is wiring up all the ui to work with multiobject
# system. Local centers enables baked coordinates and secondary transformation.
# Then local axis and angle are used, and local direction for rotation.
# As soon as user exits local mode, objects align up with world coordinates.

from OpenGL.GL import *
from OpenGL.GLU import *
import os, gc
import subprocess
import messageBox
import time
from numpy import *
import threading
from Classy import *

import urllib
import validators

from pygame.locals import *

import DragAndDrop
import navigator
import obj_loader
import scan_object
import shutil

try:
    import psutil
    psutil_enable = True
except:
    psutil_enable = False

global Xdim, Ydim, Zdim

pyversion = sys.version_info[0]

if pyversion < 3:
    import urllib2
else:
    import urllib.request as urllib2

def internet_on():
    try:
        response=urllib2.urlopen('http://google.com', timeout = 1)
        return True
    except urllib2.URLError as err: pass
    return False

internetOn = internet_on()

mem_Limit = 80.0

black = 0, 0, 0
white = 255, 255, 255
red = (255, 0, 0)
green = 0, 255, 0
blue = 0, 0, 255

nr = 0
nr_palette = 0

palettes = [1, 2, 3, 4, 7, 10, 12, 5, 6, 8, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

myFormats = [
    ('Pictures','*.png *.jpg *.gif'),
    ('Portable Network Graphics','*.png'),
    ('JPEG / JFIF','*.jpg'),
    ('CompuServer GIF','*.gif'),
    ('Tagged Image','*.tif'),
    ("All files", "*.*"),
    ]

white = (255, 255, 255)

SDL_bind = False
Depth_Mode = False

OBJ_Mode = False

strip_W = 50
strip_H = 50

cmd_folder = os.path.relpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
cmd_folder = os.path.join(cmd_folder, "Folders/imgstall/")
print('Worldpixel', cmd_folder)
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

rsc_folder          = "Folders/resources/"
palette_folder      = "Folders/resources/Palette/"
cursor_folder       = "Folders/resources/Cursor/"
folders             = "Folders"
obj_files           = "OBJ"
raster_dir          = "Raster"
pic_files_dir       = "Pic"
voxels_dir          = "Voxels"
object_dir          = "object"
scene_dir           = "Scene"
back_pic            = "Back"
sceneDir            = "Custom"
animDir             = "Anim"
repro_Dir           = "Repro"
texturesDir         = "Textures"
arraysDir           = "Arrays"
PICC                = "Folders/Pic/picc.txt"
VOXX                = "Folders/Voxels/"
keyframeDir         = "keyframes"

previousScene       = None
lastusedDir         = "."

try:
    from PIL import Image, ImageTk, ImageChops
    from PIL import ImageDraw, ImageFont
    file_extension = "jpg"
    noPIL = False
except:
    file_extension = "gif"
    noPIL = True

platform = sys.platform
sysversion = sys.version

if pyversion < 3:
    import cStringIO
    import Tkinter as tk
    import tkColorChooser
    import tkFont
    import Queue
    from tkFileDialog import askdirectory
    from tkFileDialog import askopenfilename
    from tkFileDialog import asksaveasfilename
else:
    from io import StringIO
    import tkinter as tk
    import tkinter.colorchooser as tkColorChooser
    import tkinter.font as tkFont
    import queue as Queue
    from tkinter.filedialog import askdirectory
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename

if platform == "win32":
    os.environ['TKDND_LIBRARY'] = "C:\Python27\tcl\tkdnd2.8"

if platform == 'linux2':
    from DnD import DnD
else:
    from tkdnd_wrapper import TkDND

class Dnd():
    def __init__(self, item, callback, dnd):
        self.item = item
        self.callback = callback
        self.dnd = dnd

    def drag(self, action, actions, type, win, X, Y, x, y, data):
        return action

    def drag_enter(self, action, actions, type, win, X, Y, x, y, data):
        self.item.focus_force()
        return action

    def drop(self, action, actions, type, win, X, Y, x, y, data):
        #files = data.split()
        self.callback(None, self.item, X, Y, data)

    def bindtarget(self):
        self.dnd.bindtarget(self.item, 'text/uri-list', '<Drag>', self.drag, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
        self.dnd.bindtarget(self.item, 'text/uri-list', '<DragEnter>', self.drag_enter, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
        self.dnd.bindtarget(self.item, 'text/uri-list', '<Drop>', self.drop, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y','%D'))

import embedphoto

if platform == 'win32':
    from ctypes import windll
    user = windll.user32

if platform == 'darwin':
    button_height = 1
else:
    button_height = 1

if platform == 'cygwin':
    widget_bg = None
    widget_hg = None
    widget_ag = None
    widget_fg = None
    widget_st = None
    widget_bc = "#ffffff"
else:
    widget_bg = "#366cad"
    widget_hg = "#5b80ad"
    widget_ag = "#3268ac"
    widget_fg = "#ffffff"
    widget_st = "#a9c5e7"
    widget_bc = "#ffffff"

depth_factor = 1.0
scale_factor = 2.0

hpos = 0
hstep = 140
border = 7
wm_frame = None

timeticks = 100
animLength = 25

fps = 30
delay_ms = int(1000 / fps)

rotation_amount = pi / 180.0

canvas_w = 460
canvas_h = 460

offset_2w = 2
offset_2h = 2

canvas_2w = canvas_w / 2 + offset_2w
canvas_2h = canvas_h / 2 + offset_2h

pic_image = 'Maailmapunkt_Gray1.png'

def hextorgb(s):
    if pyversion < 3:
        rgb = tuple(map(ord, s.decode('hex')))
    else:
        rgb = tuple(map(int, bytes.fromhex(s)))
    return rgb

if pyversion > 2:
    def unichr(x):
        return chr(x)

class NotFound(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Progress():
    def setup_progress(self, total, start = 0, RWidth = 200, RHeight = 150, downhill = False):
        if self.progressbar != None and self.progressbar.winfo_exists():
            self.progressbar.lift_it()
            self.progressbar.focus_set()
        else:
            self.progressbar = messageBox.ProgressBar(parent = None, root = None, ok = 'quit_progress',
                                                                 T = "WorldPixel", bc = widget_bc,
                                                                 total = total, Start = start, default = "-------------",
                                                                 RWidth = RWidth, RHeight = RHeight,
                                                                 bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg,
                                                                 downhill = downhill)
            self.progressbar.bind('<Escape>', lambda e: self.quit_progress())
            self.progressbar.protocol("WM_DELETE_WINDOW", self.quit_progress)
            self.progressbar.bind('<Escape>', lambda e: self.quit_progress())

    def quit_progress(self):
        if self.progressbar != None and self.progressbar.winfo_exists():
            self.progressbar.quit()
            self.progressbar = None

class currentObject():
    def __init__(self, o = None, v = None, d = None, l = None, f = None):
        self.object = o

        self.voxel = v
        self.dim = d
        self.level = l
        self.frame = f

        self.size_array = o.get_size_array
        self.color_array = o.get_color_array
        self.angle = o.get_angle
        self.vector = o.get_vector
        self.local = o.get_local
        self.direction = o.get_direction
        self.voxels = o.get_voxels
        self.get_direction = o.get_direction
        self.position = o.get_position
        self.conform_position = o.get_conform_position
        self.local_position = o.get_local_position
        self.local_conform = o.get_local_conform
        self.center = o.get_center
        self.highlighted = o.get_highlighted
        self.highlight_color = o.get_highlight_color
        self.collected = o.get_collected
        self.rect = o.get_rect
        self.animated_Cube = o.get_animated_Cube
        self.voxelLimit = o.get_voxelLimit
        self.levelLimit = o.get_levelLimit
        self.neighbours = o.get_neighbours
        self.cube = o.get_cube
        self.cube3d = o.get_cube3d
        self.draw_Cube = o.get_draw_Cube
        self.parent = o.get_parent
        self.LOCAL = o.get_LOCAL
        self.falloff = o.get_falloff
        self.index = o.get_index
        self.image = o.get_image
        self.OBJ_repro = o.get_OBJ_repro
        self.Frames = o.get_Frames
        self.repro = o.get_repro
        self.texName = o.get_texName
        self.texture = o.get_texture
        self.GroundImage = o.get_groundImage
        self.get_local_vector = o.get_local_vector
        self.ground = o.get_ground
        self.draw_Ground = o.get_draw_Ground
        self.print_array = o.print_array
        self.get_dimension = o.get_dimension
        self.renumber_invisible = o.renumber_invisible
        self.get_dimensions = o.get_dimensions
        self.get_object_data = o.get_object_data
        self.select_by_VoxelDim = o.select_by_VoxelDim
        self.set_highlighted = o.set_highlighted
        self.set_draw_ground = o.set_draw_ground
        self.reset_Oscillate = o.reset_Oscillate
        self.return_Pos_And_Scale = o.return_Pos_And_Scale
        self.return_Wire_Render = o.return_Wire_Render
        self.select_Level = o.select_Level
        self.select_visible_level = o.select_visible_level
        self.return_levelVoxels = o.return_levelVoxels

        self.name = o.get_name
        self.Name = o.name

        self.set_object_data = o.set_object_data
        self.spawn_to_voxels = o.spawn_to_voxels
        self.apply_to_voxels = o.apply_to_voxels
        self.apply_to_voxels_repro = o.apply_to_voxels_repro
        self.print_invisible_voxels = o.print_invisible_voxels

        self.join = o.join
        self.delete_invisible_arrays = o.delete_invisible_arrays
        self.delete_voxels_below = o.delete_voxels_below
        self.cleanup = o.cleanup
        self.set_spin_random = o.set_spin_random
        self.set_spin = o.set_spin
        self.set_spin_amount = o.set_spin_amount
        self.set_spin_amount_random = o.set_spin_amount_random
        self.selectSameLevel = o.selectSameLevel
        self.selectSameTexture = o.selectSameTexture
        self.selectSameOBJ = o.selectSameOBJ
        self.selectHighlighted = o.selectHighlighted
        self.selectSameImage = o.selectSameImage
        self.make_unique = o.make_unique
        self.toggle_propagate = o.toggle_propagate
        self.toggle_draft_Mode = o.toggle_draft_Mode
        self.toggle_draw_Cube = o.toggle_draw_Cube
        self.toggle_GL_depth_cued = o.toggle_GL_depth_cued
        self.select_array = o.select_array
        self.select_child_voxels = o.select_child_voxels
        self.set_voxel_color = o.set_voxel_color
        self.affect_neighbours = o.affect_neighbours
        self.select_neighbours_by_cube = o.select_neighbours_by_cube
        self.setup_Smooth_Arrays = o.setup_Smooth_Arrays
        self.perform_smoothing = o.perform_smoothing
        self.smooth_sizes_colors = o.smooth_sizes_colors
        self.smooth_sizes = o.smooth_sizes
        self.smooth_colors = o.smooth_colors
        self.select_expand = o.select_expand
        self.find_neighbours = o.find_neighbours
        self.update_voxels_scale = o.update_voxels_scale
        self.paste_by_coordinates = o.paste_by_coordinates
        self.give_by_coordinates = o.give_by_coordinates
        self.give_active_bounds = o.give_active_bounds
        self.validate_animated_Cube = o.validate_animated_Cube
        self.dump_arrays = o.dump_arrays
        self.setup_array = o.setup_array
        self.arrange_animated_Cube = o.arrange_animated_Cube
        self.shift_colors_reset = o.shift_colors_reset
        self.shift_colors = o.shift_colors
        self.reset_all_voxels = o.reset_all_voxels
        self.reset_matrix = o.reset_matrix
        self.manifest_grays = o.manifest_grays
        self.manifest_color = o.manifest_color
        self.get_portion_of_cube = o.get_portion_of_cube
        self.select_same_Currency = o.select_same_Currency
        self.select_through_xyz = o.select_through_xyz
        self.load_frame_size = o.load_frame_size
        self.load_frame = o.load_frame
        self.load_vector_frame = o.load_vector_frame
        self.write_frame = o.write_frame
        self.get_biggest_pixel = o.get_biggest_pixel
        self.reset_camera_pan = o.reset_camera_pan
        self.store_angle = o.store_angle
        self.restore_angle = o.restore_angle
        self.undo_zoom_screen = o.undo_zoom_screen
        self.reset_pan = o.reset_pan
        self.move_to_the_screen = o.move_to_the_screen
        self.invert_collected = o.invert_collected
        self.clear_collected = o.clear_collected
        self.return_voxels_in_3d_rect = o.return_voxels_in_3d_rect
        self.voxel_at_coordinates = o.voxel_at_coordinates
        self.return_prominent_3d_voxel = o.return_prominent_3d_voxel
        self.return_3d_rect = o.return_3d_rect
        self.get_current = o.get_current
        self.put_current = o.put_current
        self.get_collection = o.get_collection
        self.set_collection = o.set_collection
        self.refine_highlighted_level = o.refine_highlighted_level
        self.refine_highlighted = o.refine_highlighted
        self.raise_levels = o.raise_levels
        self.append_collection = o.append_collection
        self.create_3d_array = o.create_3d_array
        self.return_slice_with = o.return_slice_with
        self.subtract_collection = o.subtract_collection
        self.create_collection = o.create_collection
        self.highlight_collection = o.highlight_collection
        self.highlight_all = o.highlight_all
        self.highlight_tree = o.highlight_tree

        self.remove_highlighted_level = o.remove_highlighted_level
        self.remove_highlighted = o.remove_highlighted
        self.collapse_all = o.collapse_all
        self.clear_highlight = o.clear_highlight
        self.clear_illumination = o.clear_illumination
        self.validate_highlight = o.validate_highlight
        self.get_highlight = o.get_highlight
        self.remove_highlight = o.remove_highlight
        self.change_spawned = o.change_spawned
        self.localize_nodes = o.localize_nodes
        self.restore_vector = o.restore_vector
        self.set_vector = o.set_vector
        self.set_angle = o.set_angle
        self.set_name = o.set_name

        self.localize = o.localize

        self.give_local_vector = o.give_local_vector

        self.give_center = o.give_center
        self.give_center_parent = o.give_center_parent
        self.give_center_actual = o.give_center_actual
        self.select_closest = o.select_closest
        self.set_picmap = o.set_picmap
        self.render_shadows = o.render_shadows
        self.set_voxel_images = o.set_voxel_images
        self.set_voxel_repro = o.set_voxel_repro
        self.set_voxel_texture = o.set_voxel_texture
        self.set_images = o.set_images
        self.set_repro = o.set_repro
        self.set_texture = o.set_texture
        self.set_frame = o.set_frame
        self.set_voxel_oscillate = o.set_voxel_oscillate
        self.set_voxel_frames = o.set_voxel_frames
        self.clean_Ground = o.clean_Ground
        self.set_Ground = o.set_Ground
        self.set_Ground_Texture = o.set_Ground_Texture
        self.draw_selection_rect = o.draw_selection_rect
        self.render = o.render
        self.z_sort = o.z_sort
        self.add_voxels = o.add_voxels
        self.insert_voxels = o.insert_voxels
        self.validate_voxels = o.validate_voxels
        self.delete_voxels = o.delete_voxels
        self.delete_voxel = o.delete_voxel
        self.remove_voxels = o.remove_voxels
        self.move_around = o.move_around
        self.reset_position = o.reset_position
        self.move_conform = o.move_conform
        self.move_to_conform = o.move_to_conform
        self.add_conform_positions = o.add_conform_positions
        self.switch_conform_position = o.switch_conform_position
        self.bake_xyz_rotation = o.bake_xyz_rotation
        self.bake_rotation = o.bake_rotation
        self.restore_xyz_baked = o.restore_xyz_baked
        self.rotate3d_x = o.rotate3d_x
        self.rotate3d_y = o.rotate3d_y
        self.rotate3d_z = o.rotate3d_z
        self.rotate3d_vector = o.rotate3d_vector

    def set_LOCAL(self, value):
        self.object.set_LOCAL(value)

    def reset_local_conform(self):
        print("reset_local_conform")
        self.object.local_conform[:] = [0, 0, 0]

    def set_depth(self, d):
        self.object.Depth = d

    def set_direction(self, d):
        self.object.direction = d

    def set_center(self, c):
        self.object.center = c

    def set_draw_Cube(self, mode):
        self.object.draw_Cube = mode

    def set_depth_cued(self, d):
        self.object.GL_depth_cued = d

    def __getitem__(self):
        return self.object

    def __getitem__(self, v):
        return self.object[v]

class Coordinates_2d():
    def __init__(self, position = (0.0, 0.0)):
        self.x = position[0]
        self.y = position[1]

    def __getitem__(self, index):
        if index == 0:
            return self.x
        if index == 1:
            return self.y

class rect_2d():
    def __init__(self, rect = (0.0, 0.0, 0.0, 0.0)):
        self.max = Coordinates_2d()
        self.min = Coordinates_2d()
        self.center = Coordinates_2d()
        self.max.x = rect[0]
        self.max.y = rect[1]
        self.min.x = rect[2]
        self.min.y = rect[3]
        self.state = False

    def give_center(self):
        self.center.x = (self.min.x + self.max.x) / 2
        self.center.y = (self.min.y + self.max.y) / 2
        return self.center

    def put_array(self):
        X = arange(self.min.x, self.max.x)
        Y = arange(self.min.y, self.max.y)
        T = [(x, y) for y in Y for x in X]
        return T

    def return_tuple(self):
        return (self.max.x, self.max.y, self.min.x, self.min.y)

    def validate(self):
        if self.max.x < self.min.x:
            x = self.max.x
            self.max.x = self.min.x
            self.min.x = x
        if self.max.y < self.min.y:
            y = self.max.y
            self.max.y = self.min.y
            self.min.y = y

class tk_App(threading.Thread, Progress):
    def __init__(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", lambda e = None: self.callback_exit(e))
        self.root.bind('<Alt-q>', lambda e: self.menu_exit())

        self.update_wm = None
        self.wm_update = True

        self.root.bind('<Configure>', lambda e: self.wm_configure(e))
        self.root.bind('<Control-q>', self.exit_self)
        self.root.bind('<Control-o>', lambda e: self.open_DragAndDropView())

        if platform == 'linux2':
            self.dnd = DnD(self.root)
        else:
            self.dnd = TkDND(self.root)

        self.root.configure(bg = widget_bg)

        self.left_palette = tk.PhotoImage(file = rsc_folder + "Leftpalette.GIF")
        self.right_palette = tk.PhotoImage(file = rsc_folder + "Rightpalette.GIF")

        self.colorsandshape = tk.PhotoImage(file = rsc_folder + "colorsands.GIF")
        self.colorimage     = tk.PhotoImage(file = rsc_folder + "colorimage.GIF")
        self.shapeimage     = tk.PhotoImage(file = rsc_folder + "shapeimage.GIF")
        self.emptyshape     = tk.PhotoImage(file = rsc_folder + "emptyshape.GIF")

        self.c_tabs = 0

        self.pasteframe = PasteFrame()
        self.backup_frame = []
        self.visited = ""

        self.pic_image = pic_image
        self.msg_box_Pic_rotation = None
        self.random_rot = 0
        self.repro_random_rot = 0
        self.minorlevel = True

        self.msg_box_OBJ_repro = None
        self.msg_box_OBJ_repros = None
        self.msg_box_Smooth = None
        self.msg_box_Position_Scale_size = None
        self.msg_box_repro_rotation = None
        self.msg_box_repro_spin_amount = None
        self.msg_box_vector_smooth = None
        self.msg_box_repro_spin = None
        self.msg_box_Minor_level = None
        self.msg_box_Image_panel = None
        self.msg_box_Object_name = None
        self.msg_box_Scene_name = None
        self.msg_box_Canvas_size = None
        self.msg_box_LocalCenter = None
        self.msg_box_VoxelsRepro = None
        self.msg_box_quit_app = None
        self.crossfadebox = None
        self.about_box_app = None
        self.AboutThisVoxel = None
        self.progressbar = None
        self.helpbox = None
        self.confbox = None
        self.DragAndDropView = None
        self.Url_Filename = None

        self.VectorSmooth = 100
        self.spin_amount = 0
        self.spin = 0

        self.textures_folder = texturesDir

        self.output_folder        = "Folders/Images/"
        self.output_filename      = "animation_frames"
        self.output_format        = "xxxx"

        self.outPutDir = None

        self.followrender = True
        self.render_frames = 25
        self.start_frame = 0
        self.animation_rotate = True
        self.anim_sequence = True
        self.object_centers = True

        RTitle = self.root.title("World Pixel " + sceneDir)
        self.RWidth = int(self.root.winfo_screenwidth())
        self.RHeight = int(self.root.winfo_screenheight())
        self.root.geometry(("%dx%d+%d+0") % (self.RWidth / 1.5, self.RHeight / 1.1, self.RWidth - (self.RWidth / 1.5)))
        if hasattr(sys, '_MEIPASS'):
            self.root.wm_iconbitmap('worldpixel.ico')
        else:
            icon_img = tk.PhotoImage(data = embedphoto.icon_gif)
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon_img)

        self.courier10 = tkFont.Font(family = "Courier", size = 10, weight = "normal")
        self.sans10 = tkFont.Font(family = "sans-serif", size = 10, weight = "normal")
        self.sans8 = tkFont.Font(family = "sans-serif", size = 8, weight = "normal")
        sserif7 = tkFont.Font(family = "sans-serif", size = 7, weight = "normal")

        self.m_frames = []
        self.m_frames1 = []
        self.pos_H = 0
        self.hstep = hstep

        self.background_color = "#ff0000"

        if platform == 'darwin':
            self.clear_color = (255, 0, 0, 0) #255)
        else:
            self.clear_color = (255, 0, 0, 0)

        self.Rotation_Amount = rotation_amount

        menubar = tk.Menu()

        menubar.bind('<<MenuSelect>>', lambda e: self.menubar_action(e))

        self.mouse_move_Setup = False

        #self.localRefresh = False
        self.localCenter = False
        self.local_Center = tk.BooleanVar()
        self.local_Center.set(self.localCenter)

        self.local_Center_backup = False
        self.VBOFrames_backup = False

        self.View = False

        self.frontView = False
        self.front_View = tk.BooleanVar()
        self.front_View.set(self.frontView)

        self.sideView = False
        self.side_View = tk.BooleanVar()
        self.side_View.set(self.sideView)

        self.topView = False
        self.top_View = tk.BooleanVar()
        self.top_View.set(self.topView)

        self.syncLevels = True
        self.sync_Levels = tk.BooleanVar()
        self.sync_Levels.set(self.syncLevels)

        self.SDL_Mode = tk.BooleanVar()
        self.SDL_Mode.set(SDL_bind)

        self.OBJ_bind = OBJ_Mode
        self.OBJ_Mode = tk.BooleanVar()
        self.OBJ_Mode.set(self.OBJ_bind)

        self.Lights = True
        self.Zoomed = False
        self.isolate_rest = []

        self.GL_Lights = tk.BooleanVar()
        self.GL_Lights.set(self.Lights)

        self.OBJ_Wire = False

        self.GL_Wire = tk.BooleanVar()
        self.GL_Wire.set(self.OBJ_Wire)

        self.WireFrame = False

        self.GL_WireFrame = tk.BooleanVar()
        self.GL_WireFrame.set(self.WireFrame)

        self.GL_depth_cued = Depth_Mode
        self.Depth_Mode = tk.BooleanVar()
        self.Depth_Mode.set(self.GL_depth_cued)

        self.Background = True
        self.Background_Mode = tk.BooleanVar()
        self.Background_Mode.set(self.Background)

        self.Ground = True
        self.Ground_Mode = tk.BooleanVar()
        self.Ground_Mode.set(self.Ground)

        self.Shadows = True
        self.Shadow_Mode = tk.BooleanVar()
        self.Shadow_Mode.set(self.Shadows)

        self.VBO = True
        self.VBO_Mode = tk.BooleanVar()
        self.VBO_Mode.set(self.VBO)

        self.VBOFrames = True
        self.VBO_Frames = tk.BooleanVar()
        self.VBO_Frames.set(self.VBOFrames)

        self.VBOTween = True
        self.VBO_Tween = tk.BooleanVar()
        self.VBO_Tween.set(self.VBOTween)

        self.AlphaMode = False
        self.Alpha_Mode = tk.BooleanVar()
        self.Alpha_Mode.set(self.AlphaMode)

        self.BlurMode = False
        self.Blur_Mode = tk.BooleanVar()
        self.Blur_Mode.set(self.BlurMode)

        self.NoiseMode = False
        self.Noise_Mode = tk.BooleanVar()
        self.Noise_Mode.set(self.NoiseMode)

        self.BandingMode = False
        self.Banding_Mode = tk.BooleanVar()
        self.Banding_Mode.set(self.BandingMode)

        self.hBandingMode = False
        self.hBanding_Mode = tk.BooleanVar()
        self.hBanding_Mode.set(self.hBandingMode)

        self.MedianMode = False
        self.Median_Mode = tk.BooleanVar()
        self.Median_Mode.set(self.MedianMode)

        self.EdgeMode = False
        self.Edge_Mode = tk.BooleanVar()
        self.Edge_Mode.set(self.EdgeMode)

        self.syncPositions = False
        self.sync_Positions = tk.BooleanVar()
        self.sync_Positions.set(self.syncPositions)

        self.vectorAnim = True
        self.vector_Anim = tk.BooleanVar()
        self.vector_Anim.set(self.vectorAnim)

        self.LockAngle = True
        self.Lock_Angle = tk.BooleanVar()
        self.Lock_Angle.set(self.LockAngle)

        Local_1 = tk.BooleanVar()
        Local_2 = tk.BooleanVar()
        Local_3 = tk.BooleanVar()
        Local_4 = tk.BooleanVar()

        self.Local = [Local_1, Local_2, Local_3, Local_4]

        self.menu1 = tk.Menu(menubar, tearoff = 1, bg = widget_bg)
        self.menu1.add("checkbutton", label = "local center Shift+L", onvalue = 1, offvalue = 0, variable = self.local_Center,
                             command = lambda: self.toggle_local_Center())
        menu1_0_0 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "View ...>", menu = menu1_0_0)
        menu1_0_0.add("checkbutton", label = "front View Shift+F", onvalue = 1, offvalue = 0, variable = self.front_View,
                             command = lambda: self.toggle_View("front"))
        menu1_0_0.add("checkbutton", label = "side View Shift+S", onvalue = 1, offvalue = 0, variable = self.side_View,
                             command = lambda: self.toggle_View("side"))
        menu1_0_0.add("checkbutton", label = "top View Shift+T", onvalue = 1, offvalue = 0, variable = self.top_View,
                             command = lambda: self.toggle_View("top"))
        self.menu1.add('separator')
        menu1_0 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Scene ...>", menu = menu1_0)
        menu1_0.add_command(label = "Set scene name Ctrl+n", command = lambda: self.set_scene_name_dialog())
        menu1_0.add_command(label = "save all files Ctrl+s", command = lambda: self.save_all_files())
        menu1_0.add_command(label = "load object scene Ctrl+l", command = lambda: self.load_object_scene())
        self.menu1.add('separator')
        self.menu1_1 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Objects ...>", menu = self.menu1_1)
        self.menu1_1.add("checkbutton", label = "local object 1", onvalue = 1, offvalue = 0, variable = Local_1,
                       command = lambda: self.toggle_object(self.local1))
        self.menu1_1.add("checkbutton", label = "local object 2", onvalue = 1, offvalue = 0, variable = Local_2,
                       command = lambda: self.toggle_object(self.local2))
        self.menu1_1.add("checkbutton", label = "local object 3", onvalue = 1, offvalue = 0, variable = Local_3,
                       command = lambda: self.toggle_object(self.local3))
        self.menu1_1.add("checkbutton", label = "local object 4", onvalue = 1, offvalue = 0, variable = Local_4,
                       command = lambda: self.toggle_object(self.local4))
        self.menu1_1.add('separator')
        self.menu1_1.add_command(label = "Append object", command = lambda: self.append_object())
        self.menu1_1.add_command(label = "Remove object", command = lambda: self.remove_object())
        self.menu1_1.add('separator')
        self.menu1.add('separator')
        menu1_2 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Object Name ...>", menu = menu1_2)
        menu1_2.add_command(label = "set object name", command = lambda: self.set_object_name_dialog())
        menu1_2.add_command(label = "isolate object", command = lambda: self.isolate_object(self.objectList))
        self.menu1.add('separator')
        menu1_3 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Sync Voxels ...>", menu = menu1_3)
        menu1_3.add_command(label = "print out voxels", command = lambda: self.print_out_voxels(self.current_Object))
        menu1_3.add_command(label = "read out voxels", command = lambda: self.read_out_voxels(self.current_Object, True, True))
        menu1_3.add_command(label = "sync visible", command = lambda: self.sync_voxels())
        menu1_3.add_command(label = "sync voxels color", command = lambda: self.sync_voxels(True))
        self.menu1.add('separator')
        menu1_4 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Object Reading ...>", menu = menu1_4)
        menu1_4.add_command(label = "save object files", command = lambda: self.save_object_files())
        menu1_4.add_command(label = "read object files", command = lambda: self.read_object_files(collapse = False, ground = True))
        menu1_4.add_command(label = "read object file", command = lambda: self.read_object_file(self.current_Object, ground = True))
        self.menu1.add('separator')
        self.menu1.add("checkbutton", label = "lock Angle", onvalue = 1, offvalue = 0, variable = self.Lock_Angle,
                             command = lambda: self.toggle_LockAngle())
        self.menu1.add("checkbutton", label = "sync position", onvalue = 1, offvalue = 0, variable = self.sync_Positions,
                             command = lambda: self.toggle_syncPositions())
        self.menu1.add("checkbutton", label = "sync levels", onvalue = 1, offvalue = 0, variable = self.sync_Levels,
                             command = lambda: self.toggle_syncLevels())
        self.menu1.add('separator')
        self.menu1.add("checkbutton", label = "vector anim", onvalue = 1, offvalue = 0, variable = self.vector_Anim,
                             command = lambda: self.toggle_vector_Anim())
        self.menu1.add('separator')
        self.menu1.add_command(label = "copy selection", command = lambda: self.copy_selection())
        self.menu1.add_command(label = "paste selection", command = lambda: self.paste_selection())
        self.menu1.add('separator')
        menu1_5 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Worldpixel Modes ...>", menu = menu1_5)
        menu1_5.add("checkbutton", label = "toggle Alpha Mode", onvalue = 1, offvalue = 0, variable = self.Alpha_Mode,
                             command = lambda: self.toggle_Alpha_Mode())
        menu1_5.add("checkbutton", label = "toggle Blur Mode", onvalue = 1, offvalue = 0, variable = self.Blur_Mode,
                             command = lambda: self.toggle_Blur_Mode())
        menu1_5.add("checkbutton", label = "toggle Median Mode", onvalue = 1, offvalue = 0, variable = self.Median_Mode,
                             command = lambda: self.toggle_Median_Mode())
        menu1_5.add("checkbutton", label = "toggle Edge Mode", onvalue = 1, offvalue = 0, variable = self.Edge_Mode,
                             command = lambda: self.toggle_Edge_Mode())
        menu1_5.add("checkbutton", label = "toggle Banding Mode", onvalue = 1, offvalue = 0, variable = self.Banding_Mode,
                             command = lambda: self.toggle_Banding_Mode())
        menu1_5.add("checkbutton", label = "toggle Noise Mode", onvalue = 1, offvalue = 0, variable = self.Noise_Mode,
                             command = lambda: self.toggle_Noise_Mode())
        menu1_5.add("checkbutton", label = "toggle hBanding Mode", onvalue = 1, offvalue = 0, variable = self.hBanding_Mode,
                             command = lambda: self.toggle_hBanding_Mode())
        menu1_5.add("checkbutton", label = "toggle SDL Mode Shift+O", onvalue = 1, offvalue = 0, variable = self.SDL_Mode,
                             command = lambda: self.toggle_SDL_Mode())
        menu1_5.add("checkbutton", label = "toggle GL depth cue", onvalue = 1, offvalue = 0, variable = self.Depth_Mode,
                             command = lambda: self.toggle_Depth_Mode())
        menu1_5.add("checkbutton", label = "toggle GL OBJ Mode", onvalue = 1, offvalue = 0, variable = self.OBJ_Mode,
                             command = lambda: self.toggle_OBJ_Mode())
        self.menu1.add('separator')
        menu1_6 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Item Toggles ...>", menu = menu1_6)
        menu1_6.add("checkbutton", label = "toggle Background", onvalue = 1, offvalue = 0, variable = self.Background_Mode,
                             command = lambda: self.toggle_Background())
        menu1_6.add("checkbutton", label = "toggle Ground", onvalue = 1, offvalue = 0, variable = self.Ground_Mode,
                             command = lambda: self.toggle_Ground())
        menu1_6.add("checkbutton", label = "toggle Shadow", onvalue = 1, offvalue = 0, variable = self.Shadow_Mode,
                             command = lambda: self.toggle_Shadows())
        menu1_6.add("checkbutton", label = "toggle GL Lights", onvalue = 1, offvalue = 0, variable = self.GL_Lights,
                             command = lambda: self.toggle_Lights())
        menu1_6.add("checkbutton", label = "toggle VBO", onvalue = 1, offvalue = 0, variable = self.VBO_Mode,
                             command = lambda: self.toggle_VBO())
        menu1_6.add("checkbutton", label = "toggle VBO Frames", onvalue = 1, offvalue = 0, variable = self.VBO_Frames,
                             command = lambda: self.toggle_Frames())
        menu1_6.add("checkbutton", label = "toggle VBO Tween", onvalue = 1, offvalue = 0, variable = self.VBO_Tween,
                             command = lambda: self.toggle_Tween())
        menu1_6.add("checkbutton", label = "toggle GL Wire", onvalue = 1, offvalue = 0, variable = self.GL_Wire,
                             command = lambda: self.toggle_Wire())
        menu1_6.add("checkbutton", label = "toggle GL WireFrame", onvalue = 1, offvalue = 0, variable = self.GL_WireFrame,
                             command = lambda: self.toggle_WireFrame())
        self.menu1.add('separator')

        self.drawCube = True
        
        menu1_7 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Cube Toggles ...>", menu = menu1_7)
        menu1_7.add_command(label = "toggle draw Cube All c", command = lambda: self.toggle_draw_Cube_All())
        menu1_7.add_command(label = "toggle draw Cube", command = lambda: self.toggle_draw_Cube())
        menu1_7.add_command(label = "toggle draft Mode", command = lambda: self.toggle_draft_Mode())
        self.menu1.add('separator')
        menu1_8 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Zoom / Pan ...>", menu = menu1_8)
        menu1_8.add_command(label = "move", command = lambda: self.zoom_to_selected(self.ObjectList, move_only = True))
        menu1_8.add_command(label = "move / zoom Ctrl+Shift+Z", command = lambda: self.zoom_to_selected(self.ObjectList))
        menu1_8.add('separator')
        menu1_8.add_command(label = "undo view", command = lambda: self.undo_view(self.ObjectList, move_only = True))
        menu1_8.add_command(label = "undo view / zoom out Ctrl+Shift+Z", command = lambda: self.undo_view(self.ObjectList))
        menu1_8.add('separator')
        menu1_8.add_command(label = "restore view", command = lambda: self.zoom_to_selected(self.ObjectList, move_only = True, restore = True))
        menu1_8.add_command(label = "reset view", command = lambda: self.zoom_to_selected(self.ObjectList, resetview = True))
        menu1_8.add_command(label = "reset pan", command = lambda: self.reset_pan(self.ObjectList))
        self.menu1.add('separator')
        menu1_9 = tk.Menu(self.menu1, tearoff = 1, bg = widget_bg)
        self.menu1.add_cascade(label = "Rotation Axis ...>", menu = menu1_9)

        self.Axis = tk.IntVar()
        self.Axis.set(0)

        menu1_9.add("checkbutton", label = "axis", onvalue = 0, variable = self.Axis, command = lambda: self.set_axis("axis"))
        menu1_9.add("checkbutton", label = "x", onvalue = 1, variable = self.Axis, command = lambda: self.set_axis("x"))
        menu1_9.add("checkbutton", label = "y", onvalue = 2, variable = self.Axis, command = lambda: self.set_axis("y"))
        menu1_9.add("checkbutton", label = "z", onvalue = 3, variable = self.Axis, command = lambda: self.set_axis("z"))
        menu1_9.add('separator')
        menu1_9.add_command(label = "rotation counterclockwise", command = lambda: self.set_rotation_amount(rotation_amount))
        menu1_9.add_command(label = "rotation clockwise", command = lambda: self.set_rotation_amount(-rotation_amount))
        menu1_9.add_command(label = "toggle rotation", command = lambda: self.toggle_Rotation())
        self.menu1.configure(tearoffcommand = lambda me, m: self.postmenu(me, m, menu = "self.menu1"))
        self.menu1.bind('<q>', lambda e = None: self.menu_exit())

        menubar.add_cascade(label = "List Commands", menu = self.menu1)

        self.everyframe = True
        self.Every_Frame = tk.BooleanVar()
        self.Every_Frame.set(self.everyframe)

        self.idle_id = None
        self.dim = 4
        self.animation_id = None
        self.playing_animation = False
        self.AnimSequence = ones((animLength, self.dim, self.dim, self.dim, 2), dtype = object)
        self.AnimSequence.fill(None)
        self.animLength = timeticks
        self.frame = 0

        self.level = tk.DoubleVar()
        self.level.set(1.0 / self.dim)
        #self.level.trace('w', lambda e, m, c: self.setup_numpy(self.objectList))
        self.animation_copy = None

        self.synchronize = True
        self.Sync = tk.BooleanVar()
        self.Sync.set(self.synchronize)

        self.preMult = False
        self.pre_Mult = tk.BooleanVar()
        self.pre_Mult.set(self.preMult)

        self.smoothColors = True
        self.smooth_Colors = tk.BooleanVar()
        self.smooth_Colors.set(self.smoothColors)

        self.smoothSizes = True
        self.smooth_Sizes = tk.BooleanVar()
        self.smooth_Sizes.set(self.smoothSizes)

        self.colorShifter = False
        self.color_Shifter = tk.BooleanVar()
        self.color_Shifter.set(self.colorShifter)

        self.R = True
        self.R_ = tk.BooleanVar()
        self.R_.set(self.R)

        self.G = True
        self.G_ = tk.BooleanVar()
        self.G_.set(self.G)

        self.B = True
        self.B_ = tk.BooleanVar()
        self.B_.set(self.B)

        self.X_r = True
        self.X_R = tk.BooleanVar()
        self.X_R.set(self.X_r)

        self.Y_r = True
        self.Y_R = tk.BooleanVar()
        self.Y_R.set(self.Y_r)

        self.Z_r = True
        self.Z_R = tk.BooleanVar()
        self.Z_R.set(self.Z_r)

        self.smooth = 10

        self.menu2 = tk.Menu(menubar, tearoff = 1, bg = widget_bg)

        self.menu2.add("checkbutton", label = "premultiply toggle", onvalue = 1, offvalue = 0, variable = self.pre_Mult,
                       command = lambda: self.toggle_pre_Mult())
        menu2_0 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Color / Alpha ...>", menu = menu2_0)
        menu2_0.add_command(label = "set alpha color", command = lambda: self.set_background_color())
        menu2_0.add_command(label = "set alpha amount", command = lambda: self.set_background_alpha())
        menu2_0.add_command(label = "set shadow alpha", command = lambda: self.set_shadow_alpha())
        menu2_0.add_command(label = "set object alpha", command = lambda: self.set_object_alpha())
        self.menu2.add('separator')
        self.menu2.add_command(label = "save frame pic", command = lambda: self.save_frame_as_pict())
        self.menu2.add('separator')
        menu2_1 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Position/Rotation ...>", menu = menu2_1)
        menu2_1.add_command(label = "add positions Shift+A", command = lambda: self.add_positions([self.current_Object,]))
        menu2_1.add_command(label = "reset position Shift+R", command = lambda: self.reset_position([self.current_Object,]))
        menu2_1.add_command(label = "reset rotation", command = lambda: self.reset_rotation_all())
        self.menu2.add('separator')
        menu2_2 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Object Write ...>", menu = menu2_2)
        menu2_2.add_command(label = "write objects", command = lambda: self.write_objects())
        menu2_2.add_command(label = "place config", command = lambda: self.place_config())
        self.menu2.add('separator')
        menu2_3 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Object Pic Write ...>", menu = menu2_3)
        menu2_3.add_command(label = "write objects pic", command = lambda: self.write_objects_pic())
        menu2_3.add_command(label = "place pic config", command = lambda: self.place_images())
        self.menu2.add('separator')
        menu2_4 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Scene state ...>", menu = menu2_4)
        menu2_4.add_command(label = "save scene state", command = lambda: self.save_scene_state())
        menu2_4.add_command(label = "load scene prop", command = lambda: self.load_scene_prop())
        self.menu2.add('separator')
        menu2_5 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Smooth Colors ...>", menu = menu2_5)
        menu2_5.add_command(label = "smooth dial", command = lambda: self.smooth_dial())
        menu2_5.add("checkbutton", label = "smooth sizes", onvalue = 1, offvalue = 0, variable = self.smooth_Sizes,
                       command = lambda: self.toggle_smooth_sizes())
        menu2_5.add("checkbutton", label = "smooth colors", onvalue = 1, offvalue = 0, variable = self.smooth_Colors,
                       command = lambda: self.toggle_smooth_colors())
        self.menu2.add('separator')
        menu2_6 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Array Manipulate ...>", menu = menu2_6)
        menu2_6.add_command(label = "manifest color", command = lambda: self.manifest_color(self.objectList))
        menu2_6.add_command(label = "manifest grays", command = lambda: self.manifest_grays(self.objectList))
        menu2_6.add_command(label = "reset matrix", command = lambda: self.reset_matrix(self.objectList))
        menu2_6.add_command(label = "reset voxels", command = lambda: self.reset_voxels(self.objectList))
        menu2_6.add_command(label = "read disk arrays", command = lambda: self.read_object_arrays(True, False))
        menu2_6.add('separator')
        menu2_6.add_command(label = "size recursive", command = lambda: self.set_size_recursive())
        self.menu2.add('separator')
        menu2_7 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Color Shifter ...>", menu = menu2_7)
        menu2_7.add("checkbutton", label = "R", onvalue = 1, offvalue = 0, variable = self.R_,
                       command = lambda: self.toggle_R())
        menu2_7.add("checkbutton", label = "G", onvalue = 1, offvalue = 0, variable = self.G_,
                       command = lambda: self.toggle_G())
        menu2_7.add("checkbutton", label = "B", onvalue = 1, offvalue = 0, variable = self.B_,
                       command = lambda: self.toggle_B())
        menu2_7.add("checkbutton", label = "color shifter on / off", onvalue = 1, offvalue = 0, variable = self.color_Shifter,
                       command = lambda: self.toggle_color_Shifter())
        self.menu2.add("checkbutton", label = "every frame on / off", onvalue = 1, offvalue = 0, variable = self.Every_Frame,
                       command = lambda: self.every_frame_toggle())
        self.menu2.add('separator')
        self.menu2.add("checkbutton", label = "sync animation", onvalue = 1, offvalue = 0, variable = self.Sync,
                       command = lambda: self.sync_animation())
        self.menu2.add('separator')
        self.menu2.add_command(label = "write sync animation", command = lambda: self.write_sync_animation())
        self.menu2.add_command(label = "write sync animation colocated", command = lambda: self.write_sync_animation(True))
        self.menu2.add('separator')
        menu2_7_1 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Unravel Animation ...>", menu = menu2_7_1)
        menu2_7_1.add_command(label = "fill animation unravel", command = lambda: self.AnimSequence_fill(self.objectList, write = True, unravel = True))
        menu2_7_1.add('separator')
        menu2_7_1.add("checkbutton", label = "X", onvalue = 1, offvalue = 0, variable = self.X_R,
                       command = lambda: self.toggle_X_R())
        menu2_7_1.add("checkbutton", label = "Y", onvalue = 1, offvalue = 0, variable = self.Y_R,
                       command = lambda: self.toggle_Y_R())
        menu2_7_1.add("checkbutton", label = "Z", onvalue = 1, offvalue = 0, variable = self.Z_R,
                       command = lambda: self.toggle_Z_R())
        self.menu2.add('separator')
        menu2_8 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Fill / Start Animation ...>", menu = menu2_8)
        menu2_8.add_command(label = "fill animation", command = lambda: self.AnimSequence_fill(self.objectList, False))
        menu2_8.add_command(label = "start animation", command = lambda: self.start_animation(self.objectList, False))
        menu2_8.add_command(label = "stop animation", command = lambda: self.stop_animation())
        menu2_8.add('separator')
        menu2_8.add_command(label = "randomize animation", command = lambda: self.AnimSequence_random(self.objectList, True))
        menu2_8.add('separator')
        menu2_8.add_command(label = "crossfade animations dialog", command = lambda: self.crossfade_animations(True))
        menu2_8.add_command(label = "crossfade animations", command = lambda: self.crossfade_animations())
        self.menu2.add('separator')
        menu2_9 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Fill Vector Animation ...>", menu = menu2_9)
        menu2_9.add_command(label = "fill vector animation", command = lambda: self.Vector_Animation_fill(self.objectList))
        menu2_9.add_command(label = "fill vector animation smoothed", command = lambda: self.Vector_Animation_fill(self.objectList, smoothed = True))
        menu2_9.add_command(label = "set vector smooth modulate", command = lambda: self.set_VectorSmooth())
        menu2_9.add('separator')
        menu2_9.add_command(label = "randomize vector animation", command = lambda: self.Vector_AnimSequence_random(self.objectList, True))
        menu2_9.add('separator')
        menu2_9.add_command(label = "crossfade vector animations dialog", command = lambda: self.crossfade_vector_animations(True))
        menu2_9.add_command(label = "crossfade vector animations", command = lambda: self.crossfade_vector_animations())
        self.menu2.add('separator')
        menu2_10 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Render Animation ...>", menu = menu2_10)
        menu2_10.add_command(label = "configure animation", command = lambda: self.configure_output())
        menu2_10.add_command(label = "Output folder", command = lambda: self.open_folder(self.output_folder))
        menu2_10.add_command(label = "render animation", command = lambda: self.AnimSequence_render(self.objectList))
        menu2_10.add('separator')
        menu2_10.add_command(label = "display rendered Shift+D", command = lambda: self.display_rendered())
        self.menu2.add('separator')
        menu2_11 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Keyframes ...>", menu = menu2_11)
        menu2_11.add_command(label = "write keyframes", command = lambda: self.write_key_frames())
        menu2_11.add_command(label = "load keyframes", command = lambda: self.load_key_frames())
        menu2_11.add_command(label = "delete keyframes", command = lambda: self.delete_key_frames())
        self.menu2.add('separator')
        menu2_12 = tk.Menu(self.menu2, tearoff = 1, bg = widget_bg)
        self.menu2.add_cascade(label = "Animation ...>", menu = menu2_12)
        menu2_12.add_command(label = "copy animation", command = lambda: self.copy_animation())
        menu2_12.add_command(label = "paste animation", command = lambda: self.paste_animation())
        menu2_12.add('separator')
        menu2_12.add_command(label = "write animation", command = lambda: self.write_AnimSequence_file([self.current_Object,]))
        menu2_12.add_command(label = "load animation", command = lambda: self.load_into_AnimSequence([self.current_Object,]))
        menu2_12.add_command(label = "load anim dialog", command = lambda: self.load_into_AnimSequence([self.current_Object,], True))
        menu2_12.add('separator')
        menu2_12.add_command(label = "write vector animation", command = lambda: self.write_Vector_AnimSequence_file([self.current_Object,]))
        menu2_12.add_command(label = "load vector animation", command = lambda: self.load_Vectors_into_AnimSequence([self.current_Object,]))
        menu2_12.add_command(label = "load vector anim dialog", command = lambda: self.load_Vectors_into_AnimSequence([self.current_Object,], True))
        self.menu2.add('separator')
        self.menu2.configure(tearoffcommand = lambda me, m: self.postmenu(me, m, menu = "self.menu2"))
        self.menu2.bind('<q>', lambda e = None: self.menu_exit())

        menubar.add_cascade(label = "3d Cube Commands", menu = self.menu2)

        self.saveBackground = False
        self.save_Background = tk.BooleanVar()
        self.save_Background.set(self.saveBackground)

        self.clearcolor_Compose = False
        self.clear_color_Compose = tk.BooleanVar()
        self.clear_color_Compose.set(self.clearcolor_Compose)

        self.ImageCombo = True
        self.Image_Combo = tk.BooleanVar()
        self.Image_Combo.set(self.ImageCombo)

        self.RotCombine = True
        self.rot_Combine = tk.BooleanVar()
        self.rot_Combine.set(self.RotCombine)

        self.VoxelBased = False
        self.voxel_Based = tk.BooleanVar()
        self.voxel_Based.set(self.VoxelBased)

        self.propagate = False
        self.Propagate = tk.BooleanVar()
        self.Propagate.set(self.propagate)

        self.groundAll = False
        self.GroundAll = tk.BooleanVar()
        self.GroundAll.set(self.groundAll)

        self.menu3 = tk.Menu(menubar, tearoff = 1, bg = widget_bg)
        menu3_0 = tk.Menu(self.menu3, tearoff = 1, bg = widget_bg)
        self.menu3.add_cascade(label = "Canvas Size ...>", menu = menu3_0)
        menu3_0.add_command(label = "120 x 120", command = lambda: self.set_canvas_size(120, 120))
        menu3_0.add_command(label = "240 x 240", command = lambda: self.set_canvas_size(240, 240))
        menu3_0.add_command(label = "360 x 360", command = lambda: self.set_canvas_size(360, 360))
        menu3_0.add_command(label = "460 x 460", command = lambda: self.set_canvas_size(460, 460))
        menu3_0.add_command(label = "720 x 720", command = lambda: self.set_canvas_size(720, 720))
        menu3_0.add('separator')
        menu3_0.add_command(label = "Set Canvas Size", command = lambda: self.set_canvas_size_dialog())
        self.menu3.add('separator')
        menu3_1 = tk.Menu(self.menu3, tearoff = 1, bg = widget_bg)
        self.menu3.add_cascade(label = "Background / Ground ...>", menu = menu3_1)
        menu3_1.add_command(label = "Set Background pic", command = lambda: self.set_background())
        menu3_1.add_command(label = "Set Background url", command = lambda: self.set_background(url_dialog = True))
        menu3_1.add_command(label = "Refit Background", command = lambda: self.set_background(self.background_filename))
        menu3_1.add('separator')
        menu3_1.add_command(label = "Set Ground pic", command = lambda: self.set_ground_pic())
        menu3_1.add_command(label = "Set Object Ground pic", command = lambda: self.set_ground_pic(sceneLoad = False))
        menu3_1.add_command(label = "Set Ground url", command = lambda: self.set_ground_pic(url_dialog = True))
        menu3_1.add_command(label = "Set Object Ground url", command = lambda: self.set_ground_pic(sceneLoad = False, url_dialog = True))
        menu3_1.add('separator')
        menu3_1.add_command(label = "Clean Ground", command = lambda: self.clean_Ground())
        self.menu3.add("checkbutton", label = "toggle Ground All", onvalue = 1, offvalue = 0, variable = self.GroundAll,
                             command = lambda: self.toggle_GroundAll())
        self.menu3.add_command(label = "toggle Ground", command = lambda: self.toggle_local_Ground())
        self.menu3.add('separator')
        self.menu3.add("checkbutton", label = "Clearcolor compose", onvalue = 1, offvalue = 0, variable = self.clear_color_Compose,
                       command = lambda: self.toggle_clear_color_Compose())
        self.menu3.add("checkbutton", label = "Set Background save", onvalue = 1, offvalue = 0, variable = self.save_Background,
                       command = lambda: self.toggle_save_background())
        self.menu3.add('separator')
        menu3_2 = tk.Menu(self.menu3, tearoff = 1, bg = widget_bg)
        self.menu3.add_cascade(label = "Choose Raster ...>", menu = menu3_2)
        menu3_2.add_command(label = "Choose Raster pic", command = lambda: self.set_raster_pic_dialog())
        menu3_2.add_command(label = "Clean Raster pic", command = lambda: self.clean_raster_pic())
        menu3_2.add_command(label = "Set to loaded pic", command = lambda: self.set_images())
        self.menu3.add('separator')
        self.menu3.add("checkbutton", label = "toggle propagate", onvalue = 1, offvalue = 0, variable = self.Propagate,
                             command = lambda: self.toggle_Propagate())
        self.menu3.add("checkbutton", label = "Voxel Based pic", onvalue = 1, offvalue = 0, variable = self.voxel_Based,
                       command = lambda: self.toggle_Voxel_Based_Pic())
        self.menu3.add('separator')
        menu3_3 = tk.Menu(self.menu3, tearoff = 1, bg = widget_bg)
        self.menu3.add_cascade(label = "Selection ...>", menu = menu3_3)
        menu3_3.add_command(label = "Select Same Image", command = lambda: self.SelectSameImage())
        menu3_3.add_command(label = "Select Highlighted", command = lambda: self.SelectHighlighted())
        menu3_3.add_command(label = "Select Same Highlight", command = lambda: self.select_same_highlight())
        menu3_3.add_command(label = "Select Same Level", command = lambda: self.select_same_level())
        menu3_3.add_command(label = "Select Expand", command = lambda: self.select_expand())
        self.menu3.add('separator')
        self.menu3.add("checkbutton", label = "Use Image Comb", onvalue = 1, offvalue = 0, variable = self.Image_Combo,
                       command = lambda: self.toggle_ImageCombo())
        self.menu3.add('separator')
        menu3_4 = tk.Menu(self.menu3, tearoff = 1, bg = widget_bg)
        self.menu3.add_cascade(label = "Raster pic ...>", menu = menu3_4)
        path = os.path.join(folders, raster_dir)
        menu3_4.add_command(label = "Set Raster pic 1", command = lambda: self.set_raster_pic(path + "/Maailmapunkt_Gray1.png"))
        menu3_4.add_command(label = "Set Raster pic 2", command = lambda: self.set_raster_pic(path + "/Maailmapunkt_Gray1_Raster.png"))
        self.menu3.add('separator')
        menu3_5 = tk.Menu(self.menu3, tearoff = 1, bg = widget_bg)
        self.menu3.add_cascade(label = "Raster / Rotation ...>", menu = menu3_5)
        menu3_5.add_command(label = "Raster random amount", command = lambda: self.set_pic_rotation())
        menu3_5.add("checkbutton", label = "Raster Rotation Comb", onvalue = 1, offvalue = 0, variable = self.rot_Combine,
                       command = lambda: self.set_rotation_combine())
        self.menu3.add('separator')
        self.menu3.configure(tearoffcommand = lambda me, m: self.postmenu(me, m, menu = "self.menu3"))
        self.menu3.bind('<q>', lambda e = None: self.menu_exit())

        menubar.add_cascade(label = "Set Canvas Size", menu = self.menu3)

        self.setColor = True
        self.set_Color = tk.BooleanVar()
        self.set_Color.set(self.setColor)

        self.setShape = True
        self.set_Shape = tk.BooleanVar()
        self.set_Shape.set(self.setShape)

        self.writeKeyFrame = True
        self.write_KeyFrame = tk.BooleanVar()
        self.write_KeyFrame.set(self.writeKeyFrame)

        self.shape_menu = tk.Menu(menubar, tearoff = 1, bg = widget_bg)
        self.shape_menu.add("checkbutton", label = "writeKeyFrame", onvalue = True, offvalue = False, variable = self.write_KeyFrame,
                            command = lambda: self.toggle_write_KeyFrame())
        self.shape_menu.add('separator')
        self.shape_menu.add_command(label = "delete Keyframe", command = self.delete_KeyFrame)
        self.shape_menu.add('separator')
        self.shape_menu.add("checkbutton", label = "setColor", background = "#ee7458", onvalue = True, offvalue = False, variable = self.set_Color,
                            command = lambda: self.toggle_set_Color())
        self.shape_menu.add('separator')
        self.shape_menu.add("checkbutton", label = "setShape", background = "#6f239f", onvalue = True, offvalue = False, variable = self.set_Shape,
                            command = lambda: self.toggle_set_Shape())
        self.shape_menu.add('separator')
        self.shape_menu.add_command(label = "sphere radius 1.0", command = lambda: self.set_shape(radius = 1.0, objects = self.objectList))
        self.shape_menu.add_command(label = "sphere radius 0.5", command = lambda: self.set_shape(radius = 0.5, objects = self.objectList))
        self.shape_menu.add('separator')
        self.shape_menu.add_command(label = "radial shape 1", command = lambda: self.set_shape(shape = 1, objects = self.objectList))
        self.shape_menu.add_command(label = "radial shape 2", command = lambda: self.set_shape(shape = 2, objects = self.objectList))
        self.shape_menu.add('separator')
        self.shape_menu.add_command(label = "shape indexes", command = lambda: self.set_shape(gradient = 0, objects = self.objectList))
        self.shape_menu.add_command(label = "shape x", command = lambda: self.set_shape(gradient = "x", objects = self.objectList))
        self.shape_menu.add_command(label = "shape y", command = lambda: self.set_shape(gradient = "y", objects = self.objectList))
        self.shape_menu.add_command(label = "shape z", command = lambda: self.set_shape(gradient = "z", objects = self.objectList))
        self.shape_menu.add('separator')
        self.shape_menu.configure(tearoffcommand = lambda me, m: self.postmenu(me, m, menu = "self.shape_menu"))
        self.shape_menu.bind('<q>', lambda e = None: self.menu_exit())

        menubar.add_cascade(label = "Set Shapes", menu = self.shape_menu)

        self.neighbours = []
        self.falloff = 0
        self.checkFalloff = tk.IntVar()
        self.checkFalloff.set(0)

        self.menu5 = tk.Menu(menubar, tearoff = 0, bg = widget_bg)
        self.menu5.add("checkbutton", label = "0", onvalue = 0, variable = self.checkFalloff, command = lambda: self.find_neighbours(0))
        self.menu5.add("checkbutton", label = "1", onvalue = 1, variable = self.checkFalloff, command = lambda: self.find_neighbours(1))
        self.menu5.add("checkbutton", label = "2", onvalue = 2, variable = self.checkFalloff, command = lambda: self.find_neighbours(2))
        self.menu5.add("checkbutton", label = "3", onvalue = 3, variable = self.checkFalloff, command = lambda: self.find_neighbours(3))
        self.menu5.add("checkbutton", label = "4", onvalue = 4, variable = self.checkFalloff, command = lambda: self.find_neighbours(4))
        self.menu5.add("checkbutton", label = "5", onvalue = 5, variable = self.checkFalloff, command = lambda: self.find_neighbours(5))
        self.menu5.add("checkbutton", label = "6", onvalue = 6, variable = self.checkFalloff, command = lambda: self.find_neighbours(6))
        self.menu5.add("checkbutton", label = "7", onvalue = 7, variable = self.checkFalloff, command = lambda: self.find_neighbours(7))
        self.menu5.add("checkbutton", label = "8", onvalue = 8, variable = self.checkFalloff, command = lambda: self.find_neighbours(8))
        self.menu5.add("checkbutton", label = "9", onvalue = 9, variable = self.checkFalloff, command = lambda: self.find_neighbours(9))
        self.menu5.add("checkbutton", label = "10", onvalue = 10, variable = self.checkFalloff, command = lambda: self.find_neighbours(10))
        self.menu5.add("checkbutton", label = "11", onvalue = 11, variable = self.checkFalloff, command = lambda: self.find_neighbours(11))
        self.menu5.add("checkbutton", label = "12", onvalue = 12, variable = self.checkFalloff, command = lambda: self.find_neighbours(12))
        self.menu5.add("checkbutton", label = "13", onvalue = 13, variable = self.checkFalloff, command = lambda: self.find_neighbours(13))
        self.menu5.add("checkbutton", label = "14", onvalue = 14, variable = self.checkFalloff, command = lambda: self.find_neighbours(14))
        self.menu5.add("checkbutton", label = "15", onvalue = 15, variable = self.checkFalloff, command = lambda: self.find_neighbours(15))

        menubar.add_cascade(label = "Falloff", menu = self.menu5)

        self.checkMoreLess = 0
        self.check_MoreLess = tk.IntVar()
        self.check_MoreLess.set(self.checkMoreLess)

        self.Zippedspawn = False
        self.Zipped_spawn = tk.BooleanVar()
        self.Zipped_spawn.set(self.Zippedspawn)

        self.menu6 = tk.Menu(menubar, tearoff = 1, bg = widget_bg)
        menu6_0 = tk.Menu(self.menu6, tearoff = 1, bg = widget_bg)
        self.menu6.add_cascade(label = "Arrays / Color ...>", menu = menu6_0)
        menu6_0.add_command(label = "print invisible", command = lambda: self.print_invisible_voxels())
        menu6_0.add_command(label = "print bounds", command = lambda: self.print_bounds(self.objectList))
        menu6_0.add_command(label = "print array", command = lambda: self.print_array())
        menu6_0.add_command(label = "clear color component", command = lambda: self.clear_component_animation(1))
        menu6_0.add_command(label = "clear shape component", command = lambda: self.clear_component_animation(0))
        menu6_0.add_command(label = "setup numpy", command = lambda: self.setup_numpy(self.objectList, force = True))
        menu6_0.add_command(label = "make unique", command = lambda: self.make_unique(self.objectList))
        menu6_0.add_command(label = "arrange animated cube", command = lambda: self.arrange_Animated_Cube())
        self.menu6.add('separator')
        self.menu6.add_command(label = "ask minor level", command = lambda: self.get_minor_level_dialog())
        self.menu6.add("checkbutton", label = "Zipped spawn", onvalue = True, offvalue = False, variable = self.Zipped_spawn,
                             command = lambda: self.toggle_Zippedspawn())
        menu6_1 = tk.Menu(self.menu6, tearoff = 1, bg = widget_bg)
        self.menu6.add_cascade(label = "Truncate voxels ...>", menu = menu6_1)
        menu6_1.add_command(label = "truncate voxels and arrays", command = lambda: self.truncate_voxels_and_arrays())
        menu6_1.add_command(label = "truncate repros", command = lambda: self.truncate_repros())
        menu6_1.add_command(label = "truncate textures", command = lambda: self.truncate_textures())
        self.menu6.add('separator')
        menu6_2 = tk.Menu(self.menu6, tearoff = 1, bg = widget_bg)
        self.menu6.add_cascade(label = "Selection terms ...>", menu = menu6_2)
        menu6_2.add("checkbutton", label = "All", onvalue = 0, variable = self.check_MoreLess, command = lambda: self.toggle_MoreLess(0))
        menu6_2.add("checkbutton", label = "More", onvalue = 1, variable = self.check_MoreLess, command = lambda: self.toggle_MoreLess(1))
        menu6_2.add("checkbutton", label = "Less", onvalue = 2, variable = self.check_MoreLess, command = lambda: self.toggle_MoreLess(2))
        self.menu6.add('separator')
        menu6_3 = tk.Menu(self.menu6, tearoff = 1, bg = widget_bg)
        self.menu6.add_cascade(label = "Select axis ...>", menu = menu6_3)
        menu6_3.add_command(label = "select axis x", command = lambda: self.select_array((1, 0, 0)))
        menu6_3.add_command(label = "select axis y", command = lambda: self.select_array((0, 1, 0)))
        menu6_3.add_command(label = "select axis z", command = lambda: self.select_array((0, 0, 1)))
        self.menu6.add('separator')
        menu6_4 = tk.Menu(self.menu6, tearoff = 1, bg = widget_bg)
        self.menu6.add_cascade(label = "Select level ...>", menu = menu6_4)
        menu6_4.add_command(label = "select level x", command = lambda: self.select_array((0, 1, 1)))
        menu6_4.add_command(label = "select level y", command = lambda: self.select_array((1, 0, 1)))
        menu6_4.add_command(label = "select level z", command = lambda: self.select_array((1, 1, 0)))
        self.menu6.add('separator')
        menu6_5 = tk.Menu(self.menu6, tearoff = 1, bg = widget_bg)
        self.menu6.add_cascade(label = "Select block ...>", menu = menu6_5)
        menu6_5.add_command(label = "select block x", command = lambda: self.select_block((1, 0, 0)))
        menu6_5.add_command(label = "select block y", command = lambda: self.select_block((0, 1, 0)))
        menu6_5.add_command(label = "select block z", command = lambda: self.select_block((0, 0, 1)))
        self.menu6.add('separator')
        self.menu6.configure(tearoffcommand = lambda me, m: self.postmenu(me, m, menu = "self.menu6"))
        self.menu6.bind('<q>', lambda e = None: self.menu_exit())
        menubar.add_cascade(label = "Select array", menu = self.menu6)

        self.files_folder = os.path.join(folders, obj_files)

        self.raster_begin = 0
        self.raster_end = 100
        self.raster_step = 3
        self.raster_revolve = 1

        self.Textures = True
        self.TexturesVar = tk.BooleanVar()
        self.TexturesVar.set(self.Textures)

        self.VoxelBased_repro = False
        self.voxel_Based_repro = tk.BooleanVar()
        self.voxel_Based_repro.set(self.VoxelBased_repro)

        self.useMtl = True
        self.use_Mtl = tk.BooleanVar()
        self.use_Mtl.set(self.useMtl)

        self.fitPlace = False
        self.fit_Place = tk.BooleanVar()
        self.fit_Place.set(self.fitPlace)

        self.useLoaded = True
        self.use_Loaded = tk.BooleanVar()
        self.use_Loaded.set(self.useLoaded)

        self.menu4 = tk.Menu(menubar, tearoff = 1, bg = widget_bg)
        menu4_0 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "Load / Place OBJ ...>", menu = menu4_0)
        menu4_0.add_command(label = "Load OBJ", command = self.load_object)
        menu4_0.add_command(label = "Place OBJ", command = self.place_object)
        menu4_1 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "Place / Revolve OBJ ...>", menu = menu4_1)
        menu4_1.add_command(label = "Place transformed", command = self.place_transformed_object)
        menu4_1.add('separator')
        menu4_1.add_command(label = "Configure Raster", command = self.configure_raster)
        menu4_1.add('separator')
        menu4_1.add_command(label = "Revolve OBJ", command = lambda: self.revolve_OBJ(3))
        menu4_1.add('separator')
        menu4_1.add_command(label = "Play OBJ directory", command = lambda: self.play_OBJ_directory())
        menu4_1.add('separator')
        menu4_1.add_command(label = "Play textures directory", command = lambda: self.play_TEXTURE_directory())
        menu4_1.add('separator')
        menu4_1.add_command(label = "Choose texture", command = self.place_texture)
        self.menu4.add('separator')
        self.menu4.add("checkbutton", label = "Fit Place toggle", onvalue = 1, offvalue = 0, variable = self.fit_Place,
                       command = lambda: self.toggle_fitPlace())
        self.menu4.add('separator')
        self.menu4.add("checkbutton", label = "toggle texture", onvalue = 1, offvalue = 0, variable = self.TexturesVar,
                       command = self.toggle_textures)
        self.menu4.add('separator')
        menu4_2 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "Voxel Texture ...>", menu = menu4_2)
        menu4_2.add_command(label = "Choose voxel texture", command = self.place_voxel_texture)
        menu4_2.add_command(label = "Choose textures", command = self.place_voxel_textures)
        menu4_2.add_command(label = "Choose voxel texture url", command = lambda: self.place_voxel_texture(url_dialog = True))
        self.menu4.add('separator')
        menu4_3 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "Load OBJ Repro ...>", menu = menu4_3)
        menu4_3.add_command(label = "Load OBJ Repro", command = self.load_object_repro)
        menu4_3.add_command(label = "Load OBJ Repros", command = self.load_object_repros)
        menu4_3.add_command(label = "Reload OBJ Repro", command = self.reload_object_repro)
        self.menu4.add('separator')
        menu4_4 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "Animated Repro ...>", menu = menu4_4)
        menu4_4.add_command(label = "Load Animated Repro", command = self.load_animated_repro)
        menu4_4.add_command(label = "Animation oscillate", command = self.animation_oscillate)
        menu4_4.add_command(label = "Randomize Anim", command = self.randomize_animated_repro)
        menu4_4.add_command(label = "Reset Frames", command = self.reset_frames)
        self.menu4.add('separator')
        self.menu4.add("checkbutton", label = "Use mtl data", onvalue = 1, offvalue = 0, variable = self.use_Mtl,
                       command = self.toggle_Mtl_use)
        self.menu4.add("checkbutton", label = "Use loaded", onvalue = 1, offvalue = 0, variable = self.use_Loaded,
                       command = self.toggle_use_Loaded)
        self.menu4.add('separator')
        self.menu4.add_command(label = "About This Voxel", command = self.About_This_Voxel)
        self.menu4.add('separator')
        self.menu4.add("checkbutton", label = "Voxel Based Repro", onvalue = 1, offvalue = 0, variable = self.voxel_Based_repro,
                       command = lambda: self.toggle_Voxel_Based_Repro())
        self.menu4.add('separator')
        menu4_5 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "OBJ / Texture ...>", menu = menu4_5)
        menu4_5.add_command(label = "Clean OBJ Repro", command = lambda: self.clean_repro())
        menu4_5.add_command(label = "Clean Texture", command = lambda: self.clean_texture())
        menu4_5.add_command(label = "Empty Texture", command = lambda: self.empty_texture())
        menu4_5.add_command(label = "Copy OBJ Repro", command = lambda: self.copy_repro())
        menu4_5.add_command(label = "Set to OBJ Repro", command = lambda: self.set_repro())
        self.menu4.add('separator')
        menu4_6 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "OBJ / Texture Select ...>", menu = menu4_6)
        menu4_6.add_command(label = "Select same OBJ", command = lambda: self.SelectSameOBJ())
        menu4_6.add_command(label = "Select same Texture", command = lambda: self.SelectSameTexture())
        self.menu4.add('separator')
        menu4_7 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "Repro Spin ...>", menu = menu4_7)
        menu4_7.add_command(label = "Randomize Amount", command = lambda: self.randomize_spin_amount())
        menu4_7.add_command(label = "Set Spin Amount", command = lambda: self.set_repro_spin_amount())
        menu4_7.add_command(label = "Randomize Spin", command = lambda: self.set_repro_rotation())
        menu4_7.add_command(label = "Set Repro Spin", command = lambda: self.set_repro_spin())
        self.menu4.add('separator')
        menu4_8 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "Repro Wire / Pos ...>", menu = menu4_8)
        menu4_8.add_command(label = "Set Repro Wire Render", command = lambda: self.Set_Repro_Wire_Render())
        menu4_8.add_command(label = "Set Repro WireFrame", command = lambda: self.Set_Repro_Wire_Frame())
        menu4_8.add_command(label = "Set Repro Pos Scale", command = lambda: self.Repro_Pos_Scale_dialog())
        self.menu4.add('separator')
        menu4_9 = tk.Menu(self.menu4, tearoff = 1, bg = widget_bg)
        self.menu4.add_cascade(label = "Print Repros ...>", menu = menu4_9)
        menu4_9.add_command(label = "print voxels repro", command = lambda: self.print_out_voxels_repro(self.current_Object))
        menu4_9.add_command(label = "read voxels repro", command = lambda: self.read_out_voxels_repro(self.current_Object, True))
        self.menu4.configure(tearoffcommand = lambda me, m: self.postmenu(me, m, menu = "self.menu4"))
        self.menu4.bind('<q>', lambda e = None: self.menu_exit())

        menubar.add_cascade(label = "Load OBJ", menu = self.menu4)

        self.specialFlag = 0
        self.special_Flag = tk.IntVar()
        self.special_Flag.set(self.specialFlag)

        self.Flags = [BLEND_ADD, BLEND_SUB, BLEND_MULT, BLEND_MIN, BLEND_MAX]

        self.menu5 = tk.Menu(menubar, tearoff = 0, bg = widget_bg)
        self.menu5.add('separator')
        self.menu5.add_command(label = "Init OBJ Repro", command = self.init_OBJ_repro)
        self.menu5.add('separator')
        self.menu5.add_command(label = "Pack Images", command = self.Pack_Images)
        self.menu5.add('separator')
        self.menu5.add_command(label = "Scene folder", command = lambda: self.open_folder(sceneDir))
        self.menu5.add('separator')
        self.menu5.add_command(label = "DropView Ctrl+o", command = self.open_DragAndDropView)
        self.menu5.add('separator')
        self.menu5.add_command(label = "Help", command = self.setup_help)
        self.menu5.add('separator')
        self.menu5.add_command(label = "About Worldpixel", command = self.about_self)
        self.menu5.add('separator')
        self.menu5.add_command(label = "README.txt", command = self.readme_txt)
        self.menu5.add('separator')
        self.menu5.add("checkbutton", label = "BLEND_ADD", onvalue = 0, variable = self.special_Flag, command = lambda: self.special_flag(0))
        self.menu5.add("checkbutton", label = "BLEND_SUB", onvalue = 1, variable = self.special_Flag, command = lambda: self.special_flag(1))
        self.menu5.add("checkbutton", label = "BLEND_MULT", onvalue = 2, variable = self.special_Flag, command = lambda: self.special_flag(2))
        self.menu5.add("checkbutton", label = "BLEND_MIN", onvalue = 3, variable = self.special_Flag, command = lambda: self.special_flag(3))
        self.menu5.add("checkbutton", label = "BLEND_MAX", onvalue = 4, variable = self.special_Flag, command = lambda: self.special_flag(4))

        menubar.add_cascade(label = "About / Help", menu = self.menu5)

        self.root.config(menu = menubar)

        self.axis_rotation = False
        self.SDL_bind = SDL_bind

        self.f = tk.Frame(master = self.root, bg = widget_bg)
        self.f.pack(side = "top", fill = "x")

        self.embed = tk.Frame(self.f, width = canvas_w, height = canvas_h)

        #
        self.popvoxel = None

        self.embed.bind('<B1-Motion>', self.move_image_position)
        self.embed.bind('<Button-1>', self.down)
        self.embed.bind('<ButtonRelease-1>', self.up)
        self.embed.bind('<Shift_L>', self.shift_press)
        self.embed.bind('<Control_L>', self.control_press)
        self.embed.bind('<KeyRelease>', self.key_release)
        self.embed.bind('<KeyPress>', self.key_down)

        self.embed.bind('<Alt-Left>', lambda e, t = 7: self.canvas_move_keys(t, "left"))
        self.embed.bind('<Alt-Right>', lambda e, t = 7: self.canvas_move_keys(t, "right"))
        self.embed.bind('<Alt-Up>', lambda e, t = 7: self.canvas_move_keys(t, "up"))
        self.embed.bind('<Alt-Down>', lambda e, t = 7: self.canvas_move_keys(t, "down"))

        self.embed.bind('<Alt-Shift-Left>', lambda e, t = 1: self.canvas_move_keys(t, "left"))
        self.embed.bind('<Alt-Shift-Right>', lambda e, t = 1: self.canvas_move_keys(t, "right"))
        self.embed.bind('<Alt-Shift-Up>', lambda e, t = 1: self.canvas_move_keys(t, "up"))
        self.embed.bind('<Alt-Shift-Down>', lambda e, t = 1: self.canvas_move_keys(t, "down"))

        self.embed.bind('<Left>', lambda e: self.move_conform((-self.level.get() * 2.0, 0, 0), [self.current_Object,]))
        self.embed.bind('<Right>', lambda e: self.move_conform((self.level.get() * 2.0, 0, 0), [self.current_Object,]))
        self.embed.bind('<Up>', lambda e: self.move_conform((0, self.level.get() * 2.0, 0), [self.current_Object,]))
        self.embed.bind('<Down>', lambda e: self.move_conform((0, -self.level.get() * 2.0, 0), [self.current_Object,]))
        self.embed.bind('<Delete>', lambda e: self.delete_voxels())
        self.embed.bind('<Control-Delete>', lambda e: self.delete_voxel())

        self.embed.bind('<Insert>', lambda e, v = self.popvoxel: self.insert_voxels(0, [v,]))
        self.embed.bind('<space>', lambda e: self.toggle_Rotation())

        self.embed.bind('<Control-c>', lambda e: self.copy_selection())
        self.embed.bind('<Control-v>', lambda e: self.paste_selection())

        self.embed.bind('<Shift-L>', lambda e: self.toggle_local())
        self.embed.bind('<Shift-F>', lambda e: self.toggle_View("front"))
        self.embed.bind('<Shift-S>', lambda e: self.toggle_View("side"))
        self.embed.bind('<Shift-T>', lambda e: self.toggle_View("top"))

        self.embed.bind('<Shift-A>', lambda e: self.add_positions([self.current_Object,]))
        self.embed.bind('<Shift-R>', lambda e: self.reset_position([self.current_Object,]))
        self.embed.bind('<Shift-O>', lambda e: self.toggle_SDL_Mode())

        self.embed.bind('<Control-n>', lambda e: self.set_scene_name_dialog())
        self.embed.bind('<Control-s>', lambda e: self.save_all_files())
        self.embed.bind('<Control-l>', lambda e: self.load_object_scene())

        self.embed.bind('<Control-Left>', lambda e: self.move_around((-self.level.get(), 0, 0), self.ObjectList))
        self.embed.bind('<Control-Right>', lambda e: self.move_around((self.level.get(), 0, 0), self.ObjectList))
        self.embed.bind('<Control-Up>', lambda e: self.move_around((0, self.level.get(), 0), self.ObjectList))
        self.embed.bind('<Control-Down>', lambda e: self.move_around((0, -self.level.get(), 0), self.ObjectList))
        self.embed.bind('<Shift-Up>', lambda e: self.move_around((0, 0, self.level.get()), self.ObjectList))
        self.embed.bind('<Shift-Down>', lambda e: self.move_around((0, 0, -self.level.get()), self.ObjectList))
        self.embed.bind('<Escape>', lambda e: self.clear_collected(self.objectList))
        self.embed.bind('<Control-i>', lambda e: self.invert_collected(self.ObjectList))
        self.embed.bind('<f>', lambda e: self.find_neighbours(self.falloff))

        self.embed.bind('<plus>', lambda e: self.refine_levels(True))
        self.embed.bind('<minus>', lambda e: self.collect_voxels())

        self.embed.bind('<Control-plus>', lambda e: self.tune_voxels_size(1.1))
        self.embed.bind('<Control-minus>', lambda e: self.tune_voxels_size(0.9))
        self.embed.bind('<Shift-D>', lambda e: self.display_rendered())

        self.embed.bind('<Control-Shift-Z>', lambda e: self.switch_Zoomed())

        self.embed.bind('<l>', lambda e: self.toggle_Lights())
        self.embed.bind('<w>', lambda e: self.toggle_Wire())
        self.embed.bind('<b>', lambda e: self.toggle_Background())
        self.embed.bind('<g>', lambda e: self.toggle_GroundAll())
        self.embed.bind('<p>', lambda e: self.toggle_animation())
        self.embed.bind('<t>', lambda e: self.toggle_textures())
        self.embed.bind('<c>', lambda e: self.toggle_draw_Cube_All())
        self.embed.bind('<s>', lambda e: self.toggle_Shadows())
        self.embed.bind('<d>', lambda e: self.toggle_draft_Mode())
        self.embed.bind('<i>', lambda e: self.goto_Imagefile())
        self.embed.bind('<k>', lambda e: self.select_same_highlight())

        self.embed.bind('<y>', lambda e: self.toggle_Propagate())

        self.embed.bind('<m>', lambda e: self.select_same_level())

        self.embed.bind("0", lambda e: self.toggle_Lightsource(0))
        self.embed.bind("1", lambda e: self.toggle_Lightsource(1))

        self.embed.bind('<Prior>', lambda e: self.scroll_objects(-1))
        self.embed.bind('<Next>', lambda e: self.scroll_objects(1))

        self.embed.bind('<Return>', lambda e: self.write_key_frame())

        self.embed.bind('<Enter>', lambda e, c = self.embed, m = "Set keyboard focus": self.takefocus1(e, c, m))

        self.embed.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')

        self.embed.bind('<<scrollwheel>>', lambda e: self.scroll_embed(e, [self.current_Object,]))

        self.embed.bind('<Motion>', self.mouse_move)

        if platform == 'linux2':
            self.embedbind = Dnd(self.embed, self.drag_to_canvas, self.dnd)
            self.embedbind.bindtarget()
        else:
            self.dnd.bindtarget(self.embed, self.drag_to_canvas, 'text/uri-list')

        self.canvas = tk.Canvas(self.f, width = canvas_w, height = canvas_h, bg = self.background_color)

        self.canvas.grid(row = 0, column = 0, padx = 10, pady = 1, sticky = tk.NW)

        filename = cmd_folder + background_image
        filename = os.path.relpath(filename).replace("\\","/")
        imag1 = Image.open(filename)
        image = ImageTk.PhotoImage(imag1)
        if imag1.mode != 'RGBA':
            imag1 = imag1.convert("RGBA")
        self.backgroundImage = imag1
        (R, G, B, A) = imag1.split()
        self.backgroundAlpha = A
        self.background_Image = image
        self.background_filename = filename
        self.tag = "BackGround"

        filename = cmd_folder + ground_image
        filename = os.path.relpath(filename).replace("\\","/")
        self.groundImage = filename

        self.canvas.create_image(0, 0, image = self.background_Image, anchor = tk.NW, tags = "BackGround")

        img1 = Image.open(rsc_folder + "Cursor/Corner1.PNG")
        img = ImageTk.PhotoImage(img1, 'r')

        self.corner = img

        self.canvas.create_image(canvas_w + offset_2w, canvas_h + offset_2h, image = self.corner, anchor = tk.SE, tags = "Corner")

        self.f2 = tk.Frame(master = self.f, bg = widget_bg)
        self.f2.grid(row = 1, column = 0, padx = 10, pady = 1, sticky = tk.S)

        self.CVar1 = tk.StringVar()
        self.CVar1.set('Welcome to World!')

        self.sentences = [str] * 15
        self.sentences[0] = "None"
        self.sentences[1] = "c * sin((x + y + z) * level + i / pi)"
        self.sentences[2] = "c * cos((x * level - y + level / 2) * pi + i / pi)"
        self.sentences[3] = "c * cos((x * level - 0.5 + level / 2) * pi + i / pi)"
        self.sentences[4] = "c / (cos((x * level - 0.5 + level / 2) * pi + i / pi) + c * dim)"
        self.sentences[5] = "c / (cos((x * level - 0.5 + level / 2) * pi + i / pi) + c * dim * 2)"
        self.sentences[6] = "c * cos((x * level - y + level / 2) * pi + i / pi) * sin((z * level - x + level / 2) * pi + i / pi)"
        self.sentences[7] = "c * cos((x * level - 0.5 + level / 2) * pi + i / pi) * sin((y * level - 0.5 + level / 2) * pi + i / pi * 2)"
        self.sentences[8] = "c / (cos((x * level - 0.5 + level / 2) * pi + i / pi) * sin((y * level - 0.5 + level / 2) * pi + i / pi * 2) + c * dim)"
        self.sentences[9] = "c * cos((x * level - 0.5 + level / 2) * pi + i / pi) * sin((y * level - 0.5 + level / 2) * pi + pi * 2 + i / pi) * sin((z * level - 0.5 + level / 2) * pi + pi * 2 + i / pi)"
        self.sentences[10] = "c / (cos((x * level - 0.5 + level / 2) * pi + i / pi) * sin((y * level - 0.5 + level / 2) * pi + pi * 2 + i / pi) * sin((z * level - 0.5 + level / 2) * pi + pi * 2 + i / pi) + c * dim)"
        self.sentences[11] = "c / (cos((x * level - z + level / 2) * pi + i / pi) * sin((y * level - 0.5 + level / 2) * pi + pi * 2 + i / pi) * sin((z * level - 0.5 + level / 2) * pi + pi * 2 + i / pi) + c * dim)"
        self.sentences[12] = "c * cos(abs(x - (Xdim - 1) / 2.0) * level * pi - i / pi) * cos(abs(y - (Ydim - 1) / 2.0) * level * pi - i / pi) * cos(abs(z - (Zdim - 1) / 2.0) * level * pi - i / pi)"
        self.sentences[13] = "c / (cos(abs(x - (Xdim - 1) / 2.0) * level * pi - i / pi) * cos(abs(y - (Ydim - 1) / 2.0) * level * pi - i / pi) * cos(abs(z - (Zdim - 1) / 2.0) * level * pi - i / pi) + c * dim)"
        self.sentences[14] = "(cos((x - Xdim / 2) + i / float(s[0]) * pi * 2) - sin((y - Ydim / 2) + i / float(s[0]) * pi * 2))/10 + level"

        self.sentence_id = 14

        self.sentence = self.sentences[self.sentence_id]

        self.EntryVar2 = tk.StringVar()
        self.EntryVar2.set(self.sentence)
        self.EntryVar2.trace('w', self.shorten_sentence)

        self.Entry2 = tk.Entry(master = self.f2, textvariable = self.EntryVar2, width = 80, font = self.sans8)
        self.Entry2.grid(row = 0, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Entry2.bind('<Enter>', lambda e, c = self.Entry2, m = "Set animation sentence: x, y, z, i, f, c, level, step, s[]": self.takefocus1(e, c, m))
        self.Entry2.bind('<Return>', lambda e: self.AnimSequence_fill(objects = None))

        self.Entry2.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry2.bind('<<scrollwheel>>', lambda e: self.scroll_Sentence(e))
        self.Entry2.bind('<Up>', lambda e: self.scroll_Sentence(e))
        self.Entry2.bind('<Down>', lambda e: self.scroll_Sentence(e))

        self.Unravelsentences = [str] * 8

        self.Unravelsentences[0] = "unravel_index(int(s_) % L, [Xdim, Ydim, Zdim])"
        self.Unravelsentences[1] = "(i % Xdim, i % Ydim, i % Zdim)"
        self.Unravelsentences[2] = "(r % Xdim, r % Ydim, r % Zdim)"
        self.Unravelsentences[3] = "(sin(r) * Xdim, sin(r) * Ydim, sin(r) * Zdim)"
        self.Unravelsentences[4] = "(sin(r) * Xdim, Ydim / 2, cos(r) * Zdim)"
        self.Unravelsentences[5] = "(Xdim / 2 - 0.5, sin(r) * Ydim / 3.0 + Ydim / 2 - 0.5, cos(r) * Zdim / 3.0 + Zdim / 2 - 0.5)"
        self.Unravelsentences[6] = "(sin(r) * Xdim / 3.0 + Xdim / 2 - 0.5, Ydim / 2 - 0.5, cos(r) * Zdim / 3.0 + Zdim / 2 - 0.5)"
        self.Unravelsentences[7] = "(sin(r) * Xdim / 3.0 + Xdim / 2 - 0.5, cos(r) * Ydim / 3.0 + Ydim / 2 - 0.5, Zdim / 2 - 0.5)"

        self.Unravelsentence_id = 5
        self.Unravelsentence = self.Unravelsentences[self.Unravelsentence_id]

        self.EntryVar_4 = tk.StringVar()
        self.EntryVar_4.set(self.Unravelsentence)
        self.EntryVar_4.trace('w', self.shorten_Unravelsentence)

        self.Entry_4 = tk.Entry(master = self.f2, textvariable = self.EntryVar_4, width = 80, font = self.sans8)
        self.Entry_4.grid(row = 1, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Entry_4.bind('<Enter>', lambda e, c = self.Entry_4, m = "Set unravel sentence: x, y, z, i, s_, r, level, step": self.takefocus1(e, c, m))
        self.Entry_4.bind('<Return>', lambda e: self.AnimSequence_fill(objects = None, unravel = True))

        self.Entry_4.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_4.bind('<<scrollwheel>>', lambda e: self.scroll_UnravelSentence(e))
        self.Entry_4.bind('<Up>', lambda e: self.scroll_UnravelSentence(e))
        self.Entry_4.bind('<Down>', lambda e: self.scroll_UnravelSentence(e))

        self.Vectorsentences = [str] * 5
        self.Vectorsentences[0] = "0, 1, 0"
        self.Vectorsentences[1] = "sin(i / pi), cos(i / pi), 1"
        self.Vectorsentences[2] = "sin(i / 5.0 / pi), 1, cos(i / 5.0 / pi)"
        self.Vectorsentences[3] = "sin(i / 5 / pi), 1, cos(i / 5 / pi)"
        self.Vectorsentences[4] = "sin(i / 5.0 / pi + y * level), 0.1, cos(i / 5.0 / pi + x * level)"

        self.Vectorsentence_id = 4

        self.Vectorsentence = self.Vectorsentences[self.Vectorsentence_id]

        self.EntryVar_3 = tk.StringVar()
        self.EntryVar_3.set(self.Vectorsentence)
        self.EntryVar_3.trace('w', self.shorten_Vectorsentence)

        self.Entry_3 = tk.Entry(master = self.f2, textvariable = self.EntryVar_3, width = 80, font = self.sans8)
        self.Entry_3.grid(row = 2, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Entry_3.bind('<Enter>', lambda e, c = self.Entry_3, m = "Set vector sentence: x, y, z, i, f, c, level, step, s[]": self.takefocus1(e, c, m))
        self.Entry_3.bind('<Return>', lambda e: self.VectorAnimSequence_fill(objects = None))

        self.Entry_3.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_3.bind('<<scrollwheel>>', lambda e: self.scroll_VectorSentence(e))
        self.Entry_3.bind('<Up>', lambda e: self.scroll_VectorSentence(e))
        self.Entry_3.bind('<Down>', lambda e: self.scroll_VectorSentence(e))

        self.CVar2 = tk.StringVar()
        self.CVar2.set('Collection Info!')

        self.status1 = tk.Label(self.f2, textvariable = self.CVar2, width = 60, relief = tk.SUNKEN, bd = 1, font = self.courier10, bg = widget_bg)
        self.status1.grid(row = 3, column = 0, padx = 10, pady = 1, sticky = tk.N)
        self.status1.bind('<Enter>', lambda e, c = self.status1, m = "Collection Info!": self.takefocus1(e, c, m))

        self.CVar3 = tk.StringVar()
        self.CVar3.set('Level data!')

        self.status2 = tk.Label(self.f2, textvariable = self.CVar3, width = 60, relief = tk.SUNKEN, bd = 1, font = self.courier10, bg = widget_bg)
        self.status2.grid(row = 4, column = 0, padx = 10, pady = 1, sticky = tk.N)
        self.status2.bind('<Enter>', lambda e, c = self.status2, m = "Level data!": self.takefocus1(e, c, m))

        self.CVar4 = tk.StringVar()
        self.CVar4.set('Animation data!')

        self.status3 = tk.Label(self.f2, textvariable = self.CVar4, width = 60, relief = tk.SUNKEN, bd = 1, font = self.courier10, bg = widget_bg)
        self.status3.grid(row = 5, column = 0, padx = 10, pady = 1, sticky = tk.N)
        self.status3.bind('<Enter>', lambda e, c = self.status3, m = "Animation data!": self.takefocus1(e, c, m))

        self.f1 = tk.Frame(master = self.f, bg = widget_bg)
        self.f1.grid(row = 0, rowspan = 2, column = 1, padx = 10, pady = 1, sticky = tk.N)

        self.Dim = 4
        self.Voxel = 0

        self.EntryVar0 = tk.StringVar()
        self.EntryVar0.set("4 1")
        self.EntryVar0.trace('w', self.shorten_entry_0)

        #
        self.Entry0 = tk.Entry(master = self.f1, textvariable = self.EntryVar0, width = 10, font = self.sans8)
        self.Entry0.grid(row = 1, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Entry0.bind('<Enter>', lambda e, c = self.Entry0, m = "Set current 3d Voxel": self.takefocus3(e, c, m))
        self.Entry0.bind('<Return>', lambda e: self.update_entry_0(0, 0, 0))

        self.Entry0.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry0.bind('<<scrollwheel>>', lambda e: self.scroll_entry0(e))
        self.Entry0.bind('<Up>', lambda e: self.scroll_entry0(e))
        self.Entry0.bind('<Down>', lambda e: self.scroll_entry0(e))
        #

        self.currentVoxel = 0
        self.EntryVar1 = tk.StringVar()
        self.EntryVar1.set(str(self.currentVoxel))
        self.EntryVar1.trace('w', self.shorten_entry_1)

        self.Entry1 = tk.Entry(master = self.f1, textvariable = self.EntryVar1, width = 10, font = self.sans8)
        self.Entry1.grid(row = 2, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Entry1.bind('<Enter>', lambda e, c = self.Entry1, m = "Set current 3d Voxel": self.takefocus2(e, c, m))

        self.Entry1.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry1.bind('<<scrollwheel>>', lambda e: self.scroll_entry(e))
        self.Entry1.bind('<Return>', lambda e: self.shorten_entry_1(0, 0, 0))

        self.vector_string = "1 1 0"
        self.previousVector = None
        self.EntryVar = tk.StringVar()
        self.EntryVar.set(self.vector_string)
        self.EntryVar.trace('w', self.shorten_entry)

        self.Entry = tk.Entry(master = self.f1, textvariable = self.EntryVar, width = 10, font = self.sans8)
        self.Entry.grid(row = 3, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Entry.bind('<Enter>', lambda e, c = self.Entry, m = "Set rotation vector3d": self.takefocus1(e, c, m))
        self.Entry.bind('<Return>', lambda e: self.update_object_frame(self.objectList))

        self.coords = (0.0, 0.0, 0.0)
        self.coord_string = "0.0 0.0 0.0"
        self.EntryVar5 = tk.StringVar()
        self.EntryVar5.set(self.coord_string)
        self.EntryVar5.trace('w', self.shorten_entry_5)

        self.Entry5 = tk.Entry(master = self.f1, textvariable = self.EntryVar5, width = 30, font = self.sans8)
        self.Entry5.grid(row = 4, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Entry5.bind('<Enter>', lambda e, c = self.Entry5, m = "Set coordinates": self.takefocus1(e, c, m))
        self.Entry5.bind('<Return>', lambda e: self.update_coord_string(self.objectList))

        self.Entry5.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry5.bind('<<scrollwheel>>', lambda e: self.scroll_entry5(e))
        self.Entry5.bind('<Up>', lambda e: self.scroll_entry5(e))
        self.Entry5.bind('<Down>', lambda e: self.scroll_entry5(e))

        self.currentFrame = 0
        self.EntryVar3 = tk.StringVar()
        self.EntryVar3.set(str(self.currentFrame))
        self.EntryVar3.trace('w', self.shorten_entry_3)

        self.Entry3 = tk.Entry(master = self.f1, textvariable = self.EntryVar3, width = 10, font = self.sans8)
        self.Entry3.grid(row = 5, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Entry3.bind('<Enter>', lambda e, c = self.Entry3, m = "Set animation frame": self.takefocus1(e, c, m))
        self.Entry3.bind('<Return>', lambda e: self.shorten_entry_3(0, 0, 0))

        self.Entry3.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry3.bind('<<scrollwheel>>', lambda e: self.scroll_entry3(e))

        self.angle = 0
        self.c_baked = None

        self.idle_done = True
        self.animation_frames_done = True
        self.rotation_way = "axis"
        self.vector = (1, 1, 0)

        self.backup_angle = 0

        self.EntryVar4 = tk.StringVar()
        self.EntryVar4.set(str(rad2deg(self.angle)))
        self.EntryVar4.trace('w', self.shorten_entry_4)

        self.Entry4 = tk.Entry(master = self.f1, textvariable = self.EntryVar4, width = 10, font = self.sans8)
        self.Entry4.grid(row = 6, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Entry4.bind('<Enter>', lambda e, c = self.Entry4, m = "Set rotation": self.takefocus1(e, c, m))

        self.Entry4.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry4.bind('<<scrollwheel>>', lambda e: self.scroll_entry4(e))
        self.Entry4.bind('<Return>', lambda e: self.shorten_entry_4(0, 0, 0))

        self.Button = tk.Button(master = self.f1, text = "spawn 0", command = lambda: self.spawn_voxels(), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button.grid(row = 7, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Spawn selected voxel."))

        self.Button1 = tk.Button(master = self.f1, text = "collect 0", command = lambda: self.collect_voxels(), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button1.grid(row = 8, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button1.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Collect selected voxel."))

        self.Button2 = tk.Button(master = self.f1, text = "highlight", command = lambda: self.highlight_voxels(), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button2.grid(row = 9, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button2.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Highlight tree."))

        self.Button3 = tk.Button(master = self.f1, text = "collapse", command = lambda: self.collapse_highlighted_voxels(), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button3.grid(row = 10, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button3.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Collapse collected."))

        self.Button4 = tk.Button(master = self.f1, text = "raise levels", command = lambda: self.raise_levels(), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button4.grid(row = 11, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button4.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Raise levels to highlighted level."))

        self.Button5 = tk.Button(master = self.f1, text = "refine", command = lambda: self.refine_levels(), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button5.grid(row = 12, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button5.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Refine collected to highlighted level."))

        self.Button6 = tk.Button(master = self.f1, text = "select all", command = lambda: self.select_all([self.current_Object,]), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button6.grid(row = 13, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button6.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Select all for collected."))

        self.Button7 = tk.Button(master = self.f1, text = "select closest", command = lambda: self.select_closest(self.objectList), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button7.grid(row = 14, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button7.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Select closest."))

        self.Button8 = tk.Button(master = self.f1, text = "clear collected", command = lambda: self.clear_collected(self.objectList), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button8.grid(row = 15, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button8.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Clear collected."))

        self.Button9 = tk.Button(master = self.f1, text = "refine below", command = lambda: self.refine_levels(True), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button9.grid(row = 16, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button9.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Refine highlighted level below."))

        self.Button10 = tk.Button(master = self.f1, text = "select super", command = lambda: self.select_super(self.objectList), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button10.grid(row = 17, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button10.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Select super 3d voxel."))

##        self.Button11 = tk.Button(master = self.f1, text = "select collected", command = lambda: self.highlight_collection(self.objectList), width = 20,
##                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
##        self.Button11.grid(row = 16, column = 0, padx = 1, pady = 1, sticky = tk.N)
##        self.Button11.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Select 3d voxels in collection."))

        self.Button12 = tk.Button(master = self.f1, text = "select child voxel", command = lambda: self.select_child_voxel(self.objectList), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button12.grid(row = 18, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button12.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Select child 3d voxel."))

        self.Button13 = tk.Button(master = self.f1, text = "invert collected", command = lambda: self.invert_collected(self.objectList), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button13.grid(row = 19, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button13.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Invert collected."))

        self.Button14 = tk.Button(master = self.f1, text = "highlight slice", command = lambda: self.highlight_slice(self.objectList), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button14.grid(row = 20, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button14.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Highlight slice."))

        self.Button15 = tk.Button(master = self.f1, text = "voxel spawned", command = lambda: self.voxel_spawned(), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button15.grid(row = 21, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button15.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Toggle voxel spawned."))

        self.Button16 = tk.Button(master = self.f1, text = "clear highlight", command = lambda: self.clear_highlight(), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button16.grid(row = 22, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button16.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Clear voxel highlight."))

        self.Button17 = tk.Button(master = self.f1, text = "select child voxels", command = lambda: self.select_child_voxels(self.objectList, True), width = 20, height = button_height,
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        self.Button17.grid(row = 23, column = 0, padx = 1, pady = 1, sticky = tk.N)
        self.Button17.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Select child 3d voxel."))

        self.Depth_factor = tk.DoubleVar()
        self.Depth_factor.set(depth_factor)

        self.Depth = depth_factor

        self.scale1 = tk.Scale(master = self.f1, from_= 0, to=5, resolution = 0.1, var = self.Depth_factor, label = "Depth",
                               command = self.update_depth_factor, bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag)
        self.scale1.grid(row = 1, column = 1, rowspan = 5, padx = 10)
        self.scale1.bind('<Enter>', lambda e, c = self.scale1, m = "Depth factor.": self.takefocus1(e, c, m))

        self.scale1.bind('<Up>', lambda e, c = self.Depth: self.adjustDepth(e, c, -0.1))
        self.scale1.bind('<Down>', lambda e, c = self.Depth: self.adjustDepth(e, c, 0.1))

        self.scale1.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')

        self.scale1.bind('<<scrollwheel>>', lambda e: self.scroll_depth(e))

        self.Scale_factor = tk.DoubleVar()
        self.Scale_factor.set(scale_factor)

        self.Scale = scale_factor

        self.scale2 = tk.Scale(master = self.f1, from_= 3, to=0, resolution = 0.05, var = self.Scale_factor, label = "Scale",
                               command = lambda e: self.update_scale_factor(self.objectList), bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag)
        self.scale2.grid(row = 6, column = 1, rowspan = 5, padx = 10)
        self.scale2.bind('<Enter>', lambda e, c = self.scale2, m = "Scale factor.": self.takefocus1(e, c, m))

        self.scale2.bind('<Return>', lambda e: self.write_key_frame())

        self.scale2.bind('<Up>', lambda e, c = self.Scale: self.adjustScale(e, c, -0.05))
        self.scale2.bind('<Down>', lambda e, c = self.Scale: self.adjustScale(e, c, 0.05))

        self.scale2.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')

        self.scale2.bind('<<scrollwheel>>', lambda e: self.scroll_scale(e, [self.current_Object,]))

        # anim pane at row 11 with span 10 and width 120

        self.animpane = navigator.animation3d(master = self.f1, row = 11, column = 1, rowspan = 13,
                                              bg = self.background_color, CVar1 = self.CVar1,
                                              transformed_func = self.place_transformed_object,
                                              scroll_time = self.scroll_time)
        if platform == 'linux2':
            self.animpanebind = Dnd(self.animpane.canvas, self.drag_to_animpane, self.dnd)
            self.animpanebind.bindtarget()
        else:
            self.dnd.bindtarget(self.animpane.canvas, self.drag_to_animpane, 'text/uri-list')

        # --- color 1

        self.bgcolor = (23, 98, 129)
        self.fgcolor = (244, 224, 15)
        self.bgcolor1 = (0, 0, 0)
        self.fgcolor1 = (255, 255, 255)

        self.f5 = tk.Frame(master = self.f1, bg = widget_bg)
        self.f5.grid(row = 0, column = 0, columnspan = 2, padx = 0, sticky = tk.NW)

        self.EntryVar_1 = tk.StringVar()
        self.EntryVar_1.set('#176281')

        self.EntryVar_2 = tk.StringVar()
        self.EntryVar_2.set('#f4e00f')

        self.AlphaEntryVar1 = tk.IntVar()
        self.AlphaEntryVar1.set(255)

        self.AlphaEntryVar2 = tk.IntVar()
        self.AlphaEntryVar2.set(255)

        self.f6 = tk.Frame(master = self.f5, bg = widget_bg)
        self.f6.grid(row = 0, column = 0, columnspan = 8, padx = 0, pady = 0, sticky = tk.NW)

        self.alphaentry1 = tk.Entry(master = self.f6, textvariable = self.AlphaEntryVar1, width = 3, highlightbackground = widget_hg)
        self.alphaentry1.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = tk.NW)
        self.alphaentry1.bind('<Return>', lambda e: self.alpha1_set())
        self.alphaentry1.bind('<Enter>', lambda e, c = self.alphaentry1, m = "Hit Enter to set bg alpha": self.takefocus1(e, c, m))
        self.alphaentry1.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')

        self.alphaentry1.bind('<<scrollwheel>>', lambda e, t = 1: self.scroll_alpha(e, t))

        self.colorentry1 = tk.Entry(master = self.f6, textvariable = self.EntryVar_1, width = 7, highlightbackground = widget_hg)
        self.colorentry1.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = tk.NW)
        self.colorentry1.bind('<Return>', lambda e: self.color1_set(e))
        self.colorentry1.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Hit Enter to set color"))

        self.color1 = tk.Canvas(master = self.f6, width = strip_H + 20, height = 16, bg = '#176281', highlightbackground = widget_hg)
        self.color1.grid(row = 0, column = 2, padx = 0, pady = 0, sticky = tk.W)
        self.color1.bind('<ButtonRelease-1>', lambda e: self.color_get1(e))
        self.color1.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Click to place color into string and bg font choise."))
        self.color1.bind('<Button-1>', lambda e: self.mouse_move_set(e, 1))
        self.color1.bind('<B1-Motion>', lambda e: self.mouse_move_color(e, 1))
        self.color1.create_text(10, 1, text = "#176281", font = self.sans8, anchor = tk.NW, tag = 'color', activefill = '#ffffff')

        self.alphaentry2 = tk.Entry(master = self.f6, textvariable = self.AlphaEntryVar2, width = 3, highlightbackground = widget_hg)
        self.alphaentry2.grid(row = 0, column = 3, padx = 0, pady = 0, sticky = tk.NW)
        self.alphaentry2.bind('<Return>', lambda e: self.alpha2_set())
        self.alphaentry2.bind('<Enter>', lambda e, c = self.alphaentry2, m = "Hit Enter to set fg alpha": self.takefocus1(e, c, m))
        self.alphaentry2.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')

        self.alphaentry2.bind('<<scrollwheel>>', lambda e, t = 2: self.scroll_alpha(e, t))

        self.colorentry2 = tk.Entry(master = self.f6, textvariable = self.EntryVar_2, width = 7, highlightbackground = widget_hg)
        self.colorentry2.grid(row = 0, column = 4, padx = 0, pady = 0, sticky = tk.NW)
        self.colorentry2.bind('<Return>', lambda e: self.color2_set(e))
        self.colorentry2.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Hit Enter to set color"))

        self.color2 = tk.Canvas(master = self.f6, width = strip_H + 20, height = 16, bg = '#f4e00f', highlightbackground = widget_hg)
        self.color2.grid(row = 0, column = 5, padx = 0, pady = 0, sticky = tk.W)
        self.color2.bind('<ButtonRelease-1>', lambda e: self.color_get2(e))
        self.color2.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Click to place color into string and fg font choise."))
        self.color2.bind('<Button-1>', lambda e: self.mouse_move_set(e, 2))
        self.color2.bind('<B1-Motion>', lambda e: self.mouse_move_color(e, 2))
        self.color2.create_text(10, 1, text = "#f4e00f", font = self.sans8, anchor = tk.NW, tag = 'color1', activefill = '#ffffff')

        colorpalette_left = tk.Button(master = self.f6, text = "left", image = self.left_palette, command = lambda: self.scroll_palette('left'),
                                      bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        colorpalette_left.grid(row = 0, column = 6, padx = 0, pady = 0, sticky = tk.W)
        colorpalette_left.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Scroll palettes left."))

        colorpalette_right = tk.Button(master = self.f6, text = "right", image = self.right_palette, command = lambda: self.scroll_palette('right'),
                                       bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag, font = sserif7)
        colorpalette_right.grid(row = 0, column = 7, padx = 0, pady = 0, sticky = tk.W)
        colorpalette_right.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Scroll palettes right."))

        self.color = tk.Canvas(master = self.f5, width = strip_H * 7, height = 48, bg = 'red', highlightbackground = widget_hg)
        self.color.grid(row = 1, column = 0, columnspan = 8, padx = 0, pady = 0, sticky = tk.NW)
        self.color.bind('<ButtonRelease-1>', lambda e: self.color_get(e))
        self.color.bind('<Enter>', lambda e, y = self.enter_button: y(e, "Left and Right Mouse Over Colors"))

        self.color_font1(self.EntryVar_1.get(), 'color')
        self.color_font2(self.EntryVar_2.get(), 'color1')

        '''
        self.colorbar1 = [None] * 7

        self.colorbar1[0] = colorbar1('(R, G, b)', '(R, G, B)')
        self.colorbar1[1] = colorbar1('(b, R, G)', '(R, G, B)')
        self.colorbar1[2] = colorbar1('(G, b, R)', '(R, G, B)')
        self.colorbar1[3] = colorbar1('(r, g, b)', '(R, G, B)')
        self.colorbar1[4] = colorbar1('(b, R, G)', '(G, B, R)')
        self.colorbar1[5] = colorbar1('(G, b, R)', '(G, B, R)')
        self.colorbar1[6] = colorbar1('(R, G, b)', '(B, R, G)')
        '''

        self.colorbar = [None] * 7
        '''
        def construct_colorbar():
            for i in range(0, len(self.colorbar)):
                self.colorbar[i] = colorbar()

        def create_colorbar():
            for i in range(0, len(self.colorbar)):
                self.color.create_image(strip_W * i + 2, 0, anchor = tk.NW, image = self.colorbar[i].img, tags = 'col' + str(i))
        '''
        self.construct_colorbar()
        self.create_colorbar()

        self.cursor = cursor("Cursor")
        self.cursorFG = cursor("Cursor")

        self.color.create_image(strip_H / 2, strip_W / 2, image = self.cursor.img, tags = 'col7')
        self.color.create_image(strip_H / 2 + 10, strip_W / 2 + 10, image = self.cursorFG.img, tags = 'col8')

        self.color.bind('<Left>', lambda e, x = -10, y = 0: self.cursor_move_keys(e, x, y))
        self.color.bind('<Right>', lambda e, x = 10, y = 0: self.cursor_move_keys(e, x, y))
        self.color.bind('<Up>', lambda e, x = 0, y = -10: self.cursor_move_keys(e, x, y))
        self.color.bind('<Down>', lambda e, x = 0, y = 10: self.cursor_move_keys(e, x, y))
        self.color.bind('<Button-1>', lambda e, c = 7: self.cursor_set(e, c))
        self.color.bind('<Button-3>', lambda e, c = 7: self.cursor_set1(e, c))
        self.color.bind('<B1-Motion>', lambda e, c = 7: self.cursor_move(e, c))
        self.color.bind('<B3-Motion>', lambda e, c = 7: self.cursor_move1(e, c))
        self.color.bind('<p>', lambda e, c = 7: self.cursor_tab(e, c))
        self.color.bind('<n>', lambda e, c = 7: self.cursor_tab1(e, c))
        self.color.bind('<v>', lambda e: self.switch_colors())
        self.color.bind('<b>', lambda e: self.switch_black_white())
        self.color.bind('<u>', lambda e: self.load_backup_frame())
        self.color.bind('<i>', lambda e: self.create_backup_frame())
        self.color.bind('<Enter>', lambda e, c = self.color,
                        m = "Use p to place fg color into fg color slot. Right-click for fg colors, v to switch, b for black / white, u to undo": self.takefocus1(e, c, m))

        # --- color 2

        self.view_rect_2d = rect_2d()

        self.Screen, object1, object2, object3, object4, v = init_objects(self.pic_image)

        self.image = self.Screen[0]

        self.Screen.createBackgroundSurface(self.backgroundImage)


        if self.SDL_bind:
            os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())
            if platform == 'linux2':
                os.environ['SDL_VIDEODRIVER'] = 'x11'
            else:
                os.environ['SDL_VIDEODRIVER'] = 'windib'
            self.Screen.setup_SDL(self.Depth)
        else:
            self.screen = ImageTk.PhotoImage(self.image, 'r')

        self.Animation = [None, None, None, None]
        self.Animation_pick = [None, None, None, None]
        self.VectorAnimation = [None, None, None, None]
        self.VectorAnimation_pick = [None, None, None, None]

        self.local1 = currentObject(o = object1)
        self.local2 = currentObject(o = object2)
        self.local3 = currentObject(o = object3)
        self.local4 = currentObject(o = object4)

        self.current_Object = self.local1

        self.ObjectList = [self.local1, self.local2, self.local3, self.local4]
        self.ObjectIndexList = [self.local1.index(), self.local2.index(), self.local3.index(), self.local4.index()]

        self.objectList = [self.local1]
        self.validate_Local()
        self.current_Object[self.currentVoxel].spawn_recursive(0.25)
        self.local2[0].spawn_recursive(0.25)
        self.local3[0].spawn_recursive(0.5)
        self.local4[0].spawn_recursive(0.5)
        self.center = (self.current_Object.center())
        self.update_object_frame(self.objectList)

        self.controlDown = False
        self.shiftDown = False

        self.canvas.bind('<B1-Motion>', self.move_image_position)
        self.canvas.bind('<Button-1>', self.down)
        self.canvas.bind('<ButtonRelease-1>', self.up)
        self.canvas.bind('<Shift_L>', self.shift_press)
        self.canvas.bind('<Control_L>', self.control_press)
        self.canvas.bind('<KeyRelease>', self.key_release)
        self.canvas.bind('<KeyPress>', self.key_down)

        self.canvas.bind('<Alt-Left>', lambda e, t = 7: self.canvas_move_keys(t, "left"))
        self.canvas.bind('<Alt-Right>', lambda e, t = 7: self.canvas_move_keys(t, "right"))
        self.canvas.bind('<Alt-Up>', lambda e, t = 7: self.canvas_move_keys(t, "up"))
        self.canvas.bind('<Alt-Down>', lambda e, t = 7: self.canvas_move_keys(t, "down"))

        self.canvas.bind('<Alt-Shift-Left>', lambda e, t = 1: self.canvas_move_keys(t, "left"))
        self.canvas.bind('<Alt-Shift-Right>', lambda e, t = 1: self.canvas_move_keys(t, "right"))
        self.canvas.bind('<Alt-Shift-Up>', lambda e, t = 1: self.canvas_move_keys(t, "up"))
        self.canvas.bind('<Alt-Shift-Down>', lambda e, t = 1: self.canvas_move_keys(t, "down"))

        self.canvas.bind('<Left>', lambda e: self.move_conform((-self.level.get() * 2.0, 0, 0), [self.current_Object,]))
        self.canvas.bind('<Right>', lambda e: self.move_conform((self.level.get() * 2.0, 0, 0), [self.current_Object,]))
        self.canvas.bind('<Up>', lambda e: self.move_conform((0, self.level.get() * 2.0, 0), [self.current_Object,]))
        self.canvas.bind('<Down>', lambda e: self.move_conform((0, -self.level.get() * 2.0, 0), [self.current_Object,]))
        self.canvas.bind('<Delete>', lambda e: self.delete_voxels())
        self.canvas.bind('<Control-Delete>', lambda e: self.delete_voxel())

        self.canvas.bind('<Insert>', lambda e, v = self.popvoxel: self.insert_voxels(0, [v,]))
        self.canvas.bind('<space>', lambda e: self.toggle_Rotation())

        self.canvas.bind('<Control-c>', lambda e: self.copy_selection())
        self.canvas.bind('<Control-v>', lambda e: self.paste_selection())

        self.canvas.bind('<Shift-L>', lambda e: self.toggle_local())
        self.canvas.bind('<Shift-F>', lambda e: self.toggle_View("front"))
        self.canvas.bind('<Shift-S>', lambda e: self.toggle_View("side"))
        self.canvas.bind('<Shift-T>', lambda e: self.toggle_View("top"))

        self.canvas.bind('<Shift-A>', lambda e: self.add_positions([self.current_Object,]))
        self.canvas.bind('<Shift-R>', lambda e: self.reset_position([self.current_Object,]))
        self.canvas.bind('<Shift-O>', lambda e: self.toggle_SDL_Mode())

        self.canvas.bind('<Control-n>', lambda e: self.set_scene_name_dialog())
        self.canvas.bind('<Control-s>', lambda e: self.save_all_files())
        self.canvas.bind('<Control-l>', lambda e: self.load_object_scene())

        self.canvas.bind('<Control-Left>', lambda e: self.move_around((-self.level.get(), 0, 0), self.ObjectList))
        self.canvas.bind('<Control-Right>', lambda e: self.move_around((self.level.get(), 0, 0), self.ObjectList))
        self.canvas.bind('<Control-Up>', lambda e: self.move_around((0, self.level.get(), 0), self.ObjectList))
        self.canvas.bind('<Control-Down>', lambda e: self.move_around((0, -self.level.get(), 0), self.ObjectList))
        self.canvas.bind('<Shift-Up>', lambda e: self.move_around((0, 0, self.level.get()), self.ObjectList))
        self.canvas.bind('<Shift-Down>', lambda e: self.move_around((0, 0, -self.level.get()), self.ObjectList))
        self.canvas.bind('<Escape>', lambda e: self.clear_collected(self.objectList))
        self.canvas.bind('<Control-i>', lambda e: self.invert_collected(self.ObjectList))
        self.canvas.bind('<f>', lambda e: self.find_neighbours(self.falloff))

        self.canvas.bind('<plus>', lambda e: self.refine_levels(True))
        self.canvas.bind('<minus>', lambda e: self.collect_voxels())

        self.canvas.bind('<Control-plus>', lambda e: self.tune_voxels_size(1.1))
        self.canvas.bind('<Control-minus>', lambda e: self.tune_voxels_size(0.9))
        self.canvas.bind('<Shift-D>', lambda e: self.display_rendered())

        self.canvas.bind('<Control-Shift-Z>', lambda e: self.switch_Zoomed())

        self.canvas.bind('<g>', lambda e: self.toggle_GroundAll())
        self.canvas.bind('<b>', lambda e: self.toggle_Background())
        self.canvas.bind('<p>', lambda e: self.toggle_animation())
        self.canvas.bind('<c>', lambda e: self.toggle_draw_Cube_All())
        self.canvas.bind('<s>', lambda e: self.toggle_Shadows())
        self.canvas.bind('<d>', lambda e: self.toggle_draft_Mode())
        self.canvas.bind('<i>', lambda e: self.goto_Imagefile())
        self.canvas.bind('<k>', lambda e: self.select_same_highlight())

        self.canvas.bind('<y>', lambda e: self.toggle_Propagate())

        self.canvas.bind('<Prior>', lambda e: self.scroll_objects(-1))
        self.canvas.bind('<Next>', lambda e: self.scroll_objects(1))

        self.canvas.bind('<m>', lambda e: self.select_same_level())

        self.canvas.bind('<Return>', lambda e: self.write_key_frame())

        self.canvas.bind('<Enter>', lambda e, c = self.canvas, m = "Set keyboard focus": self.takefocus1(e, c, m))

        self.canvas.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')

        self.canvas.bind('<<scrollwheel>>', lambda e: self.scroll_embed(e, [self.current_Object,]))

        self.canvas.bind('<Motion>', self.mouse_move)

        if platform == 'linux2':
            self.canvasbind = Dnd(self.canvas, self.drag_to_canvas, self.dnd)
            self.canvasbind.bindtarget()
        else:
            self.dnd.bindtarget(self.canvas, self.drag_to_canvas, 'text/uri-list')

        self.highlight_mouse = False

        self.collected = None

        self.coords_collected = None

        self.time = 0.0

        self.f3 = tk.Frame(master = self.root, bg = widget_bg)
        self.f3.pack(side = "bottom", fill = "x")

        self.Time = 0

        self.Time_factor = tk.IntVar()
        self.Time_factor.set(self.Time)

        self.scale3 = tk.Scale(master = self.f3, from_= 0, to = timeticks, resolution = 1, var = self.Time_factor,
                               command = lambda e: self.update_time_factor(), bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg,
                               activebackground = widget_ag, orient = tk.HORIZONTAL, tickinterval = 10)
        self.scale3.pack(side = "bottom", fill = "x")
        self.scale3.bind('<Enter>', lambda e, c = self.scale3,
                         m = "Timeline, 's' - write keyframe, enter / g - goto frame, scroll to the frame, p - play frames": self.takefocus1(e, c, m))

        self.scale3.bind('<Left>', lambda e, c = self.Time: self.adjustTime(e, c, -1))
        self.scale3.bind('<Right>', lambda e, c = self.Time: self.adjustTime(e, c, 1))

        self.scale3.bind('<Control-c>', lambda e: self.copy_keyframe(self.Time))
        self.scale3.bind('<Control-v>', lambda e: self.paste_keyframe(self.Time))

        self.time_keyed = {}
        self.keyframes = []
        self.time_list = []

        self.scale3.bind('<s>', lambda e: self.write_key_frame())
        self.scale3.bind('<p>', lambda e: self.load_key_frames_into_AnimSequence())
        self.scale3.bind('<g>', lambda e: self.goto_frame())

        self.scale3.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.scale3.bind('<<scrollwheel>>', lambda e: self.scroll_time(e))
        self.scale3.bind('<Return>', lambda e: self.goto_animation_entry())

        self.f4 = tk.Frame(master = self.f3, bg = widget_bg, padx = 19, pady = 0, height = 20)
        self.f4.pack(side = "bottom", fill = "x")

        self.status = tk.Label(self.f3, textvariable = self.CVar1, width = 40, relief = tk.SUNKEN, bd = 1, font = self.courier10, bg = widget_bg)
        self.status.pack(side = "bottom", fill = "x")

        self.repro = None
        self.OBJ_repro = None

        self.texture = None
        self.texName = None

        self.empty_background()

        self.faces = []

        self.obj_transform = None

        self.objtransformList = {}

        self.colorvariation = tk.IntVar()

        self.colorvariation.set(1)

        self.colorvariation.trace("w", self.trace_color)

        self.set_parent_vectors((1, 1, 0))

#        self.canvas.focus_set()

        self.animpane.initarea()

        self.get_dimension()

        self.create_backup_frame()

        self.AnimSequence_fill(self.objectList, frame_go = False)

        self.Vector_Animation_fill(self.objectList, write = False)

        self.load_object(os.path.join(folders, obj_files, "ImagePlane.obj"))

        #self.init_OBJ_repro()

        self.root.mainloop()

        self.start()

    def toggle_local(self):
        self.localCenter = not self.localCenter
        self.local_Center.set(self.localCenter)
        self.toggle_local_Center()

    def remove_object(self, update = True):
        if len(self.ObjectList) > 4:
            if self.localCenter:
                self.local_Center.set(False)
                self.toggle_local_Center(False)

            n = len(self.ObjectList)
            n += 1
            local = self.current_Object

            if self.objectList:
                self.current_Object = self.objectList[0]
            self.currentVoxel = 0

            self.Animation.pop()
            self.Animation_pick.pop()

            self.VectorAnimation.pop()
            self.VectorAnimation_pick.pop()

            if self.ObjectList[-1] in self.objectList:
                self.objectList.pop(self.objectList.index(self.ObjectList[-1]))

            self.ObjectList.pop()
            self.ObjectIndexList.pop()

            self.Local.pop()

            self.menu1_1.delete(len(self.ObjectList) + 5)

            if update:

                self.validate_Local()
                self.sync_VoxelDim()
                self.update_object_frame(self.objectList)

    def append_object(self, update = True):
        if self.localCenter:
            self.local_Center.set(False)
            self.toggle_local_Center(False)

        n = len(self.ObjectList)
        n += 1
        name = "object" + str(n)
        pic_index = -n
        object1, v = init_object((0, 0, 0), name, pic_index)

        local = currentObject(o = object1)

        local.set_depth(self.Depth)
        local.set_draw_Cube(self.drawCube)

        self.current_Object = local

        self.Animation.append(None)
        self.Animation_pick.append(None)

        self.VectorAnimation.append(None)
        self.VectorAnimation_pick.append(None)

        self.ObjectList.append(local)
        self.ObjectIndexList.append(local.index())

        self.objectList.insert(0, local)

        self.Local.append(tk.BooleanVar())

        label = "local object " + str(n)
        self.menu1_1.add("checkbutton", label = label, onvalue = 1, offvalue = 0, variable = self.Local[-1],
                       command = lambda: self.toggle_object(local))

        if update:

            self.validate_Local()
            self.sync_VoxelDim()
            self.center = (self.current_Object.center())
            self.update_object_frame(self.objectList)


    def Pack_Images(self):
        for i in self.Screen.LoadedImages.keys():
            img = self.Screen.LoadedImages[i]
            self.saveImage(i, img)

    def saveImage(self, fileName, img):
        imagesDir = "Images"
        if validators.url(fileName):
            name = fileName.split('/')[-1]
            if '?' in name:
                R = re.match(r'([a-zA-Z]*)([\-]?)([a-zA-Z]*)([\-]?)(\d*)', name)
                N = "".join(R.groups())
                name = N + ".jpg"
        else:
            (path, name) = os.path.split(fileName)
        P = os.path.join(sceneDir, imagesDir)
        f = os.path.join(sceneDir, imagesDir, name)
        if not os.path.exists(P):
            try:
                os.makedirs(P)
            except:
                print("cannot create directory")
                return
        if not os.path.isfile(f):
            print("saving", name)
            img.save(f)

    def goto_Imagefile(self):
        if self.SDL_bind:
            if self.propagate:
                texture = self.current_Object.texName()
            else:
                texture = self.current_Object[self.currentVoxel].texName
            if texture is None:
                texture = self.current_Object.texName()
            print(texture)
            if texture is not None:
                try:
                    self.open_image_display(texture)
                except:
                    pass
        else:
            if self.propagate:
                image = self.current_Object.image()
            else:
                image = self.current_Object[self.currentVoxel].image
            if image is None:
                image = self.current_Object.image()
            print(image)
            if self.ImageCombo:
                (path, name) = os.path.split(image)
                extension = name[-3:]
                R = re.match(r'(\D*)(\d*)', name)
                from_images = []
                imgList = []
                if os.path.isdir(path):
                    dirs = []
                    try:
                        dirs = os.listdir(path)
                        dirs.sort()
                    except(Exception) as detail:
                        print('EXC0')

                    for i in dirs:
                        if i[-3:] == extension:
                            if R.group(2):
                                if R.group(1) == i[:len(R.group(1))]:
                                    imgList.append(i)
                            else:
                                imgList.append(i)
                if imgList:
                    m = (for_depth_divisions / len(imgList)) + 1
                    print(m)
                    imgList *= m
                    (x, y, s) = self.current_Object[self.currentVoxel].give_depth(self.Depth)
                    (x, y, s) = self.current_Object[self.currentVoxel].map_to_screen(x, y, s)
                    S = int(s)
                    print(S)
                    if S < len(imgList) and S >= 0:
                        name = imgList[S]
                        image = os.path.join(path, name)
            if image is not None:
                try:
                    self.open_image_display(image)
                except:
                    pass

    def tune_voxels_size(self, i):
        try:
            self.AnimSequence[:, :, :, :, 0] *= i
        except:
            (frames, X, Y, Z, t) = self.AnimSequence.shape
            for f in range(frames):
                for x in range(X):
                    for y in range(Y):
                        for z in range(Z):
                            if self.AnimSequence[f, x, y, z, 0] > 0:
                                self.AnimSequence[f, x, y, z, 0] *= i
        self.goto_animation_frame(self.objectList, self.Time)
        #self.write_AnimSequence_file([self.current_Object,])

    def menubar_action(self, event):
        self.stop_animation()
        self.root.title("World Pixel (...) " + sceneDir)
        if self.axis_rotation:
            self.toggle_Rotation()

    def drag_to_canvas(self, event, widget = None, X = 0, Y = 0, data = None):
        #self.lock.acquire()
        print(data)
        if event is None:
            if X == '0' and Y == '0':
                X = widget.winfo_pointerx()
                Y = widget.winfo_pointery()
            x = int(X) - widget.winfo_rootx()
            y = int(Y) - widget.winfo_rooty()
            filename = data
        else:
            x = event.x_root - event.widget.winfo_rootx()
            y = event.y_root - event.widget.winfo_rooty()
            filename = event.data
        filenames = [filename,]
        if filename[-1] == "}":
            filename = filename[1:-1]
            if '}{' in filename:
                filenames = filename.split('}{')
            elif '} {' in filename:
                filenames = filename.split('} {')
        else:
            if ' ' in filename:
                filenames = filename.split(' ')
        if len(filenames) > 1:
            filename = filenames[-1]
        print(filename)
        (path, name) = os.path.split(filename)
        if name[-4:] == ".obj" or name[-4:] == ".OBJ":
            try:
                l = self.Screen.pixelmap_picking.get_array()
                m = l[x, y] - 1
                M = l[x, y]
                print(m)
                if m > -1:
                    if len(filenames) > 1:
                        self.load_object_repros(filenames)
                    else:
                        self.load_object_repro(filename, m)
                elif M < 0:
                    Object = self.ObjectList[-M - 1]
                    self.load_object_repro(filename, m, local = Object)
            except(Exception) as detail:
                print(detail)
        else:
            if self.Textures and self.Screen.SDL_Mode:
                try:
                    l = self.Screen.pixelmap_picking.get_array()
                    m = l[x, y] - 1
                    M = l[x, y]
                    print(m)
                    if m > -1:
                        if len(filenames) > 1:
                            self.place_voxel_textures(filenames)
                        else:
                            self.place_voxel_texture(filename, m)
                    elif M < 0:
                        Object = self.ObjectList[-M - 1]
                        self.set_ground_pic(filename, sceneLoad = False, Object = Object)
                    else:
                        self.set_background(filename)
                except(Exception) as detail:
                    print(detail)
            else:
                try:
                    l = self.Screen.pixelmap_picking.get_array()
                    m = l[x, y] - 1
                    M = l[x, y]
                    print(m)
                    if m > -1:
                        self.set_raster_pic_dialog(filename, m)
                    elif M < 0:
                        Object = self.ObjectList[-M - 1]
                        self.set_ground_pic(filename, sceneLoad = False, Object = Object)
                    else:
                        self.set_background(filename)
                except(Exception) as detail:
                    print(detail)
        #self.lock.release()
        self.root.event_generate("<FocusIn>", when="tail")

    def drag_to_animpane(self, event, widget = None, X = 0, Y = 0, data = None):
        if event is None:
            filename = data
        else:
            filename = event.data
        if filename[-1] == "}":
            filename = filename[1:-1]
        print(filename)
        (path, name) = os.path.split(filename)
        if name[-4:] == ".obj" or name[-4:] == ".OBJ":
            self.load_object(filename, force = True)
        else:
            try:
                img = Image.open(filename)
            except(Exception) as detail:
                print(detail)
                return
            self.textures_folder = path
            self.Screen.image = filename
            if self.Textures and self.Screen.SDL_Mode:
                self.Screen.setup_Texture()
            self.update_frame(self.objectList)
        self.root.event_generate("<FocusIn>", when="tail")

    def save_all_files(self):
        if not self.localCenter:
            self.alert_LocalCenter()
            return
        t = time.time()
        if not self.minorlevel:
            self.truncate_voxels()
        self.clear_highlight()
        self.save_scene_state()
        self.write_objects_pic()
        self.dump_object_arrays()
        self.print_object_voxels_subdiv()
        self.print_object_voxels()
        self.print_object_voxels_repro()
        self.save_object_files()
        #self.write_objects()
        T = time.time()
        print("time spent", T - t)
        #self.write_AnimSequence_file(self.objectList)
        self.copy_Animation_files(self.objectList)
        self.current_Object.get_highlight(self.currentVoxel)
        self.get_dimension()
        self.root.title("World Pixel (Saved) " + sceneDir)

    def dump_object_arrays(self):
        currentDir = arraysDir
        path = os.path.join(folders, sceneDir, currentDir)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
                return

        fileName = "array"
        fileNames = []
        for i in self.objectList:
            episode = self.ObjectList.index(i)

            v, c, s, V = i.dump_arrays(self.minorlevel)
            for dim in v.keys():
                filename_vis = fileName + "vis" + str(episode) + "_" + str(dim) + ".num"
                filename_col = fileName + "col" + str(episode) + "_" + str(dim) + ".num"
                filename_siz = fileName + "siz" + str(episode) + "_" + str(dim) + ".num"
                filename_vec = fileName + "vec" + str(episode) + "_" + str(dim) + ".num"
                try:
                    v[dim].dump(os.path.join(path, filename_vis))
                    fileNames.append(filename_vis)
                    print(filename_vis + " written!")
                    c[dim].dump(os.path.join(path, filename_col))
                    fileNames.append(filename_col)
                    print(filename_col + " written!")
                    s[dim].dump(os.path.join(path, filename_siz))
                    fileNames.append(filename_siz)
                    print(filename_siz + " written!")
                    V[dim].dump(os.path.join(path, filename_vec))
                    fileNames.append(filename_vec)
                    print(filename_vec + " written!")
                except(Exception) as detail:
                    print("Exception", detail)
        self.CVar1.set(str(len(fileNames)) + " arrays written into " + currentDir + " directory!")

    def read_object_arrays(self, update = False, visibility = True):
        currentDir = arraysDir
        path = os.path.join(folders, sceneDir, currentDir)
        if not os.path.exists(path):
            return

        fileName = "array"
        for i in self.objectList:
            i.shift_colors_reset()
            episode = self.ObjectList.index(i)
            v, c, s, V = i.dump_arrays()
            for dim in v.keys():
                filename_vis = fileName + "vis" + str(episode) + "_" + str(dim) + ".num"
                filename_col = fileName + "col" + str(episode) + "_" + str(dim) + ".num"
                filename_siz = fileName + "siz" + str(episode) + "_" + str(dim) + ".num"
                filename_vec = fileName + "vec" + str(episode) + "_" + str(dim) + ".num"
                if visibility:
                    try:
                        v[dim][:][:] = load(os.path.join(path, filename_vis))[:][:]
                        print(filename_vis + " opened and read!")
                    except(Exception) as detail:
                        print(filename_vis + " not opened!", detail)
                        continue
                try:
                    c[dim][:][:] = load(os.path.join(path, filename_col))[:][:]
                    print(filename_col + " opened and read!")
                except(Exception) as detail:
                    print(filename_col + " not opened!", detail)
                    continue
                try:
                    s[dim][:][:] = load(os.path.join(path, filename_siz))[:][:]
                    print(filename_siz + " opened and read!")
                except(Exception) as detail:
                    print(filename_siz + " not opened!", detail)
                    continue
                try:
                    V[dim][:][:] = load(os.path.join(path, filename_vec))[:][:]
                    print(filename_vec + " opened and read!")
                except(Exception) as detail:
                    print(filename_vec + " not opened!", detail)
                    continue
        if update:
            self.update_frame(self.objectList)

    def copy_Animation_files(self, objects):
        currentDir = animDir
        path = os.path.join(folders, sceneDir, currentDir)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
                return
        fileNames = []
        if previousScene is None:
            return
        previouspath = os.path.join(folders, previousScene, currentDir)
        if not os.path.exists(previouspath):
            return
        if path != previouspath:
            Animationfiles = os.listdir(previouspath)
            ExsistingFiles = os.listdir(path)
            file_Names = ["anim", "vec_anim"]
            for fileName in file_Names:
                for i in self.objectList:
                    episode = self.ObjectList.index(i)
                    dimensions = i.get_dimensions()
                    for d in dimensions:
                        filename = fileName + str(episode) + "_" + str(d) + ".num"
                        if filename in Animationfiles:
                            name = os.path.join(previouspath, filename)
                            if filename not in ExsistingFiles:
                                Name = os.path.join(path, filename)
                                shutil.copy2(name, Name)
                                fileNames.append(filename)

        self.CVar1.set(str(len(fileNames)) + " files written into " + currentDir + " directory!")

    def reset_camera_pan(self):
        for i in self.ObjectList:
            i.reset_camera_pan()

    def verify_objects(self):
        currentDir = object_dir
        pathName = os.path.join(folders, sceneDir, currentDir)
        if os.path.isdir(pathName):
            dirs = []
            objList = []
            try:
                dirs = os.listdir(pathName)
                dirs.sort()
            except(Exception) as detail:
                print('EXC0')
                return

            for i in dirs:
                if i[-8:] == "_pos.txt":
                    objList.append(i)
        else:
            return
        if not objList:
            return
        if len(self.ObjectList) < len(objList):
            L = len(objList) - len(self.ObjectList)
            for i in range(L):
                self.append_object(False)

    def load_object_scene(self, cleanupRepro = True):
        t = time.time()
        if psutil_enable:
            v = psutil.virtual_memory().percent
        else:
            v = 0.0
        if cleanupRepro and v > mem_Limit:
            self.alert_CleanupVoxelsRepro()
        self.cleanup()
        if self.Zoomed:
            self.Zoomed = False
            self.tunein_Ground()
            self.toggle_Shadows(True, False)
            self.undo_rest(self.isolate_rest)
        if self.frontView or self.sideView or self.topView:
            self.undo_View()
        self.reset_camera_pan()
        self.verify_objects()
        self.setup_progress(6)
        self.openMinorHint()
        self.openAngleHint()
        sdl_bind = self.SDL_bind

        for i in self.ObjectList:
            i.set_direction(rotation_amount)
        self.progressbar.set_msg(sceneDir + "\nread object files\n")
        self.read_object_files(update = False)
        if self.progressbar == None:
            return
        else:
            self.progressbar.advance(sceneDir + "\nload scene\n")

        SDL_bind = self.load_scene()
        if platform == 'darwin':
            SDL_bind = False

        if (SDL_bind and not self.SDL_bind) or (not SDL_bind and self.SDL_bind):
            self.toggle_SDL_Mode(False)
        VBOFrames = False
        if self.VBOFrames:
            VBOFrames = True
            self.toggle_Frames()

        if self.progressbar == None:
            return
        else:
            self.progressbar.advance(sceneDir + "\nplace images\n")

        self.place_images()

        if self.progressbar == None:
            return
        else:
            self.progressbar.advance(sceneDir + "\nread object voxels\n")

        self.read_object_voxels(True)
        if self.progressbar == None:
            return
        else:
            self.progressbar.advance(sceneDir + "\nread voxels repro\n")

        self.read_object_voxels_repro()
        if self.progressbar == None:
            return
        else:
            self.progressbar.advance(sceneDir + "\nread object arrays\n")

        self.read_object_arrays()

        self.load_into_AnimSequence(self.objectList)
        if self.vectorAnim:
            self.load_Vectors_into_AnimSequence(self.objectList)

        if SDL_bind and not sdl_bind:
            self.Screen.Background_texture = self.Screen.createBackground(self.Screen.BackgroundImage)

        if SDL_bind:
            self.Screen.setup_Objects_Ground(self.objectList)
        if VBOFrames:
            self.toggle_Frames()

        self.get_dimension()

        self.quit_progress()
        T = time.time()
        print("time spent", T - t)
        self.root.event_generate("<FocusIn>", when="tail")
        self.root.title("World Pixel (Loaded) " + sceneDir)
        self.clear_collected(self.objectList)
        self.update_frame(self.objectList)

    def load_scene_prop(self):
        self.OBJ_bind = False
        self.OBJ_Mode.set(self.OBJ_bind)
        self.Screen.set_OBJ_Mode(self.OBJ_bind, self.obj_transform)
        self.load_scene()

    def load_scene(self):
        currentDir = scene_dir
        fileName = "Scene" + ".txt"
        path = os.path.join(folders, sceneDir, currentDir)
        filename = os.path.join(folders, sceneDir, currentDir, fileName)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        try:
            f = open(filename, "r")
            scene = eval(f.read())
            f.close()
            print(str(scene))
        except(Exception) as detail:
            print("opening and reading " + str(filename) + " failed")
            print(detail)
            return
        if self.localCenter:
            self.local_Center.set(False)
            self.toggle_local_Center(False)
        objectList = scene[1]
        objects = []
        for i in objectList:
            for j in self.ObjectList:
                if j.Name == i:
                    objects.append(j)
                    break
        self.objectList = objects
        Name = scene[11]
        for x, i in enumerate(self.objectList):
            i.set_name(Name[x])
            if i is not self.current_Object:
                print("i is not" + i.Name)
                i.set_picmap(False)
        self.validate_Local()
        self.random_rot = scene[2]
        self.Screen.random_rot = self.random_rot
        self.RotCombine = scene[3]
        self.rot_Combine.set(self.RotCombine)
        self.ImageCombo = scene[4]
        self.Image_Combo.set(self.ImageCombo)
        self.set_canvas_size(scene[5], scene[6], False)
        try:
            self.saveBackground = scene[14]
            print("saveBackground", self.saveBackground)
            self.save_Background.set(self.saveBackground)
            self.Depth = scene[15]
            print("Depth", self.Depth)
            if self.Depth:
                d = 5.0 / self.Depth
            else:
                d = 0
            self.Depth_factor.set(d)
            for i in self.objectList:
                i.set_depth(self.Depth)
        except:
            pass
        try:
            self.set_background_color_alpha(scene[12], scene[13])
        except:
            pass
        if scene[7]:
            self.set_background(scene[7])
        self.synchronize = scene[8]
        self.Sync.set(self.synchronize)
        self.EntryVar4.set("%3.2f"%rad2deg(scene[0]))
        self.EntryVar.set("%d %d %d" % scene[10])
        self.localCenter = scene[9]
        self.local_Center.set(self.localCenter)
        self.toggle_local_Center()
        if self.objectList:
            self.select_object(self.objectList[0])
        SDL_bind = True
        try:
            SDL_bind = scene[16]
        except:
            pass
        try:
            ground_image = scene[17]
            if platform == 'darwin':
                pass
            else:
                self.set_ground_pic(ground_image, False)
        except:
            pass
        try:
            self.Screen.SPECIAL_FLAG = scene[18]
            self.special_Flag.set(self.Flags.index(scene[18]))
        except:
            pass
        try:
            BlurMode    = scene[19]
            MedianMode  = scene[20]
            BandingMode = scene[21]
            NoiseMode   = scene[22]
            AlphaMode   = scene[23]
            EdgeMode    = scene[25]
            self.toggle_Blur_Mode(BlurMode)
            self.toggle_Median_Mode(MedianMode)
            self.toggle_Edge_Mode(EdgeMode)
            self.toggle_Banding_Mode(BandingMode)
            self.toggle_Noise_Mode(NoiseMode)
            self.toggle_Alpha_Mode(AlphaMode)
        except:
            pass
        try:
            preMult = scene[24]
            self.toggle_pre_Mult(preMult)
        except:
            pass
        try:
            useMtl = scene[26]
            self.toggle_Mtl_use(useMtl)
        except:
            pass
        try:
            colorShifter = scene[27]
            R = scene[28]
            G = scene[29]
            B = scene[30]
            self.toggle_color_Shifter(colorShifter)
            self.toggle_R(R)
            self.toggle_G(G)
            self.toggle_B(B)
        except:
            pass
        try:
            groundAll = scene[31]
            self.toggle_GroundAll(update = False, mode = groundAll)
        except:
            pass
        try:
            self.syncLevels = scene[32]
            self.sync_Levels.set(self.syncLevels)
            self.syncPositions = scene[33]
            self.sync_Positions.set(self.syncPositions)
        except:
            pass
        try:
            self.clearcolor_Compose = scene[34]
            self.clear_color_Compose.set(self.clearcolor_Compose)
        except:
            pass
        try:
            hBandingMode = scene[35]
            self.toggle_hBanding_Mode(hBandingMode)
        except:
            pass
        try:
            Zippedspawn = scene[36]
            self.toggle_Zippedspawn(Zippedspawn)
        except:
            pass
        try:
            vectorAnim = scene[37]
            self.toggle_vector_Anim(vectorAnim)
        except:
            pass
        try:
            self.LockAngle = scene[38]
            self.Lock_Angle.set(self.LockAngle)
        except:
            pass
        try:
            self.Time = scene[39]
            self.frame = self.Time
        except:
            pass
        return SDL_bind

    def save_scene_state(self):
        currentDir = scene_dir
        fileName = "Scene" + ".txt"
        path = os.path.join(folders, sceneDir, currentDir)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
                return
        filename = os.path.join(folders, sceneDir, currentDir, fileName)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        if self.localCenter:
            angle = self.c_baked
        else:
            angle = self.angle

        objectList = []
        Names = []
        for i in self.objectList:
            objectList.append(i.Name)
            Names.append(i.name())
        scene = [
        angle,
        objectList,
        self.random_rot,
        self.RotCombine,
        self.ImageCombo,
        canvas_w,
        canvas_h,
        self.background_filename,
        self.synchronize,
        self.localCenter,
        self.vector,
        Names,
        self.background_color,
        self.clear_color,
        self.saveBackground,
        self.Depth,
        self.SDL_bind,
        self.groundImage,
        self.Screen.SPECIAL_FLAG,
        self.BlurMode,
        self.MedianMode,
        self.BandingMode,
        self.NoiseMode,
        self.AlphaMode,
        self.Screen.preMult,
        self.EdgeMode,
        self.useMtl,
        self.colorShifter,
        self.R,
        self.G,
        self.B,
        self.groundAll,
        self.syncLevels,
        self.syncPositions,
        self.clearcolor_Compose,
        self.hBandingMode,
        self.Zippedspawn,
        self.vectorAnim,
        self.LockAngle,
        self.Time
        ]
        try:
            f = open(filename, "w")
            f.write(str(scene))
            f.close()
            self.CVar1.set(str(filename) + " written")
        except:
            self.CVar1.set("writing " + str(filename) + " failed")

        fileName1 = "MinorHint.txt"
        filename1 = os.path.join(folders, sceneDir, currentDir, fileName1)
        minorlevel = self.minorlevel
        try:
            f = open(filename1, "w")
            f.write(str(minorlevel))
            f.close()
        except:
            pass
        fileName2 = "AngleHint.txt"
        filename2 = os.path.join(folders, sceneDir, currentDir, fileName2)
        lockAngle = self.LockAngle
        try:
            f = open(filename2, "w")
            f.write(str(lockAngle))
            f.close()
        except:
            pass

    def openAngleHint(self):
        currentDir = scene_dir
        fileName1 = "AngleHint.txt"
        filename1 = os.path.join(folders, sceneDir, currentDir, fileName1)
        n = None
        try:
            f = open(filename1, "r")
            n = eval(f.read())
            f.close()
        except:
            pass
        if n == None:
            return
        self.LockAngle = n
        self.Lock_Angle.set(self.LockAngle)

    def openMinorHint(self):
        currentDir = scene_dir
        fileName1 = "MinorHint.txt"
        filename1 = os.path.join(folders, sceneDir, currentDir, fileName1)
        n = None
        try:
            f = open(filename1, "r")
            n = eval(f.read())
            f.close()
        except:
            pass
        if n == None:
            return
        self.minorlevel = n
        if self.msg_box_Minor_level != None and self.msg_box_Minor_level.winfo_exists():
            self.msg_box_Minor_level.set_Lock(self.minorlevel)

    def saveMinorHint(self):
        currentDir = scene_dir
        fileName1 = "MinorHint.txt"
        filename1 = os.path.join(folders, sceneDir, currentDir, fileName1)
        try:
            f = open(filename1, "w")
            f.write(str(self.minorlevel))
            f.close()
        except(Exception) as detail:
            print(detail)

    def print_object_voxels(self):
        for i in self.ObjectList:
            self.print_out_voxels(i, init = False)

    def print_out_voxels(self, object_treat, init = True):
        currentDir = voxels_dir
        fileName = object_treat.Name + ".txt"
        path = os.path.join(folders, sceneDir, currentDir)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
                return
        filename = os.path.join(folders, sceneDir, currentDir, fileName)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return

        object_treat.renumber_invisible()

        current_voxel = object_treat.get_biggest_pixel()
        biggest_pixel = object_treat.voxels()[current_voxel]
        voxels = biggest_pixel.voxels
        if type(voxels) is not list:
            voxels = []

        conform = object_treat.conform_position() + object_treat.local_conform()
        images = []
        spins = []
        spin_amounts = []
        frame = []
        spawned = []
        color = []
        size = []
        c = []
        k = {}

        images = [biggest_pixel.image,]
        spins = [biggest_pixel.spin,]
        spin_amounts = [biggest_pixel.spin_amount,]
        frame = [biggest_pixel.frame,]
        spawned = [biggest_pixel.spawned,]
        if init:
            color = [tuple(biggest_pixel.color),]
            size = [list(biggest_pixel.size),]

        #if biggest_pixel.voxels and not biggest_pixel.spawned:
        zipped = biggest_pixel.zipped

        c = [-1,]
        k[-1] = [((0.0, 0.0, 0.0), 0, 0, 0, 0, 0, 0, 0, zipped),]

        def append_c(superior, voxels, collect, keyed):
            c = []
            collect.append(superior.currency)
            for i in voxels:
                image = i.image
                if image not in images:
                    images.append(image)
                img = images.index(image)

                spin = i.spin
                if spin not in spins:
                    spins.append(spin)
                spi = spins.index(spin)

                spin_amount = i.spin_amount
                if spin_amount not in spin_amounts:
                    spin_amounts.append(spin_amount)
                spi_amount = spin_amounts.index(spin_amount)

                fram = i.frame
                if fram not in frame:
                    frame.append(fram)
                frm = frame.index(fram)

                spaw = i.spawned
                if spaw not in spawned:
                    spawned.append(spaw)
                spa = spawned.index(spaw)

##                if i.voxels and not spaw:
##                    zipped = True
##                else:
##                    zipped = False
                if init:
                    col = tuple(i.color)
                    IS = False
                    for clr, COL in enumerate(color):
                        if str(COL) == str(col):
                            IS = True
                            break
                    if not IS:
                        clr = len(color)
                        color.append(col)

                    siz = list(i.size)
                    if siz not in size:
                        size.append(siz)
                    sze = size.index(siz)
                else:
                    clr = 0
                    sze = 0

                c.append((i.get_unchanged(conform), img, spi, spi_amount, frm, spa, clr, sze, int(i.zipped)))
                if i.voxels:
                    append_c(i, i.voxels, collect, keyed)
            keyed[superior.currency] = c


        append_c(biggest_pixel, voxels, c, k)

        try:
            f = open(filename, "w")
            f.write("[" + str(images) + ",\n")
            f.write(str(spins) + ",\n")
            f.write(str(spin_amounts) + ",\n")
            f.write(str(frame) + ",\n")
            f.write(str(spawned) + ",\n")
            f.write(str(color) + ",\n")
            f.write(str(size) + ",\n")
            f.write("[" + "\n")
            for C in c:
                f.write("(" + str(C) + "," + str(k[C]) + "),\n")
            f.write("]" + "\n")
            f.write("]" + "\n")
            f.close()
            self.CVar1.set(str(filename) + " written")
        except:
            self.CVar1.set("writing " + str(filename) + " failed")

    def sync_voxels(self, color = False, objects = None):
        self.clear_highlight()
        self.Screen.set_Tween(False)
        self.Screen.set_Frames(False)
        fileName = self.current_Object.Name + ".txt"
        vector = self.current_Object.get_local_vector()
        if objects is None:
            objects = self.objectList
        for i in objects:
            i.reset_Oscillate()
            self.read_out_voxels(i, False, False, fileName, colors = color, visible = True)
            i.set_vector(vector)
        self.Screen.set_Tween(self.VBOTween)
        self.Screen.set_Frames(self.VBOFrames)
        self.update_frame(self.objectList)

    def read_object_voxels(self, colors):
        if self.minorlevel:
            spawn = True
        else:
            spawn = False
        for i in self.ObjectList:
            self.read_out_voxels(i, spawn = spawn, colors = colors)
        self.update_object_frame(self.objectList)

    def span_out_voxels(self, object_treat, init = True):
        currentDir = voxels_dir
        fileName = object_treat.Name + "_subdiv.txt"
        filename = os.path.join(folders, sceneDir, currentDir, fileName)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return False
        try:
            f = open(filename, "r")
            data = eval(f.read())
            print("span_out_voxels READ", len(data))
            f.close()
        except(Exception) as detail:
            print("opening and reading " + str(filename) + " failed")
            print(detail)
            return False

        object_treat.spawn_to_voxels(data, init)
        return True


    def read_out_voxels(self, object_treat, update = False, dialog = False,
                        fileName = None, spawn = False, colors = True, sizes = True, visible = False):
        currentDir = voxels_dir
        if not fileName:
            fileName = object_treat.Name + ".txt"
        if dialog:
            path = os.path.join(folders, sceneDir, currentDir)
            filename = askopenfilename(initialdir = path,
                                       initialfile = fileName,
                                    filetypes = (("Text files", "*.txt"),
                                                 ("All files", "*.*")))
        else:
            filename = os.path.join(folders, sceneDir, currentDir, fileName)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        try:
            f = open(filename, "r")
            data = eval(f.read())
            spawned = []
            color = []
            size = []
            print("READ", len(data))
            if len(data) == 6:
                if spawn:
                    (images, spins, spin_amounts, frame, spawned, voxels) = data
                else:
                    (images, spins, spin_amounts, frame) = data[0:4]
                    voxels = data[5]
            elif len(data) == 8:
                (images, spins, spin_amounts, frame) = data[0:4]
                voxels = data[7]
                if spawn:
                    spawned = data[4]
                if colors:
                    color = data[5]
                if sizes:
                    size = data[6]
            else:
                (images, spins, spin_amounts, frame, voxels) = data
            f.close()
##            print(str(images))
##            print(str(color))
##            print(voxels[0][1][0][0])

        except(Exception) as detail:
            print("opening and reading " + str(filename) + " failed")
            print(detail)
            return
        if self.progressbar:
            object_treat.apply_to_voxels(images, spins, spin_amounts, frame, spawned, voxels, color, size, self.random_rot,
                                         self.RotCombine, self.ImageCombo, visible, self.progressbar)
        else:
            self.setup_progress(len(images))
            object_treat.apply_to_voxels(images, spins, spin_amounts, frame, spawned, voxels, color, size, self.random_rot,
                                         self.RotCombine, self.ImageCombo, visible, self.progressbar, True)
            self.quit_progress()
        if update:
            self.update_frame(self.objectList)

    #
    def print_object_voxels_repro(self, objects = None, path = None):
        if objects == None:
            objects = self.ObjectList
        for i in objects:
            self.print_out_voxels_repro(i, path)

    def print_object_voxels_subdiv(self, objects = None, path = None):
        if objects == None:
            objects = self.ObjectList
        for i in objects:
            self.print_out_voxels_subdiv(i, path)

    def print_out_voxels_subdiv(self, object_treat, path):
        if path:
            currentDir = path
            fileName = object_treat.Name + "_subdiv.txt"
            filename = os.path.join(currentDir, fileName)
        else:
            currentDir = voxels_dir
            fileName = object_treat.Name + "_subdiv.txt"
            path = os.path.join(folders, sceneDir, currentDir)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except:
                    print("cannot create directory")
                    return
            filename = os.path.join(folders, sceneDir, currentDir, fileName)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return

        object_treat.renumber_invisible()

        current_voxel = object_treat.get_biggest_pixel()
        biggest_pixel = object_treat.voxels()[current_voxel]
        voxels = biggest_pixel.voxels
        if type(voxels) is not list:
            voxels = []

        conform = object_treat.conform_position() + object_treat.local_conform()
        c = []
        k = {}

        if biggest_pixel.voxels:
            zipped = 1
        else:
            zipped = 0

        c = [-1,]
        k[-1] = [((0.0, 0.0, 0.0), zipped),]

        def append_c(superior, voxels, collect, keyed):
            c = []
            collect.append(superior.currency)
            for i in voxels:
                if i.voxels:
                    zipped = 1
                else:
                    zipped = 0
                c.append((i.get_unchanged(conform), zipped))
                if i.voxels:
                    append_c(i, i.voxels, collect, keyed)
            keyed[superior.currency] = c


        append_c(biggest_pixel, voxels, c, k)

        try:
            f = open(filename, "w")
            f.write("[" + "\n")
            for C in c:
                f.write("(" + str(C) + "," + str(k[C]) + "),\n")
            f.write("]" + "\n")
            f.close()
            self.CVar1.set(str(filename) + " written")
        except:
            self.CVar1.set("writing " + str(filename) + " failed")

    def print_out_voxels_repro(self, object_treat, path):
        if path:
            currentDir = path
            fileName = object_treat.Name + "_repro.txt"
            filename = os.path.join(currentDir, fileName)
        else:
            currentDir = voxels_dir
            fileName = object_treat.Name + "_repro.txt"
            path = os.path.join(folders, sceneDir, currentDir)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except:
                    print("cannot create directory")
                    return
            filename = os.path.join(folders, sceneDir, currentDir, fileName)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return

        object_treat.renumber_invisible()

        current_voxel = object_treat.get_biggest_pixel()
        biggest_pixel = object_treat.voxels()[current_voxel]
        voxels = biggest_pixel.voxels
        if type(voxels) is not list:
            voxels = []

        conform = object_treat.conform_position() + object_treat.local_conform()
        repros = []
        textures = []
        Frames = []
        Pos_And_Scale = []
        Wire_Frame = []
        Oscillate = [0, 1, -1]
        c = []
        k = {}

        repros = [biggest_pixel.repro,]
        textures = [biggest_pixel.texName,]
        Frames = [biggest_pixel.Frames,]
        Pos_And_Scale = [biggest_pixel.return_Pos_And_Scale(),]
        Wire_Frame = [biggest_pixel.return_Wire_Render(),]
        Osc = Oscillate.index(biggest_pixel.Oscillate)
        c = [-1,]
        k[-1] = [((0.0, 0.0, 0.0), 0, 0, 0, Osc),]

        def append_c(superior, voxels, collect, keyed):
            c = []
            collect.append(superior.currency)
            for i in voxels:
                repro = i.repro
                if repro not in repros:
                    repros.append(repro)
                    PosScale = i.return_Pos_And_Scale()
                    Pos_And_Scale.append(PosScale)
                    WireFrame = i.return_Wire_Render()
                    Wire_Frame.append(WireFrame)
                rep = repros.index(repro)
                texture = i.texName
                if texture not in textures:
                    textures.append(texture)
                tex = textures.index(texture)
                Fram = i.Frames
                if Fram not in Frames:
                    Frames.append(Fram)
                Frm = Frames.index(Fram)
                Osc = Oscillate.index(i.Oscillate)
                c.append((i.get_unchanged(conform), rep, tex, Frm, Osc))
                if i.voxels:
                    append_c(i, i.voxels, collect, keyed)
            keyed[superior.currency] = c


        append_c(biggest_pixel, voxels, c, k)

        try:
            f = open(filename, "w")
            f.write("[" + str(repros) + ",\n")
            f.write(str(textures) + ",\n")
            f.write(str(Frames) + ",\n")
            f.write(str(Pos_And_Scale) + ",\n")
            f.write(str(Wire_Frame) + ",\n")
            f.write("[" + "\n")
            for C in c:
                f.write("(" + str(C) + "," + str(k[C]) + "),\n")
            f.write("]" + "\n")
            f.write("]" + "\n")
            f.close()
            self.CVar1.set(str(filename) + " written")
        except:
            self.CVar1.set("writing " + str(filename) + " failed")

    def read_object_voxels_repro(self, objects = None, path = None):
        if objects == None:
            objects = self.ObjectList
        for i in objects:
            self.read_out_voxels_repro(i, path = path)

    def read_out_voxels_repro(self, object_treat, update = False, path = None):
        if path:
            currentDir = path
            fileName = object_treat.Name + "_repro.txt"
            filename = os.path.join(currentDir, fileName)
        else:
            currentDir = voxels_dir
            fileName = object_treat.Name + "_repro.txt"
            filename = os.path.join(folders, sceneDir, currentDir, fileName)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        try:
            f = open(filename, "r")
            n = eval(f.read())
            f.close()
        except(Exception) as detail:
            print("opening and reading " + str(filename) + " failed")
            print(detail)
            return
        try:
            Wire_Frame = None
            if len(n) == 5:
                (repros, textures, Frames, Pos_And_Scale, voxels) = n
            elif len(n) == 6:
                (repros, textures, Frames, Pos_And_Scale, Wire_Frame, voxels) = n
##            print(str(repros))
##            print(voxels[0][1][0][0])
        except(Exception) as detail:
            print(detail)
            return
        if self.progressbar:
            print("progress exists")
            object_treat.apply_to_voxels_repro(repros, textures, Frames, Pos_And_Scale, Wire_Frame, voxels, self.useLoaded, self.progressbar)
        else:
            print("progress setup")
            self.setup_progress(len(repros) + len(textures))
            object_treat.apply_to_voxels_repro(repros, textures, Frames, Pos_And_Scale, Wire_Frame, voxels, self.useLoaded, self.progressbar, True)
            self.quit_progress()
        if update:
            self.update_frame(self.objectList)
    #

    def select_visible_level(self):
        for i in self.ObjectList:
            i.select_visible_level()
        self.currentVoxel = self.current_Object.highlighted()

    def save_object_files(self):
        for i in self.ObjectList:
            i.select_visible_level()
            self.save_object_file(i, self.minorlevel)

    def read_object_files(self, collapse = True, ground = False, update = True):
        for i in self.ObjectList:
            self.read_object_file(i, False, collapse, ground)
        if update:
            self.update_object_frame(self.ObjectList)

    def save_object_file(self, local, minorlevel = True):
        currentDir = object_dir
        fileName = local.Name + "_pos.txt"
        path = os.path.join(folders, sceneDir, currentDir)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
                return
        filename = os.path.join(folders, sceneDir, currentDir, fileName)

        object_data = local.get_object_data(minorlevel)
        print("object_data", object_data)
        try:
            f = open(filename, "w")
            f.write("[" + "\n")

            f.write("('local_conform   '," + array_repr(object_data[0]) + "),\n")
            f.write("('conform_position'," + array_repr(object_data[1]) + "),\n")
            f.write("('local_position  '," + array_repr(object_data[2]) + "),\n")
            f.write("('angle           '," + str(object_data[3]) + "),\n")
            f.write("('local           '," + str(object_data[4]) + "),\n")
            f.write("('LOCAL           '," + str(object_data[5]) + "),\n")
            f.write("('DIM             '," + str(object_data[6]) + "),\n")
            f.write("('direction       '," + str(object_data[7]) + "),\n")
            f.write("('ground          '," + "\'" + object_data[8] + "\'" + "),\n")
            f.write("('draw_ground     '," + str(object_data[9]) + "),\n")
            f.write("]" + "\n")
            f.close()
            self.CVar1.set(str(filename) + " written")
        except:
            self.CVar1.set("writing " + str(filename) + " failed")

    def read_object_file(self, local, update = True, collapse = True, ground = False):
        currentDir = object_dir
        fileName = local.Name + "_pos.txt"
        filename = os.path.join(folders, sceneDir, currentDir, fileName)
        try:
            f = open(filename, "r")
            n = eval(f.read())
            f.close()
        except:
            print("opening and reading " + str(filename) + " failed")
            return
        if self.localCenter:
            self.local_Center.set(False)
            self.toggle_local_Center(False)
        try:
            D = dict(n)
        except:
            print("no dict success!")
            return
        local.reset_position()
        object_data = [D['local_conform   '],
                       D['conform_position'],
                       D['local_position  '],
                       D['angle           '],
                       D['local           '],]
        if 'direction       ' in D:
            object_data.append(D['direction       '])
        if 'ground          ' in D:
            filename = self.validate_filename(D['ground          '])
            object_data.append(filename)
        if 'draw_ground     ' in D:
            object_data.append(D['draw_ground     '])
        local.set_object_data(object_data)
        if 'LOCAL           ' in D and D['LOCAL           ']:
            local.switch_conform_position()
            local.move_to_conform(local.conform_position())

        if 'DIM             ' in D and collapse:
            DIM = D['DIM             ']
            #dim = local.get_dimension()
            print("local", local.Name)
            print("DIM AND dim", DIM, dim)
            #if dim != DIM:

            #local.collapse_all()
            """
            #local.setup_array(DIM)
            """


            if self.minorlevel:
                result = self.span_out_voxels(local)
                local.collapse_all()
            else:
                result = self.span_out_voxels(local, init = False)

        if ground and 'ground          ' in D:
            self.Screen.setup_Objects_Ground([self.current_Object,])

        if update:
            self.update_object_frame(self.objectList)

    def sync_animation(self):
        self.synchronize = not self.synchronize
        self.Sync.set(self.synchronize)

    def copy_animation(self):
        i = self.ObjectList.index(self.current_Object)
        if self.Animation[i] is None:
            self.animation_copy = self.AnimSequence.copy()
        else:
            self.animation_copy = self.Animation[i].copy()

    def paste_animation(self):
        i = self.ObjectList.index(self.current_Object)
        if self.animation_copy is not None:
            self.Animation[i] = self.animation_copy
        self.update_object_frame(self.objectList)

    def write_objects(self):
        self.clear_highlight()
        self.write_frame(self.objectList, object_name = True)
        # self.write_frame_levels(self.objectList)

    def place_config_levels(self):
        self.clear_highlight()
        self.load_frame_levels(self.objectList)

    def place_config(self):
        self.clear_highlight()
        self.load_frame(self.objectList, frame = 0, object_name = True)

    def write_objects_pic(self, filename = None, Repros_Only = False):
        if filename is None:
            currentDir = pic_files_dir
            currentDir = os.path.join(folders, sceneDir, currentDir)
            path = os.path.join(folders, sceneDir, pic_files_dir)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except:
                    print("cannot create directory")
                    return
            fileName = "Raster_0000.PICC"
            filename = os.path.join(path, fileName)

        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        data = []
        for i in self.objectList:
            PosAndScale = i.return_Pos_And_Scale()
            WireRender = i.return_Wire_Render()
            data.append(i.Name)
            if Repros_Only:
                data.append((None, i.repro(), i.texName(), i.Frames(), PosAndScale, WireRender))
            else:
                data.append((i.image(), i.repro(), i.texName(), i.Frames(), PosAndScale, WireRender))
        if data:
            f = open(filename, "w")
            f.write(str(data))
            f.close()

    def validate_filename(self, filename, dialog = True):
        if filename == None or filename == "":
            return ""
        if validators.url(filename):
            if internetOn:
                return filename
            else:
                return ""
        filename = filename.replace("\\","/")
        if not os.path.exists(filename):
            if os.path.isabs(filename):
                return ""
            else:
                S = filename.split('/')
                Name = []
                search = False
                for s in S:
                    if s == "..":
                        search = True
                    else:
                        Name.append(s)
                F = "/".join(Name)
                if search:
                    pre = ""
                    while not os.path.ismount(os.path.realpath(pre)):
                        pre += "../"
                        filename = pre + F
                        if os.path.exists(filename):
                            break
        if not os.path.exists(filename) and dialog:
            global lastusedDir
            (path, name) = os.path.split(filename)
            filename = os.path.join(lastusedDir, name)
            if not os.path.isfile(filename):
                filename = askopenfilename(title       = "Open " + path,
                                           initialdir  = lastusedDir,
                                           initialfile = name,
                                           filetypes   = [("All files", "*.*")])
            try:
                l = len(filename)
            except:
                l = len(str(filename))
            if l > 0:
                filename = os.path.normpath(filename)
                try:
                    filename = os.path.relpath(filename).replace("\\","/")
                except:
                    print("using absolute path")
                (lastusedDir, name) = os.path.split(filename)
                return filename
            else:
                return ""
        else:
            return filename

    def place_images(self, filename = None):
        if filename is None:
            currentDir = pic_files_dir
            currentDir = os.path.join(folders, sceneDir, currentDir)
            fileName = "Raster_0000.PICC"
            filename = os.path.join(currentDir, fileName)

        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        try:
            f = open(filename, "r")
            n = eval(f.read())
            f.close()
            print("file opened and read!")
            self.CVar1.set("loading raster pic " + str(filename) + " successful!")
        except(Exception) as detail:
            print("file not opened!", detail)
            self.CVar1.set("loading raster pic " + str(filename) + " failed")
            return
        try:
            N = dict(zip(n[0::2], n[1::2]))
        except:
            print("failed to dict")
            return

        F = False
        if not self.progressbar:
            F = True
            self.setup_progress(len(self.objectList))

        for i in reversed(self.objectList):
            name = i.Name
            if name in N:
                filename = N[name][0]
            else:
                continue
            filename = self.validate_filename(filename)
            if os.path.exists(filename):
                self.pic_image = filename
                init_images(filename, self.random_rot, self.RotCombine, self.ImageCombo)
                i.set_images()
            filename = N[name][1]
            filename = self.validate_filename(filename)
            try:
                Frames = N[name][3]
            except:
                Frames = 0
            if filename and os.path.isfile(filename):
                self.repro = filename
                if i.repro() == filename:
                    self.OBJ_repro = i.OBJ_repro()
                else:
                    if filename in self.Screen.objFileNames and self.useLoaded:
                        self.OBJ_repro = self.Screen.objFileNames[filename]
                    else:
                        faces = obj_loader.load(filename)
                        print("polys", len(faces))
                        Faces = []
                        Verts = []
                        Norms = []
                        if Frames > 1:
                            Faces, Verts, Norms = obj_loader.load_Faces(filename, self.progressbar, False)
                        self.OBJ_repro = obj_loader.obj_transform(faces, Faces, Verts, Norms)
                        self.Screen.objFileNames[filename] = self.OBJ_repro
                        self.Screen.obj_transforms.append(self.OBJ_repro)
                try:
                    PosAndScale = N[name][4]
                    self.OBJ_repro.tune_Position_And_Scale(PosAndScale)
                except:
                    pass

                try:
                    WireRender = N[name][5]
                    self.OBJ_repro.tune_Wire_Render(WireRender)
                except:
                    pass

                if self.SDL_bind and self.OBJ_repro:
                    if self.Screen.VBO:
                        if not self.OBJ_repro.VBO:
                            self.OBJ_repro.set_up_vertex_array()
                    elif not self.OBJ_repro.objdisplayList:
                        self.OBJ_repro.set_up_display_list()


                texture = None
                texName = None
                image = None

                if self.useMtl:
                    if filename[-3:] == "obj":
                        filename1 = filename.replace(".obj", ".mtl")
                    elif filename[-3:] == "OBJ":
                        filename1 = filename.replace(".OBJ", ".mtl")
                    else:
                        filename1 = ""
                    if os.path.exists(filename1):
                        f = open(filename1, "r")
                        lines = f.readlines()
                        while(lines):
                            p = lines.pop()
                            if p[:6] == "map_Kd":
                                image = p[7:]
                                image = image.rstrip()
                                break
                        f.close()
                        print(image)
                    else:
                        try:
                            image = N[name][2]
                        except:
                            print("no tex image")
                else:
                    try:
                        image = N[name][2]
                    except:
                        print("no tex image")

                if image == "empty":
                    if self.Screen.SDL_Mode:
                        texName = "empty"
                        texture = self.Screen.Empty_texture
                elif image is not None:
                    texName = image.replace("\\", "/")
                    texName = self.validate_filename(texName, False)
                    (path, name) = os.path.split(texName)
                    print(path)
                    if os.path.exists(path):
                        self.textures_folder = path

                    if self.Textures and self.Screen.SDL_Mode:
                        if texName in self.Screen.texNamesList and self.useLoaded:
                            texture = self.Screen.texNamesList[texName]
                        else:
                            texture = self.Screen.TexFromPNG(texName)

                self.texture = texture
                self.texName = texName
                i.set_repro(self.repro, self.OBJ_repro, texture, texName)

            if F:
                if self.progressbar == None:
                    return
                else:
                    self.progressbar.advance()

        if F:
            self.quit_progress()

        self.update_frame(self.objectList)

    def set_parent_vectors(self, vec):
        for i in self.objectList:
            i.set_vector(vec)

    def set_images(self):
        if self.current_Object.collected():
            self.current_Object.set_voxel_images()
        elif self.VoxelBased:
            self.current_Object.voxels()[self.currentVoxel].set_images()
        else:
            self.current_Object.set_images()
        restore_images_to_loaded()
        self.update_frame(self.objectList)

    def copy_repro(self):
        voxel = self.current_Object.voxels()[self.currentVoxel]
        if self.propagate or not voxel.repro:
            self.repro = self.current_Object.repro()
            self.OBJ_repro = self.current_Object.OBJ_repro()
            self.texture = self.current_Object.texture()
            self.texName = self.current_Object.texName()
        else:
            self.repro = voxel.repro
            self.OBJ_repro = voxel.OBJ_repro
            self.texture = voxel.texture
            self.texName = voxel.texName

    def set_repro(self):
        repro = self.repro
        OBJ_repro = self.OBJ_repro
        texture = self.texture
        texName = self.texName

        if self.SDL_bind and OBJ_repro:
            if self.Screen.VBO:
                if not OBJ_repro.VBO:
                    OBJ_repro.set_up_vertex_array()
            elif not OBJ_repro.objdisplayList:
                OBJ_repro.set_up_display_list()

        if self.Textures and self.Screen.SDL_Mode:
            if texName in self.Screen.texNamesList and self.useLoaded:
                texture = self.Screen.texNamesList[texName]
            else:
                texture = self.Screen.TexFromPNG(texName)

        if self.current_Object.collected():
            self.current_Object.set_voxel_repro(repro, OBJ_repro, texture, texName)
        elif self.VoxelBased_repro:
            self.current_Object.voxels()[self.currentVoxel].set_repro(repro, OBJ_repro, texture, texName)
        else:
            self.current_Object.set_repro(repro, OBJ_repro, texture, texName)
        self.update_frame(self.objectList)

    def cleanup(self):
        for i in self.ObjectList:
            i.cleanup()

    def empty_texture(self):
        if self.SDL_bind:
            texture = self.Screen.Empty_texture
            texName = "empty"
        else:
            texture = None
            texName = None
        if self.current_Object.collected():
            self.current_Object.set_voxel_texture(texture, texName)
            self.print_object_voxels_repro(self.objectList, VOXX)
        elif self.VoxelBased_repro:
            self.current_Object.voxels()[self.currentVoxel].set_texture(texture, texName)
            self.print_object_voxels_repro(self.objectList, VOXX)
        else:
            self.current_Object.set_texture(texture, texName)
            self.write_objects_pic(PICC, True)
        self.update_frame(self.objectList)

    def clean_texture(self):
        texture = None
        texName = None
        if self.OBJ_bind:
            self.Screen.clean_Texture()
        elif self.current_Object.collected():
            self.current_Object.set_voxel_texture(texture, texName)
            self.print_object_voxels_repro(self.objectList, VOXX)
        elif self.VoxelBased_repro:
            self.current_Object.voxels()[self.currentVoxel].set_texture(texture, texName)
            self.print_object_voxels_repro(self.objectList, VOXX)
        else:
            self.current_Object.set_texture(texture, texName)
            self.write_objects_pic(PICC, True)
        self.update_frame(self.objectList)

    def clean_repro(self):
        filename = os.path.join(folders, obj_files, "Cube.obj")
        repro = filename
        if filename in self.Screen.objFileNames and self.useLoaded:
            OBJ_repro = self.Screen.objFileNames[filename]
        else:
            repro = None
            OBJ_repro = None
        texture = None
        texName = None
        if self.current_Object.collected():
            self.current_Object.set_voxel_repro(repro, OBJ_repro, texture, texName)
            self.print_object_voxels_repro(self.objectList, VOXX)
        elif self.VoxelBased_repro:
            self.current_Object.voxels()[self.currentVoxel].set_repro(repro, OBJ_repro, texture, texName)
            self.print_object_voxels_repro(self.objectList, VOXX)
        else:
            self.current_Object.set_repro(repro, OBJ_repro, texture, texName)
            self.write_objects_pic(PICC, True)
        self.update_frame(self.objectList)

    def SelectSameTexture(self):
        self.current_Object.selectSameTexture()
        self.update_frame(self.objectList)

    def SelectSameOBJ(self):
        self.current_Object.selectSameOBJ()
        self.update_frame(self.objectList)

    def SelectHighlighted(self):
        self.current_Object.selectHighlighted()
        self.update_frame(self.objectList)

    def SelectSameImage(self):
        self.current_Object.selectSameImage()
        self.update_frame(self.objectList)

    def set_raster_pic(self, image):
        self.pic_image = image
        init_images(image, self.random_rot, self.RotCombine, self.ImageCombo)
        if self.current_Object.collected():
            self.current_Object.set_voxel_images()
        elif self.VoxelBased:
            self.current_Object.voxels()[self.currentVoxel].set_images()
        else:
            self.current_Object.set_images()
        self.update_frame(self.objectList)

    def clean_raster_pic(self):
        if self.current_Object.collected():
            self.current_Object.set_voxel_images(None)
        elif self.VoxelBased:
            self.current_Object.voxels()[self.currentVoxel].set_images(None)
        else:
            self.set_raster_pic("./Maailmapunkt_Gray1.png")
        self.update_frame(self.objectList)

    def set_raster_pic_dialog(self, filename = None, voxel = None):
        if filename == None:
            currentDir = os.path.dirname(self.pic_image)
            print("currentDir", currentDir)
            if currentDir == "" or currentDir == ".":
                currentDir = os.path.join(folders, raster_dir)
            filename = askopenfilename(initialdir = currentDir,
                                        filetypes = myFormats)
        if voxel == None:
            voxel = self.currentVoxel
        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        self.pic_image = filename
        init_images(filename, self.random_rot, self.RotCombine, self.ImageCombo)
        if self.current_Object.collected():
            self.current_Object.set_voxel_images()
        elif self.VoxelBased:
            self.current_Object.voxels()[voxel].set_images()
        else:
            self.current_Object.set_images()
        self.update_frame(self.objectList)

    def empty_background(self):
        background = Image.new("RGBA", (canvas_w, canvas_h))
        self.empty_background = ImageTk.PhotoImage(background)

    def set_background(self, filename = None, url_dialog = False):
        if filename is None:
            if url_dialog:
                self.open_Url_Filename(self.set_background)
                return
            else:
                currentDir = os.path.dirname(self.background_filename)
                print("currentDir", currentDir)
                if currentDir == "":
                    currentDir = os.path.join(folders, back_pic)
                filename = askopenfilename(initialdir = currentDir,
                                            filetypes = myFormats)
        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            if validators.url(filename):
                if internetOn:
                    f = cStringIO.StringIO(urllib.urlopen(filename).read())
                    try:
                        img1 = Image.open(f)
                    except(Exception) as detail:
                        print(detail)
                        return
                else:
                    return
            else:
                filename = os.path.normpath(filename)
                print(filename)
                try:
                    filename = os.path.relpath(filename).replace("\\","/")
                except:
                    print("using absolute path")

                filename = self.validate_filename(filename)
                if not os.path.exists(filename):
                    return
                img1 = Image.open(filename)
            self.background_filename = filename
        if img1.size[0] != canvas_w or img1.size[1] != canvas_h:
            if canvas_w / float(img1.size[0]) < canvas_h / float(img1.size[1]):
                mult = canvas_h / float(img1.size[1])
            else:
                mult = canvas_w / float(img1.size[0])
            w = int(img1.size[0] * mult)
            h = int(img1.size[1] * mult)
            img1 = img1.resize((w, h), Image.ANTIALIAS)
        if img1.mode != 'RGBA':
            img1 = img1.convert("RGBA")
        background = Image.new("RGBA", (canvas_w, canvas_h))
        background.paste(img1, (0, 0))
        self.backgroundImage = background
        backgroundName = cmd_folder + "/background.png"
        background.save(backgroundName)
        self.Screen.createBackgroundSurface(self.backgroundImage)
        self.Screen.BackgroundImage = backgroundName
        if self.SDL_bind:
            self.Screen.Background_texture = self.Screen.createBackground(backgroundName)

        (R, G, B, A) = background.split()
        self.backgroundAlpha = A
        image = ImageTk.PhotoImage(background)

        self.background_Image = image
        self.canvas.delete("BackGround")
        self.canvas.create_image(0, 0, image = self.background_Image, anchor = tk.NW, tags = "BackGround")
        self.canvas.tag_lower("BackGround")
        self.canvas.update()
        self.update_frame(self.objectList)

    def clean_Ground(self):
        self.current_Object.clean_Ground()
        self.update_frame(self.objectList)

    def set_ground_pic(self, filename = None, update = True, sceneLoad = True, Object = None, url_dialog = False):
        if filename is None:
            if url_dialog:
                self.open_Url_Filename(lambda f = None: self.set_ground_pic(f, sceneLoad = sceneLoad))
                return
            else:
                currentDir = os.path.dirname(self.groundImage)
                print("currentDir", currentDir)
                if currentDir == "":
                    currentDir = os.path.join(folders, ground_image)
                filename = askopenfilename(initialdir = currentDir,
                                            filetypes = myFormats)
        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            if not validators.url(filename):
                filename = os.path.normpath(filename)
                print(filename)
                try:
                    filename = os.path.relpath(filename).replace("\\","/")
                except:
                    print("using absolute path")
                filename = self.validate_filename(filename)
                if not os.path.exists(filename):
                    return
            elif not internetOn:
                return
        else:
            return
        if sceneLoad:
            self.groundImage = filename
            self.Screen.GroundImage = filename
            if self.SDL_bind:
                self.Screen.create_Ground(self.Screen.GroundImage)
        else:
            if Object is None:
                Object = self.current_Object
            Object.set_Ground(filename)
            self.Screen.setup_Objects_Ground([Object])
        if update:
            self.update_frame(self.objectList)

    def set_object(self, A):
        self.get_dimension()
        A1 = self.current_Object.animated_Cube()
        (X1, Y1, Z1) = A1.shape
        global Xdim, Ydim, Zdim
        (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
        a = ones((Xdim, Ydim, Zdim, 2), dtype = object)
        (X, Y, Z, T) = a.shape
        if X > A1.shape[0]:
            self.setup_numpy([self.current_Object,])
            self.get_dimension()
            (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
            a = ones((Xdim, Ydim, Zdim, 2), dtype = object)
            (X, Y, Z, T) = a.shape

        level = self.level.get()
        size = level * 2.0
        c = float(self.dim) / 2.0
        a1 = self.AlphaEntryVar1.get()
        a2 = self.AlphaEntryVar2.get()
        (M2, N2) = self.func_0_1(255, a2)
        (M1, N1) = self.func_0_1(255, a1)
        self.clear_highlight()
        if self.fitPlace:
            step_x = X1 / float(Xdim)
            step_y = Y1 / float(Ydim)
            step_z = Z1 / float(Zdim)
            X_start = 0
            Y_start = 0
            Z_start = 0
        else:
            step_x = 1
            step_y = 1
            step_z = 1
            X_start = Xbound[0]
            Y_start = Ybound[0]
            Z_start = Zbound[0]
        x1 = 0
        for x in range(X):
            y1 = 0
            for y in range(Y):
                z1 = 0
                for z in range(Z):
                    s = A[x1 + X_start, y1 + Y_start, z1 + Z_start]
                    (m, n) = self.func_0_1(size, s[0])
                    if s[1]:
                        a[x, y, z][1] = (s[1][0], s[1][1], s[1][2])
                    elif self.setColor:
                        v = A1[x1 + X_start, y1 + Y_start, z1 + Z_start]
                        color = self.current_Object[v].color
                        fgcolor =       (self.fgcolor[0] * M2 + color[0] * N2,
                                         self.fgcolor[1] * M2 + color[1] * N2,
                                         self.fgcolor[2] * M2 + color[2] * N2)
                        bgcolor =       (self.bgcolor[0] * M1 + color[0] * N1,
                                         self.bgcolor[1] * M1 + color[1] * N1,
                                         self.bgcolor[2] * M1 + color[2] * N1)
                        a[x, y, z][1] = (fgcolor[0] * m + bgcolor[0] * n,
                                         fgcolor[1] * m + bgcolor[1] * n,
                                         fgcolor[2] * m + bgcolor[2] * n)
                    else:
                        a[x, y, z][1] = None
                    if self.setShape:
                        S2 = size * M2
                        S1 = size * N1
                        a[x, y, z][0] = S2 * m + S1 * n
                    else:
                        a[x, y, z][0] = None
                    z1 += step_z
                y1 += step_y
            x1 += step_x

        self.current_Object.load_frame(a, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
        self.write_key_frame()
        self.update_object_frame(self.objectList)

    def func_0_1(self, radius, l):
        m = abs(l / float(radius))
        if m > 1.0:
            m = 1.0
        if m <= 1.0:
            n = 1.0 - m
        else:
            n = m - 1.0
            m = 1.0 - n
        return (m, n)

    def revolve_OBJ(self, step):
        if len(self.AnimSequence) < 1:
            print("fill animation first!")
            return
        if self.obj_transform == None:
            return

        self.stop_animation()
        self.stop_Rotation()

        raster_begin   = self.raster_begin
        raster_end     = self.raster_end
        raster_step    = self.raster_step
        raster_revolve = float(self.raster_revolve) * pi * 2.0

        length = raster_end - raster_begin
        animLength = length / raster_step
        self.setup_progress(animLength)
        angle = raster_revolve / float(animLength)
        self.Time = raster_begin
        A = 0
        for i in range(raster_begin, raster_end, raster_step):
            self.place_transformed_object(A)
            A += angle
            self.Time += raster_step
            if self.progressbar == None:
                return
            else:
                self.progressbar.advance()
        self.quit_progress()
        self.CVar2.set(str(len(self.AnimSequence)) + " frames rasterised")

    def reload_object_repro(self):
        print("reload_object_repro")
        collected = self.current_Object.collected()
        if collected:
            levelVoxels = collected
        elif self.VoxelBased_repro:
            levelVoxels = [self.current_Object.voxels()[self.currentVoxel],]
        else:
            levelVoxels = [self.current_Object,]

        self.setup_progress(len(levelVoxels))
        c = 0
        texNamesList = {}
        for i in levelVoxels:
            try:
                pathname = i.repro()
            except:
                pathname = i.repro
            d = i.return_Pos_And_Scale()
            r = i.return_Wire_Render()
            if pathname and os.path.isfile(pathname):
                repro = pathname
                if pathname not in self.objtransformList:
                    Faces = []
                    Verts = []
                    Norms = []
                    faces = obj_loader.load(pathname)
                    print("polys", len(faces))
                    if i == self.current_Object:
                        rep = i.OBJ_repro()
                    else:
                        rep = i.OBJ_repro
                    if rep and rep.Frames > 1:
                        Faces, Verts, Norms = obj_loader.load_Faces(pathname, self.progressbar, False)
                    OBJ_repro = obj_loader.obj_transform(faces, Faces, Verts, Norms)
                    OBJ_repro.tune_Position_And_Scale(d)
                    OBJ_repro.tune_Wire_Render(r)
                    self.Screen.objFileNames[pathname] = OBJ_repro
                    self.Screen.obj_transforms.append(OBJ_repro)
                    self.objtransformList[pathname] = OBJ_repro
                else:
                    OBJ_repro = self.objtransformList[pathname]
            else:
                repro = None
                OBJ_repro = None

            if self.progressbar == None:
                return
            else:
                self.progressbar.advance()

            texture = None
            texName = None
            image = None
            if self.useMtl and pathname:
                print("using mtl file data!")
                if pathname[-3:] == "obj":
                    filename1 = pathname.replace(".obj", ".mtl")
                elif pathname[-3:] == "OBJ":
                    filename1 = pathname.replace(".OBJ", ".mtl")
                else:
                    filename1 = ""
                if os.path.exists(filename1):
                    f = open(filename1, "r")
                    lines = f.readlines()
                    while(lines):
                        p = lines.pop()
                        if p[:6] == "map_Kd":
                            image = p[7:]
                            image = image.rstrip()
                            break
                    f.close()
                    print(image)

            if image is not None:
                texName = image.replace("\\", "/")
                (path, name) = os.path.split(texName)
                print(path)
                if os.path.exists(path):
                    self.textures_folder = path
                    if self.Textures and self.Screen.SDL_Mode:
                        if texName in self.Screen.texNamesList and self.useLoaded:
                            texture = self.Screen.texNamesList[texName]
                        elif texName in texNamesList:
                            texture = texNamesList[texName]
                        else:
                            texture = self.Screen.TexFromPNG(texName)
                            texNamesList[texName] = texture

            i.set_repro(repro, OBJ_repro, texture, texName)

            if self.SDL_bind and OBJ_repro:
                if self.Screen.VBO:
                    if not OBJ_repro.VBO:
                        OBJ_repro.set_up_vertex_array()
                elif not OBJ_repro.objdisplayList:
                    OBJ_repro.set_up_display_list()

        self.objtransformList = {}

        self.quit_progress()

        self.write_objects_pic(PICC, True)
        self.update_object_frame(self.objectList)

    def load_object_repros(self, filenames = None):
        print("load_object_repros")
        if not self.SDL_bind:
            self.toggle_SDL_Mode(False)

        if filenames is None:
            self.files_folder = askdirectory(title = "Choose Files Directory", initialdir = self.files_folder)

            if os.path.isdir(self.files_folder):
                dirs = []
                objList = []
                try:
                    dirs = os.listdir(self.files_folder)
                    dirs.sort()
                except(Exception) as detail:
                    print('EXC0')
                    return

                for i in dirs:
                    if i[-3:] == "obj":
                        objList.append(i)
            else:
                return
            if not objList:
                return
        else:
            (path, name) = os.path.split(filenames[-1])
            objList = []
            for i in filenames:
                (path1, name1) = os.path.split(i)
                if (path1 == path) and (name1[-3:] == "obj" or name1[-3:] == "OBJ"):
                    objList.append(name1)
            self.files_folder = path
            if not objList:
                return

        collected = self.current_Object.collected()
        if collected:
            levelVoxels = collected
        elif self.VoxelBased_repro:
            levelVoxels = self.current_Object.return_levelVoxels(self.currentVoxel)
        else:
            levelVoxels = self.current_Object.return_levelVoxels(self.currentVoxel)

        self.setup_progress(len(levelVoxels))
        c = 0
        for i in levelVoxels:
            c += 1
            if c >= len(objList):
                c = 0
            filename = objList[c]
            pathname = os.path.join(self.files_folder, filename)
            pathname = pathname.replace("\\", "/")
            self.repro = pathname

            if self.progressbar == None:
                return
            else:
                self.progressbar.advance()
                try:
                    self.progressbar.set_msg1(filename)
                except(Exception) as detail:
                    print(detail)

            if pathname in self.Screen.objFileNames and self.useLoaded:
                self.OBJ_repro = self.Screen.objFileNames[pathname]
            else:
                faces = obj_loader.load(pathname)
                print("polys", len(faces))
                self.OBJ_repro = obj_loader.obj_transform(faces)
                self.Screen.objFileNames[pathname] = self.OBJ_repro
                self.Screen.obj_transforms.append(self.OBJ_repro)

            texture = None
            texName = None
            image = None
            if self.useMtl:
                print("using mtl file data!")
                filename1 = pathname.replace(".obj", ".mtl")
                if os.path.exists(filename1):
                    f = open(filename1, "r")
                    lines = f.readlines()
                    while(lines):
                        p = lines.pop()
                        if p[:6] == "map_Kd":
                            image = p[7:]
                            image = image.rstrip()
                            break
                    f.close()
                    print(image)

            if image is not None:
                texName = image.replace("\\", "/")
                (path, name) = os.path.split(texName)
                print(path)
                if os.path.exists(path):
                    self.textures_folder = path
                    if self.Textures and self.Screen.SDL_Mode:
                        if texName in self.Screen.texNamesList and self.useLoaded:
                            texture = self.Screen.texNamesList[texName]
                        else:
                            texture = self.Screen.TexFromPNG(texName)

            self.texture = texture
            self.texName = texName

            i.set_repro(self.repro, self.OBJ_repro, texture, texName)

            if self.SDL_bind and self.OBJ_repro:
                if self.Screen.VBO:
                    if not self.OBJ_repro.VBO:
                        self.OBJ_repro.set_up_vertex_array()
                elif not self.OBJ_repro.objdisplayList:
                    self.OBJ_repro.set_up_display_list()

        self.quit_progress()

        self.write_objects_pic(PICC, True)
        self.update_object_frame(self.objectList)
        self.root.event_generate("<FocusIn>", when="tail")

    def load_object_repro(self, filename = None, voxel = None, local = None):
        print("load_object_repro")
        if not self.SDL_bind:
            self.toggle_SDL_Mode(False)

        if local == None:
            Object = self.current_Object
        else:
            Object = local

        if filename == None:
            filename = askopenfilename(initialdir = self.files_folder,
                                        filetypes = (("Object files", "*.obj *.OBJ")
                                                         ,("Template files", "*.tplate")
                                                         ,("HTML files", "*.html *.htm")
                                                         ,("All files", "*.*") ))
        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        if not os.path.exists(filename):
            return
        if voxel == None:
            voxel = self.currentVoxel
        self.files_folder = os.path.dirname(filename)

        self.repro = filename
        if filename in self.Screen.objFileNames and self.useLoaded:
            self.OBJ_repro = self.Screen.objFileNames[filename]
        else:
            faces = obj_loader.load(filename)
            print("polys", len(faces))
            self.OBJ_repro = obj_loader.obj_transform(faces)
            self.Screen.objFileNames[filename] = self.OBJ_repro
            self.Screen.obj_transforms.append(self.OBJ_repro)

        texture = None
        texName = None
        image = None
        if self.useMtl:
            print("using mtl file data!")
            filename1 = ""
            if filename[-3:] == "obj":
                filename1 = filename.replace(".obj", ".mtl")
            elif filename[-3:] == "OBJ":
                filename1 = filename.replace(".OBJ", ".mtl")
            if os.path.exists(filename1):
                f = open(filename1, "r")
                lines = f.readlines()

                while(lines):
                    p = lines.pop()
                    if p[:6] == "map_Kd":
                        image = p[7:]
                        image = image.rstrip()
                        break
                f.close()
                print(image)

        if image is not None:
            texName = image.replace("\\", "/")
            (path, name) = os.path.split(texName)
            print(path)
            if os.path.exists(path):
                self.textures_folder = path
                if self.Textures and self.Screen.SDL_Mode:
                    if texName in self.Screen.texNamesList and self.useLoaded:
                        texture = self.Screen.texNamesList[texName]
                    else:
                        texture = self.Screen.TexFromPNG(texName)

        self.texture = texture
        self.texName = texName
        if Object.collected():
            Object.set_voxel_repro(self.repro, self.OBJ_repro, texture, texName)
        elif self.VoxelBased_repro:
            Object.voxels()[voxel].set_repro(self.repro, self.OBJ_repro, texture, texName)
        else:
            Object.set_repro(self.repro, self.OBJ_repro, texture, texName)
        if self.SDL_bind and self.OBJ_repro:
            if self.Screen.VBO:
                if not self.OBJ_repro.VBO:
                    self.OBJ_repro.set_up_vertex_array()
            elif not self.OBJ_repro.objdisplayList:
                self.OBJ_repro.set_up_display_list()

        self.write_objects_pic(PICC, True)
        self.update_frame(self.objectList)

    def load_animated_repro(self):
        print("load_animated_repro")
        if not self.SDL_bind:
            self.toggle_SDL_Mode(False)

        filename = askopenfilename(initialdir = self.files_folder,
                                    filetypes = (("Object files", "*.obj *.OBJ")
                                                     ,("Template files", "*.tplate")
                                                     ,("HTML files", "*.html *.htm")
                                                     ,("All files", "*.*") ))
        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        if not os.path.exists(filename):
            return
        self.files_folder = os.path.dirname(filename)

        self.repro = filename
        if filename in self.Screen.objFileNames and self.useLoaded and self.Screen.objFileNames[filename].Frames > 1:
            self.OBJ_repro = self.Screen.objFileNames[filename]
        else:
            (path, name) = os.path.split(filename)
            extension = name[-3:]
            R = re.match(r'(\D*)(\d*)', name)

            F = 0

            if os.path.isdir(path):
                dirs = []
                try:
                    dirs = os.listdir(path)
                    dirs.sort()
                except(Exception) as detail:
                    print('EXC0')
                    return

                for i in dirs:
                    if i[-3:] == extension:
                        if R.group(2):
                            if R.group(1) == i[:len(R.group(1))]:
                                F += 1

            if F == 0:
                return

            self.setup_progress(F)
            Faces, Verts, Norms = obj_loader.load_Faces(filename, self.progressbar, True)
            self.quit_progress()
            faces = obj_loader.load(filename)
            print("polys", len(faces))
            self.OBJ_repro = obj_loader.obj_transform(faces, Faces, Verts, Norms)
            self.Screen.objFileNames[filename] = self.OBJ_repro
            self.Screen.obj_transforms.append(self.OBJ_repro)

        texture = None
        texName = None
        image = None
        if self.useMtl:
            print("using mtl file data!")
            if filename[-3:] == "obj":
                filename1 = filename.replace(".obj", ".mtl")
            elif filename[-3:] == "OBJ":
                filename1 = filename.replace(".OBJ", ".mtl")
            else:
                filename1 = ""
            if os.path.exists(filename1):
                f = open(filename1, "r")
                lines = f.readlines()

                while(lines):
                    p = lines.pop()
                    if p[:6] == "map_Kd":
                        image = p[7:]
                        image = image.rstrip()
                        break
                f.close()
                print(image)

        if image is not None:
            texName = image.replace("\\", "/")
            (path, name) = os.path.split(texName)
            print(path)
            if os.path.exists(path):
                self.textures_folder = path
                if self.Textures and self.Screen.SDL_Mode:
                    if texName in self.Screen.texNamesList and self.useLoaded:
                        texture = self.Screen.texNamesList[texName]
                    else:
                        texture = self.Screen.TexFromPNG(texName)

        self.texture = texture
        self.texName = texName
        if self.current_Object.collected():
            self.current_Object.set_voxel_repro(self.repro, self.OBJ_repro, texture, texName)
        elif self.VoxelBased_repro:
            self.current_Object.voxels()[self.currentVoxel].set_repro(self.repro, self.OBJ_repro, texture, texName)
        else:
            self.current_Object.set_repro(self.repro, self.OBJ_repro, texture, texName)
        if self.SDL_bind and self.OBJ_repro:
            if self.Screen.VBO:
                if not self.OBJ_repro.VBO:
                    self.OBJ_repro.set_up_vertex_array()
            elif not self.OBJ_repro.objdisplayList:
                self.OBJ_repro.set_up_display_list()

        self.write_objects_pic(PICC, True)
        self.update_frame(self.objectList)

    def load_object(self, filename = None, force = False):
        print("load_object")
        if not filename:
            filename = askopenfilename(initialdir = self.files_folder,
                                        filetypes = (("Object files", "*.obj *.OBJ")
                                                         ,("Template files", "*.tplate")
                                                         ,("HTML files", "*.html *.htm")
                                                         ,("All files", "*.*") ))
        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        if not os.path.exists(filename):
            return
        self.files_folder = os.path.dirname(filename)

        if  not force and filename in self.Screen.objFileNames and self.useLoaded:
            print("filename exists")
            self.lock.acquire()
            self.obj_transform = self.Screen.objFileNames[filename]
            self.lock.release()
            self.faces = self.obj_transform.faces
        else:
            self.lock.acquire()
            self.faces = obj_loader.load(filename)
            self.lock.release()
            print("polys", len(self.faces))
##            self.faces = obj_loader.qualify(faces)
##            print("polys", len(self.faces))
            self.obj_transform = obj_loader.obj_transform(self.faces)
            self.Screen.objFileNames[filename] = self.obj_transform
            self.Screen.obj_transforms.append(self.obj_transform)
        if self.SDL_bind and self.obj_transform:
            if self.Screen.VBO:
                if not self.obj_transform.VBO:
                    self.obj_transform.set_up_vertex_array()
            elif not self.obj_transform.objdisplayList:
                self.obj_transform.set_up_display_list()

        if self.useMtl:
            print("using mtl file data!")
            if filename[-3:] == "obj":
                filename = filename.replace(".obj", ".mtl")
            elif filename[-3:] == "OBJ":
                filename = filename.replace(".OBJ", ".mtl")
            if os.path.exists(filename):
                f = open(filename, "r")
                lines = f.readlines()
                image = None
                while(lines):
                    p = lines.pop()
                    if p[:6] == "map_Kd":
                        image = p[7:]
                        image = image.rstrip()
                        break
                f.close()
                print(image)
                if image is not None:
                    filename = image.replace("\\", "/")
                    (path, name) = os.path.split(filename)
                    print(path)
                    if os.path.exists(path):
                        self.textures_folder = path
                        self.Screen.image = filename
                        if self.Textures and self.Screen.SDL_Mode:
                            self.Screen.setup_Texture()

        self.Screen.set_OBJ_Mode(self.OBJ_bind, self.obj_transform)
        self.update_object_frame(self.objectList)

    def place_texture(self):
        print("place_texture")
        filename = askopenfilename(initialdir = self.textures_folder,
                                    filetypes = myFormats)
        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            filename = os.path.normpath(filename)
            print(filename)
            try:
                filename = os.path.relpath(filename).replace("\\","/")
            except:
                print("using absolute path")
        else:
            return
        (path, name) = os.path.split(filename)
        if os.path.exists(path):
            self.textures_folder = path
            self.Screen.image = filename
            if self.Textures and self.Screen.SDL_Mode:
                self.Screen.setup_Texture()
        self.update_frame(self.objectList)

    def place_voxel_texture(self, filename = None, voxel = None, url_dialog = False):
        print("place_texture")
        if filename is None:
            if url_dialog:
                self.open_Url_Filename(self.place_voxel_texture)
                return
            else:
                filename = askopenfilename(initialdir = self.textures_folder,
                                            filetypes = myFormats)
        print(filename)
        try:
            l = len(filename)
        except:
            l = len(str(filename))
        if l > 0:
            if not validators.url(filename):
                filename = os.path.normpath(filename)
                print(filename)
                try:
                    filename = os.path.relpath(filename).replace("\\","/")
                except:
                    print("using absolute path")
                (path, name) = os.path.split(filename)
                if os.path.exists(path):
                    self.textures_folder = path
            elif not internetOn:
                return

            texture = None

            if self.SDL_bind:
                if filename in self.Screen.texNamesList and self.useLoaded:
                    texture = self.Screen.texNamesList[filename]
                else:
                    texture = self.Screen.TexFromPNG(filename, force = True)

            self.texture = texture
            self.texName = filename

            if self.current_Object.collected():
                self.current_Object.set_voxel_texture(texture, self.texName)
                repro = None
            elif self.VoxelBased_repro:
                self.current_Object.set_voxel_texture(texture, self.texName, voxel)
                repro = self.current_Object.voxels()[voxel].repro
            else:
                self.current_Object.set_texture(texture, self.texName)
                repro = self.current_Object.repro()

            if self.useMtl and repro:
                try:
                    (path, name) = os.path.split(repro)
                    name = name.replace(".obj", ".mtl")
                    mtl_file = os.path.join(path, name)
                    f = open(mtl_file, "a")
                    f.write("\n")
                    f.write("map_Kd " + filename)
                    f.close()
                    print("mtl file appended." + str(mtl_file))
                except:
                    print("mtl file not appended!")

            self.write_objects_pic(PICC, True)
            self.update_frame(self.objectList)

    def place_voxel_textures(self, filenames = None):
        print("place_textures")
        if filenames is None:
            filename = askopenfilename(initialdir = self.textures_folder,
                                        filetypes = myFormats)
            print(filename)
            try:
                l = len(filename)
            except:
                l = len(str(filename))
            if l > 0:
                filename = os.path.normpath(filename)
                print(filename)
                try:
                    filename = os.path.relpath(filename).replace("\\","/")
                except:
                    print("using absolute path")
            else:
                return

            (path, name) = os.path.split(filename)
            extension = name[-3:]

            if os.path.isdir(path):
                dirs = []
                texList = []
                try:
                    dirs = os.listdir(path)
                    dirs.sort()
                except(Exception) as detail:
                    print('EXC0')
                    return

                for i in dirs:
                    if i[-3:] == extension:
                        texList.append(i)
            else:
                return
        else:
            (path, name) = os.path.split(filenames[-1])
            extension = name[-3:]
            texList = []
            for i in filenames:
                (path1, name1) = os.path.split(i)
                if name1[-3:] == extension:
                    texList.append(name1)

        if not texList:
            return

        self.textures_folder = path
        texture = None

        collected = self.current_Object.collected()
        if collected:
            levelVoxels = collected
        else:
            levelVoxels = self.current_Object.return_levelVoxels(self.currentVoxel)

        self.setup_progress(len(levelVoxels))
        c = 0
        for i in levelVoxels:
            c += 1
            if c >= len(texList):
                c = 0
            filename = texList[c]
            pathname = os.path.join(self.textures_folder, filename)
            pathname = pathname.replace("\\", "/")
            self.texture = pathname

            if self.progressbar == None:
                return
            else:
                self.progressbar.advance()
                try:
                    self.progressbar.set_msg1(filename)
                except(Exception) as detail:
                    print(detail)

            if self.SDL_bind:
                if pathname in self.Screen.texNamesList and self.useLoaded:
                    texture = self.Screen.texNamesList[pathname]
                else:
                    texture = self.Screen.TexFromPNG(pathname)

            self.texture = texture
            self.texName = pathname

            i.set_texture(texture, self.texName)

        self.quit_progress()
        self.write_objects_pic(PICC, True)
        self.update_frame(self.objectList)

    def toggle_textures(self, update = True):
        if self.SDL_bind:
            self.Textures = not self.Textures
            self.Screen.setup_Texture()
            self.Screen.set_Texture(self.Textures)
        self.TexturesVar.set(self.Textures)
        if update:
            self.update_frame(self.objectList)

    def place_transformed_object(self, angle = None, x = 0, y = 0, z = 0,
                                 symX = 0, symY = 0, symZ = 0):
        self.setup_numpy([self.current_Object,])
        if self.obj_transform:
            self.obj_transform.get_transformed(angle, x, y, z)
            faces = self.obj_transform.Tfaces
            uvfaces = self.obj_transform.faces
            self.get_dimension()
            level = self.level.get()
            size = level * 2.0
            texture = self.Screen.image
            A = scan_object.scan(self.dim, size, faces, uvfaces, texture)
            dim2 = self.dim // 2

            if symX < 0:
                X = self.dim
                for x in range(0, dim2):
                    X -= 1
                    for y in range(0, self.dim):
                        for z in range(0, self.dim):
                            s = A[x, y, z]
                            A[X, y, z] = s

            elif symX > 0:
                X = dim2
                for x in range(dim2, self.dim):
                    X -= 1
                    for y in range(0, self.dim):
                        for z in range(0, self.dim):
                            s = A[x, y, z]
                            A[X, y, z] = s
            if symY < 0:
                Y = self.dim
                for y in range(0, dim2):
                    Y -= 1
                    for x in range(0, self.dim):
                        for z in range(0, self.dim):
                            s = A[x, y, z]
                            A[x, Y, z] = s

            elif symY > 0:
                Y = dim2
                for y in range(dim2, self.dim):
                    Y -= 1
                    for x in range(0, self.dim):
                        for z in range(0, self.dim):
                            s = A[x, y, z]
                            A[x, Y, z] = s
            if symZ < 0:
                Z = self.dim
                for z in range(0, dim2):
                    Z -= 1
                    for y in range(0, self.dim):
                        for x in range(0, self.dim):
                            s = A[x, y, z]
                            A[x, y, Z] = s

            elif symZ > 0:
                Z = dim2
                for z in range(dim2, self.dim):
                    Z -= 1
                    for y in range(0, self.dim):
                        for x in range(0, self.dim):
                            s = A[x, y, z]
                            A[x, y, Z] = s
            self.set_object(A)

    def place_object(self):
        print("place_object")
        if self.faces:
            self.get_dimension()
            level = self.level.get()
            size = level * 2.0
            texture = self.Screen.image
            A = scan_object.scan(self.dim, size, self.faces, self.faces, texture)
            self.set_object(A)

    def play_TEXTURE_directory(self):
        self.textures_folder = askdirectory(title = "Choose Files Directory", initialdir = self.textures_folder)
        if os.path.isdir(self.textures_folder):
            dirs = []
            textueList = []
            try:
                dirs = os.listdir(self.textures_folder)
                dirs.sort()
            except(Exception) as detail:
                print('EXC0')
                return

            for i in dirs:
                if (i[-3:] == "png" or i[-3:] == "PNG" or
                    i[-3:] == "jpg" or i[-3:] == "JPG"):
                    textueList.append(i)

            if not textueList:
                return

            if len(self.AnimSequence) < 1:
                print("fill animation first!")
                return

            self.stop_animation()
            self.stop_Rotation()

            raster_begin   = self.raster_begin
            raster_end     = self.raster_end
            raster_step    = self.raster_step
            raster_revolve = float(self.raster_revolve) * pi * 2.0

            length = raster_end - raster_begin
            animLength = length / raster_step
            self.setup_progress(animLength)
            self.Time = raster_begin
            n = 0
            A = self.current_Object.cube3d().angle
            for i in range(raster_begin, raster_end, raster_step):
                filename = textueList[n]
                pathname = os.path.join(self.textures_folder, filename)
                pathname = pathname.replace("\\", "/")
                print(pathname)
                n += 1
                if n >= len(textueList):
                    n = 0
                if not self.obj_transform:
                    continue

                (path, name) = os.path.split(pathname)
                if os.path.exists(path):
                    self.Screen.image = pathname
                    if self.Textures and self.Screen.SDL_Mode:
                        self.Screen.setup_Texture()

                self.place_transformed_object(A)
                self.Time += raster_step
                if self.progressbar == None:
                    return
                else:
                    self.progressbar.advance()
            self.quit_progress()
            self.CVar2.set(str(len(self.AnimSequence)) + " frames rasterised")

    def play_OBJ_directory(self):
        self.files_folder = askdirectory(title = "Choose Files Directory", initialdir = self.files_folder)
        if os.path.isdir(self.files_folder):
            dirs = []
            objList = []
            try:
                dirs = os.listdir(self.files_folder)
                dirs.sort()
            except(Exception) as detail:
                print('EXC0')
                return

            for i in dirs:
                if i[-3:] == "obj":
                    objList.append(i)

            if not objList:
                return

            if len(self.AnimSequence) < 1:
                print("fill animation first!")
                return

            self.stop_animation()
            self.stop_Rotation()

            raster_begin   = self.raster_begin
            raster_end     = self.raster_end
            raster_step    = self.raster_step
            raster_revolve = float(self.raster_revolve) * pi * 2.0

            length = raster_end - raster_begin
            animLength = length / raster_step
            self.setup_progress(animLength)
            angle = raster_revolve / float(animLength)
            self.Time = raster_begin
            A = 0
            n = 0
            for i in range(raster_begin, raster_end, raster_step):
                filename = objList[n]
                pathname = os.path.join(self.files_folder, filename)
                pathname = pathname.replace("\\", "/")
                print(pathname)
                n += 1
                if n >= len(objList):
                    n = 0

                faces = obj_loader.load(pathname)
                self.faces = obj_loader.qualify(faces)
                print("polys", len(self.faces))
                self.obj_transform = obj_loader.obj_transform(self.faces)
                if not self.obj_transform:
                    continue
                if self.useMtl:
                    print("using mtl file data!")
                    if pathname[-3:] == "obj":
                        pathname = pathname.replace(".obj", ".mtl")
                    elif pathname[-3:] == "OBJ":
                        pathname = pathname.replace(".OBJ", ".mtl")
                    if os.path.exists(pathname):
                        f = open(pathname, "r")
                        lines = f.readlines()
                        image = None
                        while(lines):
                            p = lines.pop()
                            if p[:6] == "map_Kd":
                                image = p[7:]
                                image = image.rstrip()
                                break
                        f.close()
                        print(image)
                        if image is not None:
                            filename = image.replace("\\", "/")
                            (path, name) = os.path.split(filename)
                            print(path)
                            if os.path.exists(path):
                                self.Screen.image = filename
                                if self.Textures and self.Screen.SDL_Mode:
                                    self.Screen.setup_Texture()
                            else:
                                self.Screen.clean_Texture()

                self.Screen.set_OBJ_Mode(self.OBJ_bind, self.obj_transform)
                self.place_transformed_object(A)
                A += angle
                self.Time += raster_step
                if self.progressbar == None:
                    return
                else:
                    self.progressbar.advance()
            self.quit_progress()
            self.CVar2.set(str(len(self.AnimSequence)) + " frames rasterised")

    def toggle_OBJ_Mode(self):
        if not self.localCenter:
            self.local_Center.set(True)
            self.toggle_local_Center()
        self.OBJ_bind = not self.OBJ_bind
        self.OBJ_Mode.set(self.OBJ_bind)
        self.Screen.set_OBJ_Mode(self.OBJ_bind, self.obj_transform)

        if self.OBJ_bind:
            for i in self.ObjectList:
                i.cube3d().set_LOCAL(True)
                i.cube3d().localize(None)
                i.cube3d().center = i.give_center_parent(-1)
            if self.SDL_bind and self.obj_transform:
                if self.Screen.VBO:
                    if not self.obj_transform.VBO:
                        self.obj_transform.set_up_vertex_array()
                elif not self.obj_transform.objdisplayList:
                    self.obj_transform.set_up_display_list(self.Screen.polyDraw)
            vector = self.current_Object.cube3d().local
            self.angle = self.current_Object.cube3d().angle
            self.EntryVar.set("%d %d %d" % vector)
        else:
            vector = self.current_Object.local()
            self.angle = self.current_Object.angle()
            self.EntryVar.set(vector)
        self.update_object_frame(self.objectList)

    def toggle_Depth_Mode(self):
        self.GL_depth_cued = not self.GL_depth_cued
        self.Depth_Mode.set(self.GL_depth_cued)
        for i in self.objectList:
            i.set_depth_cued(self.GL_depth_cued)
        self.update_frame(self.objectList)

    def toggle_Tween(self):
        self.VBOTween = not self.VBOTween
        self.Screen.set_Tween(self.VBOTween)
        self.VBO_Tween.set(self.VBOTween)

    def toggle_Frames(self):
        self.VBOFrames = not self.VBOFrames
        self.Screen.set_Frames(self.VBOFrames)
        self.VBO_Frames.set(self.VBOFrames)

    def toggle_VBO(self):
        self.VBO = not self.VBO
        self.VBO = self.Screen.set_VBO(self.VBO)
        self.VBO_Mode.set(self.VBO)

    def toggle_WireFrame(self):
        self.WireFrame = not self.WireFrame
        self.GL_WireFrame.set(self.WireFrame)
        self.Screen.set_Geometry(self.WireFrame)
        self.update_frame(self.objectList)

    def toggle_Wire(self, mode = None):
        if mode == "Off":
            self.OBJ_Wire = False
        else:
            self.OBJ_Wire = not self.OBJ_Wire
        self.GL_Wire.set(self.OBJ_Wire)
        self.Screen.set_Wireframe(self.OBJ_Wire)
        if self.SDL_bind and self.obj_transform:
            self.obj_transform.set_up_display_list(self.Screen.polyDraw)
        self.update_frame(self.objectList)

    def toggle_Lightsource(self, source):
        if self.SDL_bind:
            self.Screen.set_LightSource(source)
            self.update_frame(self.objectList)

    def toggle_Lights(self):
        if self.SDL_bind:
            self.Lights = not self.Lights
            self.Screen.set_Lights(self.Lights)
            self.update_frame(self.objectList)
        self.GL_Lights.set(self.Lights)

    def toggle_Background(self):
        self.Background = not self.Background
        self.Background_Mode.set(self.Background)
        self.update_frame(self.objectList)

        if self.Background:
            image = self.background_Image
        else:
            image = self.empty_background
        self.canvas.delete("BackGround")
        self.canvas.create_image(0, 0, image = image, anchor = tk.NW, tags = "BackGround")
        self.canvas.tag_lower("BackGround")
        self.canvas.update()

    def toggle_GroundAll(self, update = True, mode = None):
        if mode is None:
            self.groundAll = not self.groundAll
        else:
            self.groundAll = mode
        self.GroundAll.set(self.groundAll)
        if update:
            self.update_frame(self.objectList)

    def toggle_local_Ground(self, mode = None, local = None, update = True):
        if local is None:
            local = self.current_Object
        if mode is None:
            ground = local.draw_Ground()
            ground = not ground
        else:
            ground = mode
        local.set_draw_ground(ground)
        if update:
            self.update_frame(self.objectList)

    def tunein_Ground(self):
        for x, i in zip(self.GroundList, self.ObjectList):
            i.set_draw_ground(x)

    def toggle_Ground(self, mode = None, update = True):
        if mode is not None:
            self.Ground = mode
        else:
            self.Ground = not self.Ground
        self.Ground_Mode.set(self.Ground)
        for i in self.ObjectList:
            i.set_draw_ground(self.Ground)
        if update:
            self.update_frame(self.objectList)

    def toggle_Shadows(self, mode = None, update = True):
        if mode is not None:
            self.Shadows = mode
        else:
            self.Shadows = not self.Shadows
        self.Shadow_Mode.set(self.Shadows)
        if update:
            self.update_frame(self.objectList)

    def toggle_LockAngle(self):
        self.LockAngle = not self.LockAngle
        self.Lock_Angle.set(self.LockAngle)

    def toggle_syncPositions(self):
        self.syncPositions = not self.syncPositions
        self.sync_Positions.set(self.syncPositions)

    def toggle_syncLevels(self):
        self.syncLevels = not self.syncLevels
        self.sync_Levels.set(self.syncLevels)

    def toggle_vector_Anim(self, mode = None):
        if mode is not None:
            self.vectorAnim = mode
        else:
            self.vectorAnim = not self.vectorAnim
        self.vector_Anim.set(self.vectorAnim)
        self.update_frame(self.objectList)

    def toggle_pre_Mult(self, mode = None):
        if mode is None:
            self.preMult = not self.preMult
        else:
            self.preMult = mode
        self.pre_Mult.set(self.preMult)
        self.Screen.preMult = self.preMult

    def toggle_Alpha_Mode(self, mode = None):
        if mode is None:
            self.AlphaMode = not self.AlphaMode
        else:
            self.AlphaMode = mode
        self.Alpha_Mode.set(self.AlphaMode)
        self.Screen.alphamode = self.AlphaMode
        self.update_frame(self.objectList)

    def toggle_Blur_Mode(self, mode = None):
        if mode is None:
            self.BlurMode = not self.BlurMode
        else:
            self.BlurMode = mode
        self.Blur_Mode.set(self.BlurMode)
        self.Screen.blurred = self.BlurMode
        self.update_frame(self.objectList)

    def toggle_Median_Mode(self, mode = None):
        if mode is None:
            self.MedianMode = not self.MedianMode
        else:
            self.MedianMode = mode
        self.Median_Mode.set(self.MedianMode)
        self.Screen.median = self.MedianMode
        self.update_frame(self.objectList)

    def toggle_Edge_Mode(self, mode = None):
        if mode is None:
            self.EdgeMode = not self.EdgeMode
        else:
            self.EdgeMode = mode
        self.Edge_Mode.set(self.EdgeMode)
        self.Screen.edge = self.EdgeMode
        self.update_frame(self.objectList)

    def toggle_Banding_Mode(self, mode = None):
        if mode is None:
            self.BandingMode = not self.BandingMode
        else:
            self.BandingMode = mode
        self.Banding_Mode.set(self.BandingMode)
        self.Screen.banding = self.BandingMode
        self.update_frame(self.objectList)

    def toggle_hBanding_Mode(self, mode = None):
        if mode is None:
            self.hBandingMode = not self.hBandingMode
        else:
            self.hBandingMode = mode
        self.hBanding_Mode.set(self.hBandingMode)
        self.Screen.h_banding = self.hBandingMode
        self.update_frame(self.objectList)

    def toggle_Noise_Mode(self, mode = None):
        if mode is None:
            self.NoiseMode = not self.NoiseMode
        else:
            self.NoiseMode = mode
        self.Noise_Mode.set(self.NoiseMode)
        self.Screen.noise = self.NoiseMode
        self.update_frame(self.objectList)

    def toggle_SDL_Mode(self, noload = True):
        if platform == 'darwin':
            self.SDL_Mode.set(False)
            print("No SDL Mode")
            return
        if not self.SDL_bind:
            if self.OBJ_Wire:
                self.toggle_Wire("Off")
            self.SDL_bind = True
            self.SDL_Mode.set(True)
            h = self.canvas.winfo_height()
            w = self.canvas.winfo_width()
            self.canvas.grid_forget()
            self.embed.grid(row = 0, column = 0, padx = 10, pady = 1, sticky = tk.NW)
            self.embed.configure(width = w, height = h)
            os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())
            if platform == 'linux2':
                os.environ['SDL_VIDEODRIVER'] = 'x11'
            else:
                os.environ['SDL_VIDEODRIVER'] = 'windib'
            self.Screen.setup_SDL(self.Depth)
            self.Screen.setup_Objects_Ground(self.objectList)
            self.Screen.set_Clear_Color(self.clear_color)
            if not self.Textures:
                self.toggle_textures(update = False)
            if noload:
                self.place_images(PICC)
                self.read_object_voxels_repro(self.objectList, VOXX)
            if self.OBJ_bind:
                if self.SDL_bind and self.obj_transform:
                    if self.Screen.VBO:
                        if not self.obj_transform.VBO:
                            self.obj_transform.set_up_vertex_array()
                    elif not self.obj_transform.objdisplayList:
                        self.obj_transform.set_up_display_list(self.Screen.polyDraw)
            self.embed.update()
        else:
            self.embed.grid_forget()
            self.canvas.grid(row = 0, column = 0, padx = 10, pady = 1, sticky = tk.NW)
            self.SDL_bind = False
            self.SDL_Mode.set(False)
            for i in self.Screen.obj_transforms:
                i.delete_display_list()
                i.delete_VBO()
            self.Screen.release_SDL()
            if noload:
                self.write_objects_pic(PICC, True)
                self.print_object_voxels_repro(self.objectList, VOXX)
            self.canvas.update()
            self.canvas.focus_set()

        self.update_object_frame(self.objectList)

    def Set_Repro_Wire_Render(self):
        OBJ_Repro = self.current_Object.voxels()[self.currentVoxel].OBJ_repro
        if not OBJ_Repro:
            OBJ_Repro = self.current_Object.OBJ_repro()
        if not OBJ_Repro:
            return
        (wireDraw, objectDraw) = OBJ_Repro.return_Wire_Render()
        wireDraw = not wireDraw
        OBJ_Repro.tune_Wire_Render((wireDraw, objectDraw))
        self.update_frame(self.objectList)

    def Set_Repro_Wire_Frame(self):
        OBJ_Repro = self.current_Object.voxels()[self.currentVoxel].OBJ_repro
        if not OBJ_Repro:
            OBJ_Repro = self.current_Object.OBJ_repro()
        if not OBJ_Repro:
            return
        (wireDraw, objectDraw) = OBJ_Repro.return_Wire_Render()
        objectDraw = not objectDraw
        OBJ_Repro.tune_Wire_Render((wireDraw, objectDraw))
        self.update_frame(self.objectList)

    def toggle_Voxel_Based_Pic(self):
        self.VoxelBased = not self.VoxelBased
        self.voxel_Based.set(self.VoxelBased)

    def toggle_Voxel_Based_Repro(self):
        self.VoxelBased_repro = not self.VoxelBased_repro
        self.voxel_Based_repro.set(self.VoxelBased_repro)

    def toggle_fitPlace(self):
        self.fitPlace = not self.fitPlace
        self.fit_Place.set(self.fitPlace)

    def toggle_use_Loaded(self):
        self.useLoaded = not self.useLoaded
        self.use_Loaded.set(self.useLoaded)

    def toggle_Mtl_use(self, mtl = None):
        if mtl is not None:
            self.useMtl = mtl
        else:
            self.useMtl = not self.useMtl
        self.use_Mtl.set(self.useMtl)

    def toggle_Zippedspawn(self, mode = None):
        if mode is not None:
            self.Zippedspawn = mode
        else:
            self.Zippedspawn = not self.Zippedspawn
        self.Zipped_spawn.set(self.Zippedspawn)

    def toggle_Propagate(self):
        self.propagate = not self.propagate
        self.Propagate.set(self.propagate)
        for i in self.ObjectList:
            i.toggle_propagate()
        self.update_frame(self.objectList)

    def select_block(self, t):
        print(t)
        arranged = self.current_Object.validate_animated_Cube()
        if not arranged:
            self.arrange_Animated_Cube()
        v = self.currentVoxel
        l = self.level.get()
        self.current_Object.select_array(t, v, l, self.checkMoreLess, True)
        self.update_frame(self.objectList)

    def toggle_MoreLess(self, c):
        print(c)
        self.checkMoreLess = c
        self.check_MoreLess.set(self.checkMoreLess)

    def select_array(self, t):
        print(t)
        arranged = self.current_Object.validate_animated_Cube()
        if not arranged:
            self.arrange_Animated_Cube()
        v = self.currentVoxel
        l = self.level.get()
        self.current_Object.select_array(t, v, l, self.checkMoreLess)
        self.update_frame(self.objectList)

    def undo_View(self):
        if self.VBOFrames_backup:
            self.toggle_Frames()
        self.frontView = False
        self.sideView = False
        self.topView = False
        self.front_View.set(self.frontView)
        self.side_View.set(self.sideView)
        self.top_View.set(self.topView)
        self.set_axis("axis", update = False)
        self.undo_rest(self.isolate_rest)
        if self.localCenter:
            self.local_Center.set(False)
            self.toggle_local_Center(False, force = True)
        self.Depth = self.backup_Depth
        for i in self.objectList:
            i.set_depth(self.Depth)
        if self.backup_Ground:
            self.toggle_local_Ground(mode = True, update = False)
        self.EntryVar4.set(ceil(rad2deg(self.backup_angle)))
        if self.local_Center_backup:
            self.local_Center_backup = False
            self.local_Center.set(True)
            self.toggle_local_Center(False, force = True)
            self.EntryVar4.set(ceil(rad2deg(self.backup_local_angle)))

    def toggle_View(self, view = "front"):

        if self.Zoomed:
            self.undo_view(self.ObjectList, update = False)

        if self.frontView or self.sideView or self.topView:
            self.View = False
        else:
            self.View = True

        if view == "front":
            self.frontView = not self.frontView
            if self.frontView:
                self.sideView = False
                self.topView = False
        elif view == "side":
            self.sideView = not self.sideView
            if self.sideView:
                self.frontView = False
                self.topView = False
        elif view == "top":
            self.topView = not self.topView
            if self.topView:
                self.frontView = False
                self.sideView = False
            
        self.front_View.set(self.frontView)
        self.side_View.set(self.sideView)
        self.top_View.set(self.topView)

        if self.frontView or self.sideView or self.topView:
            if self.SDL_bind:
                if self.VBOFrames:
                    self.VBOFrames_backup = True
                    self.toggle_Frames()
            if self.localCenter:
                self.backup_local_angle = self.current_Object.angle()
                self.local_Center_backup = True
                self.local_Center.set(False)
                self.toggle_local_Center(False, force = True)
            if self.View:
                self.isolate_rest = self.objectList
                self.isolate_object(self.objectList, False)
                self.backup_Ground = self.current_Object.draw_Ground()
                if self.backup_Ground:
                    self.toggle_local_Ground(mode = False, update = False)
                self.backup_angle = self.angle
                self.backup_Depth = self.Depth
                self.Depth = 0
                for i in self.objectList:
                    i.set_depth(self.Depth)
            if view == "front":
                self.set_axis("y", update = False)
                self.EntryVar4.set(0)
            elif view == "side":
                self.set_axis("y", update = False)
                self.EntryVar4.set(90)
            elif view == "top":
                self.set_axis("x", update = False)
                self.EntryVar4.set(90)
        else:
            self.set_axis("axis", update = False)
            if self.localCenter:
                self.local_Center.set(False)
                self.toggle_local_Center(False, force = True)
            self.undo_rest(self.isolate_rest)
            self.Depth = self.backup_Depth
            for i in self.objectList:
                i.set_depth(self.Depth)
            if self.backup_Ground:
                self.toggle_local_Ground(mode = True, update = False)
            self.EntryVar4.set(ceil(rad2deg(self.backup_angle)))
            if self.local_Center_backup:
                self.local_Center_backup = False
                self.local_Center.set(True)
                self.toggle_local_Center(False, force = True)
                self.EntryVar4.set(ceil(rad2deg(self.backup_local_angle)))
            if self.VBOFrames_backup:
                self.toggle_Frames()
            if self.LockAngle:
                conform = self.current_Object.conform_position() + self.current_Object.local_conform()
                objectList = []
                for i in self.objectList:
                    Conform = i.conform_position() + i.local_conform()
                    if str(conform) == str(Conform):
                        objectList.append(i)
            else:
                objectList = self.objectList
            self.sync_voxels(objects = objectList)

    def toggle_local_Center(self, update = True, force = False):
        if not force and (self.frontView or self.sideView or self.topView):
            return
        condition = self.local_Center.get()
        print("toggle_local_Center", condition)
        if condition:
            self.localCenter = condition
            self.c_baked = self.angle
            self.Screen.baked_c = self.c_baked
            self.Screen.vector_c = self.vector
            for i in self.ObjectList:
                i.set_LOCAL(True)
                i.cube().rotate3d_vector(self.center, self.vector, self.c_baked)
                i.localize(None)
                i.switch_conform_position()
                i.move_to_conform(i.conform_position())
        else:
            if self.OBJ_bind:
                self.toggle_OBJ_Mode()
            self.localCenter = condition
            self.Screen.baked_c = 0
            self.Screen.vector_c = (0, 1, 0)
            for i in self.ObjectList:
                i.set_LOCAL(False)
                i.reset_position(False)
                i.switch_conform_position()
                i.restore_vector()
        vector = self.current_Object.local()
        self.angle = self.current_Object.angle()
        if update:
            self.EntryVar.set(vector)
            self.update_object_frame(self.objectList)

    def toggle_write_KeyFrame(self):
        c = self.write_KeyFrame.get()
        print("toggle_write_KeyFrame", c)
        self.writeKeyFrame = c

    def toggle_set_Shape(self):
        c = self.set_Shape.get()
        print("toggle_set_Shape", c)
        self.setShape = c

    def toggle_set_Color(self):
        c = self.set_Color.get()
        print("toggle_set_Color", c)
        self.setColor = c

    def load_backup_frame(self):
        global Xdim, Ydim, Zdim
        try:
            (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
            data = array(self.backup_frame).reshape(Xdim, Ydim, Zdim, 2)
        except(Exception) as detail:
            print("frame is not in current dimension", detail)
            return
        #self.current_Object.remove_highlight()
        self.current_Object.load_frame(data, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
        self.update_frame(self.objectList)

    def create_backup_frame(self):
        self.current_Object.remove_highlight()
        if self.current_Object.collected() != []:
            self.backup_frame = self.current_Object.write_frame(False, True, True)
            print("create_backup_frame with illumination color")
        else:
            self.backup_frame = self.current_Object.write_frame(False, True)
            print("create_backup_frame with object color")

    def set_voxel_color(self, color, mix):
        if self.falloff > 1:
            falloff = self.falloff**2
        else:
            falloff = 0
        print("set_voxel_color", color)
        self.current_Object.set_voxel_color(self.currentVoxel, color, mix, falloff)
        self.write_key_frame()
        self.update_frame(self.objectList)

    def switch_black_white(self):
        t = self.colorvariation.get()
        if t == 1:
            self.colorvariation.set(2)
        elif t == 2:
            self.colorvariation.set(1)

    def trace_color(self, *args):
        t = self.colorvariation.get()
        if t == 1:
            self.restore_fg_bg()
        elif t == 2:
            self.black_and_white()

    def restore_fg_bg(self):
        if self.fgcolor == (255, 255, 255) and self.bgcolor == (0, 0, 0) or self.bgcolor == (255, 255, 255) and self.fgcolor == (0, 0, 0):
            fgcolor = self.fgcolor
            self.fgcolor = self.fgcolor1
            self.fgcolor1 = fgcolor
            bgcolor = self.bgcolor
            self.bgcolor = self.bgcolor1
            self.bgcolor1 = bgcolor
        else:
            fgcolor = self.fgcolor
            self.fgcolor = self.bgcolor
            self.bgcolor = fgcolor

        rgb = "#%02x%02x%02x" % self.fgcolor
        rgb1 = "#%02x%02x%02x" % self.bgcolor
        self.color1['background'] = rgb1
        self.color2['background'] = rgb

        self.color_font1(rgb1, 'color')
        self.color_font2(rgb, 'color1')
        self.CVar1.set('bg fg updated. ')

    def black_and_white(self):
        if self.fgcolor == (255, 255, 255) and self.bgcolor == (0, 0, 0):
            self.bgcolor = (255, 255, 255)
            self.fgcolor = (0, 0, 0)
        elif self.bgcolor == (255, 255, 255) and self.fgcolor == (0, 0, 0):
            self.fgcolor = (255, 255, 255)
            self.bgcolor = (0, 0, 0)
        else:
            self.fgcolor1 = self.fgcolor
            self.fgcolor = (255, 255, 255)

            self.bgcolor1 = self.bgcolor
            self.bgcolor = (0, 0, 0)


        rgb = "#%02x%02x%02x" % self.fgcolor
        rgb1 = "#%02x%02x%02x" % self.bgcolor
        self.color1['background'] = rgb1
        self.color2['background'] = rgb

        self.color_font1(rgb1, 'color')
        self.color_font2(rgb, 'color1')
        self.CVar1.set('bg fg updated. ')

    def switch_colors(self):
        rgb = self.color1['background']
        rgb1 = self.color2['background']
        rgb2 = rgb1
        rgb1 = rgb
        rgb = rgb2
        self.color1['background'] = rgb
        self.color2['background'] = rgb1
        rgb = rgb[1:]
        (r, g, b) = hextorgb(rgb)
        self.bgcolor = (r, g, b)
        self.color_font1(rgb, 'color')
        rgb1 = rgb1[1:]
        (r, g, b) = hextorgb(rgb1)
        self.fgcolor = (r, g, b)
        self.color_font2(rgb1, 'color1')
        self.CVar1.set('bg fg updated. ')

    def color1_set(self, event):
        try:
            bg = self.EntryVar_1.get()
            self.color1['background'] = bg
            self.color_font1(bg, 'color')
            rgb = bg[1:]
            (r, g, b) = hextorgb(rgb)
            self.bgcolor = (r, g, b)
        except:
            print('error in hexadecimal 1')

    def color2_set(self, event):
        try:
            bg = self.EntryVar_2.get()
            self.color2['background'] = bg
            self.color_font2(bg, 'color1')
            rgb = bg[1:]
            (r, g, b) = hextorgb(rgb)
            self.fgcolor = (r, g, b)
        except:
            print('error in hexadecimal 2')

    def scroll_alpha(self, event, t):
        amount = 0
        if platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform == 'cygwin':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta
        if t == 1:
            self.alpha1_set(amount)
        else:
            self.alpha2_set(amount)

    def alpha1_set(self, amount = 0):
        var = self.AlphaEntryVar1.get()
        try:
            v = int(var)
            v += amount
            v = divmod(v, 256)[1]
        except:
            v = 255
        self.AlphaEntryVar1.set(v)

    def alpha2_set(self, amount = 0):
        var = self.AlphaEntryVar2.get()
        try:
            v = int(var)
            v += amount
            v = divmod(v, 256)[1]
        except:
            v = 255
        self.AlphaEntryVar2.set(v)

    def color_font1(self, bg, T):
        self.color1.delete(T)
        self.color1.create_text(10, 1, text = bg + 'BG', font = self.sans8, anchor = tk.NW, tag = T, activefill = '#ffffff')

    def color_font2(self, bg, T):
        self.color2.delete(T)
        self.color2.create_text(10, 1, text = bg + 'FG', font = self.sans8, anchor = tk.NW, tag = T, activefill = '#ffffff')

    def construct_colorbar(self):
        global nr
        nr = 0
        for i in range(0, len(self.colorbar)):
            self.colorbar[i] = colorbar()

    def create_colorbar(self):
        for i in range(0, len(self.colorbar)):
            self.color.delete('col' + str(i))
            self.color.create_image(strip_W * i + 2, 0, anchor = tk.NW, image = self.colorbar[i].img, tags = 'col' + str(i))
        self.color.tag_raise('col7')
        self.color.tag_raise('col8')

    def scroll_palette(self, t):
        print('scroll_palette', t)
        global palettes
        if t == 'left':
            first = palettes.pop(0)
            palettes.append(first)
        else:
            last = palettes.pop(-1)
            palettes.insert(0, last)
        colorbar.N = []
        self.construct_colorbar()
        self.create_colorbar()
        print(colorbar.N)

    def color_get1(self, event):
        rgb = self.color1['background']
        self.EntryVar_1.set(rgb)
        rgb = rgb[1:]
        (r, g, b) = hextorgb(rgb)
        self.bgcolor = (r, g, b)
        print(r, g, b)
        self.set_voxel_color(self.bgcolor, self.AlphaEntryVar1.get())

    def color_get2(self, event):
        rgb = self.color2['background']
        self.EntryVar_2.set(rgb)
        rgb = rgb[1:]
        (r, g, b) = hextorgb(rgb)
        self.fgcolor = (r, g, b)
        print(r, g, b)
        self.set_voxel_color(self.fgcolor, self.AlphaEntryVar2.get())

    def cursor_tab1(self, event, cursor):
        self.c_tabs += 1
        if self.c_tabs > 7:
            self.c_tabs = 0
        c = self.c_tabs
        x1 = strip_W * c
        y1 = 0
        self.color.coords(cursor + 1, (x1, y1))
        print(c, "got focus")
        self.color.focus(c)

        if platform == 'win32':
            x = self.color.winfo_rootx()
            y = self.color.winfo_rooty()
            user.SetCursorPos(x1 + x, y1 + y)

        (r, g, b) = (255, 255, 255)

        if noPIL == True:
            pass
        else:
            try:
                (r, g, b, a) = self.colorbar[c].pixload[x1, y1]
            except(Exception) as detail:
                pass

        print(r, g, b)
        self.color2['background'] = "#%02x%02x%02x" % (r, g, b)

    def cursor_tab(self, event, cursor):
        x = event.x
        y = event.y
        if y < 0:
            y = 0
        elif y > strip_H:
            y = strip_H

        if x < 0:
            c = 0
            x = 0
        elif x >= 0 and x <= strip_W:
            c = 0
        elif x > strip_W and x <= strip_W * 2:
            c = 1
        elif x > strip_W * 2 and x <= strip_W * 3:
            c = 2
        elif x > strip_W * 3 and x <= strip_W * 4:
            c = 3
        elif x > strip_W * 4 and x <= strip_W * 5:
            c = 4
        elif x > strip_W * 5 and x <= strip_W * 6:
            c = 5
        elif x > strip_W * 6 and x <= strip_W * 7:
            c = 6
        elif x > strip_W * 7:
            c = 6
            x = strip_W * 7
        self.color.coords(cursor + 1, (x, y))
        print(c, "got focus")
        self.color.focus(c)

        (r, g, b) = (255, 255, 255)

        if noPIL == True:
            pass
        else:
            try:
                (r, g, b, a) = self.colorbar[c].pixload[x - strip_W * c, y]
            except(Exception) as detail:
                pass

        self.color2['background'] = "#%02x%02x%02x" % (r, g, b)

    def color_focus(self, event):
        print('got focus')
        self.color.focus_set()
        if platform == 'win32':
            x = self.color.winfo_rootx()
            y = self.color.winfo_rooty()
            user.SetCursorPos(x, y)

    def cursor_set(self, event, c):
        x = event.x
        y = event.y
        self.cursor.x = x
        self.cursor.y = y
        self.color.coords(c + 1, (x, y))
        color = self.color_get(event)
        bg = "#%02x%02x%02x" % color
        self.bgcolor = color
        self.color1['background'] = bg
        self.color_font1(bg, 'color')
        self.color.focus_set()
        print('focus')

    def cursor_set1(self, event, c):
        x = event.x
        y = event.y
        self.cursor.x = x
        self.cursor.y = y
        self.color.coords(c + 2, (x, y))
        color = self.color_get(event)
        bg = "#%02x%02x%02x" % color
        self.fgcolor = color
        self.color2['background'] = bg
        self.color_font2(bg, 'color1')
        self.color.focus_set()
        print('focus')

    def cursor_move(self, event, c):
        x = event.x
        y = event.y
        self.cursor.x = x
        self.cursor.y = y
        self.color.coords(c + 1, (x, y))
        color = self.color_get(event)
        bg = "#%02x%02x%02x" % color
        self.bgcolor = color
        self.color1['background'] = bg
        self.color_font1(bg, 'color')

    def cursor_move1(self, event, c):
        x = event.x
        y = event.y
        self.cursor.x = x
        self.cursor.y = y
        self.color.coords(c + 2, (x, y))
        color = self.color_get(event)
        bg = "#%02x%02x%02x" % color
        self.fgcolor = color
        self.color2['background'] = bg
        self.color_font2(bg, 'color1')

    def cursor_move_keys(self, event, x, y):
        self.color.move('col7', x , y)
        (x, y) = self.color.coords('col7')
        color = self.color_get(event = None, x = x, y = y)
        bg = "#%02x%02x%02x" % color
        self.fgcolor = color
        self.color1['background'] = bg
        self.color_font1(bg, 'color')

    def color_get(self, event = None, x = None, y = None):
        if event == None:
            x = x
            y = y
        else:
            x = event.x
            y = event.y
            self.cursor.x = x
            self.cursor.y = y

        if y < 0:
            y = 0
        elif y > strip_H:
            y = strip_H

        if x < 0:
            c = 0
            x = 0
        elif x >= 0 and x <= strip_W:
            c = 0
        elif x > strip_W and x <= strip_W * 2:
            c = 1
        elif x > strip_W * 2 and x <= strip_W * 3:
            c = 2
        elif x > strip_W * 3 and x <= strip_W * 4:
            c = 3
        elif x > strip_W * 4 and x <= strip_W * 5:
            c = 4
        elif x > strip_W * 5 and x <= strip_W * 6:
            c = 5
        elif x > strip_W * 6 and x <= strip_W * 7:
            c = 6
        elif x > strip_W * 7:
            c = 6
            x = strip_W * 7

        (r, g, b) = (255, 255, 255)

        if noPIL == True:
            pass
        else:
            try:
                (r, g, b, a) = self.colorbar[c].pixload[x - strip_W * c, y]
            except(Exception) as detail:
                pass

        self.r = r
        self.g = g
        self.b = b
        print(r, g, b)
        return(r, g, b)

    # --- color 4

    def find_neighbours(self, falloff):
        self.checkFalloff.set(falloff)
        self.falloff = falloff
        self.arrange_Animated_Cube()
        if not self.current_Object.collected():
            voxel = self.currentVoxel
            self.current_Object.remove_highlight()
            self.CVar1.set("neighbours for highlighted set, measuring %d voxels"% self.falloff)
        else:
            voxel = None
            self.CVar1.set("neighbours for collection set, measuring %d voxels"% self.falloff)
        self.current_Object.select_neighbours_by_cube(falloff, voxel)
        self.update_frame(self.objectList)

    def paste_selection(self):
        if self.coords_collected:
            c = self.current_Object.paste_by_coordinates(self.coords_collected)
            if c > 0:
                self.update_frame(self.objectList)
            print("pasted %d items" % c)
            self.CVar1.set("pasted %d items" % c)

    def copy_selection(self):
        self.coords_collected = self.current_Object.give_by_coordinates()
        c = len(self.coords_collected)
        print("copyed %d items" % c)
        self.CVar1.set("copyed %d items" % c)

    def clear_highlight(self, update = True):
        for i in self.objectList:
            if i.collected() == []:
                i.remove_highlight()
            else:
                i.clear_collected()
        if update:
            self.update_frame(self.objectList)

    def voxel_spawned(self):
        self.current_Object.change_spawned()
        self.update_frame(self.objectList)

    def key_down(self, e):
        print("key_down", e.keycode)
        self.root.title("World Pixel (...) " + sceneDir)
        if self.SDL_bind:
            events = pygame.event.get()
            for event in events:
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.toggle_Rotation()
                    elif event.key == K_ESCAPE:
                        self.clear_collected(self.objectList)
                    elif event.key == K_f:
                        self.find_neighbours(self.falloff)
                    elif event.key == K_l:
                        self.toggle_Lights()
                    elif event.key == K_w:
                        self.toggle_Wire()
                    elif event.key == K_b:
                        self.toggle_Background()
                    elif event.key == K_g:
                        self.toggle_Ground()
                    elif event.key == K_p:
                        self.toggle_animation()
                    elif event.key == K_t:
                        self.toggle_textures()
                    elif event.key == K_c:
                        self.toggle_draw_Cube_All()
                    elif event.key == K_s:
                        self.toggle_Shadows()
                    elif event.key == K_d:
                        self.toggle_draft_Mode()
                    elif event.key == K_i:
                        self.goto_Imagefile()
                    elif event.key == K_m:
                        self.select_same_level()
                    elif event.key == K_k:
                        self.select_same_highlight()
                    elif event.key == K_y:
                        self.toggle_Propagate()
                    elif event.key == K_KP0:
                        self.toggle_Lightsource(0)
                    elif event.key == K_KP1:
                        self.toggle_Lightsource(1)
                    elif event.key == K_PAGEUP:
                        self.scroll_objects(-1)
                    elif event.key == K_PAGEDOWN:
                        self.scroll_objects(1)
                    elif event.key == K_RETURN:
                        self.write_key_frame()
                    elif event.key == K_KP_PLUS:
                        self.refine_levels(True)
                    elif event.key == K_KP_MINUS:
                        self.collect_voxels()
                    elif event.key == K_a:
                        self.shiftDown = not self.shiftDown
                        self.controlDown = not self.shiftDown
                    elif event.key == K_q:
                        self.controlDown = not self.controlDown
                        self.shiftDown = not self.controlDown
##                    elif event.key == K_LEFT:
##                        if pygame.key.get_mods() & KMOD_CTRL:
##                            self.move_around((-self.level.get(), 0, 0), self.ObjectList)
##                        else:
##                            self.move_conform((-self.level.get() * 2.0, 0, 0), [self.current_Object,])
##                    elif event.key == K_RIGHT:
##                        if pygame.key.get_mods() & KMOD_CTRL:
##                            self.move_around((self.level.get(), 0, 0), self.ObjectList)
##                        else:
##                            self.move_conform((self.level.get() * 2.0, 0, 0), [self.current_Object,])

    def key_release(self, e):
        print("key_release", e.keycode)
        print("key_release", e.keysym)
        if e.keycode == 16 or e.keysym == 'Shift_L':
            self.shiftDown = False
        if e.keycode == 17 or e.keysym == 'Control_L':
            self.controlDown = False
##        if e.keycode == 65:
##            self.shiftDown = False
##        if e.keycode == 81:
##            self.controlDown = False

    def shift_press(self, e):
        self.shiftDown = True

    def control_press(self, e):
        self.controlDown = True

    def adjustTime(self, e, c, d):
        c += d
        self.shorten_entry_3(0, 0, 0)

    def adjustScale(self, e, c, d):
        c += d
        self.write_key_frame()

    def adjustDepth(self, e, c, d):
        c += d

    def set_size_recursive(self):
        self.current_Object[self.currentVoxel].set_size_recursive()
        self.update_frame(self.objectList)

    def set_shadow_alpha(self):
        (rgb, hx) = tkColorChooser.askcolor()
        if rgb and hx:
            global shadowcolor, gl_shadowcolor
            c = shadowcolor
            if platform == 'darwin':
                color = (c[0], c[1], c[2], 255)
            else:
                color = (c[0], c[1], c[2], rgb[0])
            set_shadow_color(color)
            self.update_frame(self.objectList)

    def set_object_alpha(self):
        (rgb, hx) = tkColorChooser.askcolor()
        if rgb and hx:
            global objectcolor, gl_objectcolor
            c = objectcolor
            color = (c[0], c[1], c[2], rgb[0])
            set_object_color(color)
            self.update_frame(self.objectList)

    def set_background_color_alpha(self, bgcol, alpha):
        print("bgcol", bgcol)
        print("alpha", alpha)
        self.background_color = bgcol.strip()
        self.canvas.configure(bg = self.background_color)
        if platform == 'darwin':
            alpha = alpha[-1] #255
        else:
            alpha = alpha[-1]
        background_color = self.background_color[1:]
        rgb = hextorgb(background_color)
        self.clear_color = tuple(list(rgb) + [alpha,])
        self.Screen.set_Clear_Color(self.clear_color)

    def set_background_alpha(self):
        (rgb, hx) = tkColorChooser.askcolor()
        if rgb and hx:
            c = self.clear_color
            if platform == 'darwin':
                self.clear_color = (c[0], c[1], c[2], rgb[0]) #255)
            else:
                self.clear_color = (c[0], c[1], c[2], rgb[0])
            self.Screen.set_Clear_Color(self.clear_color)
            if self.SDL_bind:
                self.Screen.Background_texture = self.Screen.createBackground(self.Screen.BackgroundImage)
            self.update_frame(self.objectList)
            print(self.clear_color)

    def set_background_color(self):
        (rgb, hx) = tkColorChooser.askcolor()
        if rgb and hx:
            self.background_color = hx
            self.canvas.configure(bg = self.background_color)
            if platform == 'darwin':
                alpha = self.clear_color[-1] #255
            else:
                alpha = self.clear_color[-1]
            self.clear_color = tuple(list(rgb) + [alpha,])
            self.Screen.set_Clear_Color(self.clear_color)
            self.update_frame(self.objectList)
            print(self.clear_color)

    def select_voxels_by_rect(self):
        T = self.view_rect_2d.put_array()
        V = self.Screen.screen_voxel.keys()
        C = set(V) - set(T)
        c = set(V) - set(C)
        candidates = array([self.Screen.screen_voxel[i] for i in c])
        try:
            candidates = concatenate(candidates)
        except:
            pass
        if len(candidates) == 0:
            print("picmap")
            candidates = self.find_candidates_in_picmap()
        print("CANDIDATES")
        if len(candidates) != 0:
            if self.shiftDown:
                self.current_Object.append_collection(candidates)
            elif self.controlDown:
                self.current_Object.subtract_collection(candidates)
            else:
                self.current_Object.create_collection(candidates)
##            self.shiftDown = False
##            self.controlDown = False
            self.current_Object.validate_highlight()

            self.current_Object.highlight_collection()
            self.update_frame(self.objectList)

    def find_candidates_in_picmap(self):
        l = self.Screen.pixelmap_picking.get_array()
        b = l[self.view_rect_2d.min.x:self.view_rect_2d.max.x,
              self.view_rect_2d.min.y:self.view_rect_2d.max.y]
        b = b - 1
        condition = b > -1
        c = extract(condition, b)

##        print(type(b))
##        p = b.shape
##        for x in range(p[0]):
##            C = []
##            for y in range(p[1]):
##                C.append(b[x, y])
##            print(C)
        return set(c)

    def up(self, event):
        self.tag = "Screen"
        global canvas_w, canvas_h
        x = event.x - offset_2w
        y = event.y - offset_2h
        if canvas_w != self.Screen.width or canvas_h != self.Screen.height:
            self.stop_animation()
            self.stop_Rotation()
            self.Screen.renew_objects(canvas_w, canvas_h)
##            self.image = self.Screen[0]
##            self.screen = ImageTk.PhotoImage(self.image, 'r')
##            canvas_2w = canvas_w / 2 + offset_2w
##            canvas_2h = canvas_h / 2 + offset_2h
            self.set_background(self.background_filename)
            self.update_frame(self.objectList)
        elif self.view_rect_2d.state:
            self.view_rect_2d.state = False
            self.view_rect_2d.validate()
            self.select_voxels_by_rect()
            if self.mouseDownId:
                self.mouseWidget.delete("Rect2D")
                self.mouseDownId = 0
            if self.SDL_bind:
                glDisable(GL_COLOR_LOGIC_OP)
                glEnable(GL_DEPTH_TEST)
                glDisable(GL_LINE_STIPPLE)
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glDrawBuffer(GL_BACK)
                if self.Lights:
                    glEnable(GL_LIGHTING)
                self.mouse_move_Setup = False
                self.update_frame(self.objectList)
            else:
                self.mouseWidget.delete("Rect2D")
        else:
            try:
                l = self.Screen.pixelmap_picking.get_array()
                m = l[x, y] - 1
                M = l[x, y]
                print(m)
                if m > -1:
                    if self.shiftDown:
                        self.current_Object.append_collection([m, self.currentVoxel])
                        self.current_Object.validate_highlight()
                        self.current_Object.highlight_collection()
                        self.update_frame(self.objectList)
                    elif self.controlDown:
                        self.current_Object.subtract_collection([m,])
                        self.current_Object.validate_highlight()
                        self.current_Object.highlight_collection()
                        self.update_frame(self.objectList)
                    else:
                        self.currentVoxel = m
                        self.current_Object.get_highlight(m)
                        self.update_frame(self.objectList)
                        self.get_dimension()
                        self.EntryVar1.set(self.currentVoxel)
                elif M < 0:
                    object_to_select = self.ObjectList[-M - 1]
                    if object_to_select is not self.current_Object:
                        self.select_object(object_to_select)
            except(Exception) as detail:
                print(detail)
        self.shiftDown = False
        self.controlDown = False

    def down(self, event, t = 0):
        self.mouseDownId = t
        self.mouseWidget = event.widget
        x = event.x - offset_2w
        y = event.y - offset_2h

        self.stop_animation()
        self.stop_Rotation()

        global backup_linecolor

        if backup_linecolor:
            if backup_linecolor is not self.current_Object:
                print("mousedown selection")
                self.select_object(backup_linecolor)
                for i in self.objectList:
                    i.cube().normal_line()
                backup_linecolor = None

        #- test for pickmap grayscale -
        #l = self.Screen.pixelmap_picking.get_array()
        #l = l.transpose()
        #img1 = Image.fromarray(l)
        #self.screen = ImageTk.PhotoImage(img1, 'r')
        #self.canvas.delete('Screen')
        #self.canvas.create_image(offset_2w, offset_2h, image = self.screen, anchor = tk.NW, tags = "Screen")
        #self.canvas.tag_raise('Corner')
        #self.canvas.update()
        #- -

        self.view_rect_2d.min.x = x
        self.view_rect_2d.min.y = y
        self.view_rect_2d.max.x = x
        self.view_rect_2d.max.y = y


        enclosed = self.canvas.find_enclosed(x - 28,
                                             y - 28,
                                             x + 28,
                                             y + 28)
        if len(enclosed) > 0:
            self.tag = self.canvas.gettags(enclosed[0])[0]
        else:
            closest = self.canvas.find_closest(x, y)
            self.tag = self.canvas.gettags(closest[0])[0]

        print(self.tag)

    def move_image_position(self, event):
        x = event.x
        y = event.y
        #print("move_image_position", x, y)
        global canvas_w, canvas_h
        if x < 1:
            x = 1
        if y < 1:
            y = 1
        if self.tag == "Corner" and not self.mouseDownId:
            if self.SDL_bind:
                return
##                self.SDL_bind = False
##                self.SDL_Mode.set(False)
##                self.Screen.release_SDL()
            canvas_w += (x - canvas_w)
            canvas_h += (y - canvas_h)
            self.canvas.coords("Corner", (x + offset_2w, y + offset_2h))
            self.canvas.configure(width = canvas_w, height = canvas_h)
            self.CVar1.set("%sx%s" % (canvas_w, canvas_h))
        else:
            self.view_rect_2d.state = True
            X = self.view_rect_2d.max.x
            Y = self.view_rect_2d.max.y
            self.view_rect_2d.max.x = x
            self.view_rect_2d.max.y = y
            if self.mouseDownId:
                self.mouseWidget.delete("Rect2D")
                self.mouseWidget.create_rectangle(self.view_rect_2d.min.x, self.view_rect_2d.min.y,
                                             self.view_rect_2d.max.x, self.view_rect_2d.max.y,
                                             outline = "yellow", dash = (2, 2), tags = "Rect2D")
            if self.SDL_bind:
                if not self.mouse_move_Setup:
                    self.mouse_move_Setup = True
                    if self.Lights:
                        glDisable(GL_LIGHTING)
                    glEnable(GL_COLOR_LOGIC_OP)
                    glLogicOp(GL_XOR)
                    glDisable(GL_DEPTH_TEST)
                    if self.shiftDown:
                        glLineStipple(1, 0x00FF)
                    elif self.controlDown:
                        glLineStipple(1, 0xF0F0)
                    else:
                        glLineStipple(1, 0x3333)
                    glColor4f(1.0, 1.0, 1.0, 1.0)
                    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                    glDrawBuffer(GL_FRONT)
                    glEnable(GL_LINE_STIPPLE)
                glRecti(self.view_rect_2d.min.x, self.view_rect_2d.min.y,
                        X, Y)
                glRecti(self.view_rect_2d.min.x, self.view_rect_2d.min.y,
                        self.view_rect_2d.max.x, self.view_rect_2d.max.y)
                glFlush()
            else:
                self.mouseWidget.delete("Rect2D")
                self.mouseWidget.create_rectangle(self.view_rect_2d.min.x, self.view_rect_2d.min.y,
                                             self.view_rect_2d.max.x, self.view_rect_2d.max.y,
                                             outline = "yellow", dash = (2, 2), tags = "Rect2D")

    def canvas_move_keys(self, c, t):
        self.nudge_img(t, c)

    def nudge_img(self, c, t = None):
        global canvas_w, canvas_h
        (x, y) = (canvas_w, canvas_h)
        if c == 'left':
            x -= t
        elif c == 'right':
            x += t
        elif c == 'up':
            y -= t
        elif c == 'down':
            y += t
        if x < 1:
            x = 1
        if y < 1:
            y = 1
        if self.tag == "Corner":
            (canvas_w, canvas_h) = (x, y)
            self.canvas.coords("Corner", (x + offset_2w, y + offset_2h))
            self.canvas.configure(width = canvas_w, height = canvas_h)
            self.CVar1.set("%sx%s" % (canvas_w, canvas_h))

    def reset_frames(self):
        if self.current_Object.collected():
            self.current_Object.set_voxel_frames(0)
        elif self.VoxelBased:
            self.current_Object.voxels()[self.currentVoxel].set_frame(0)
        else:
            self.current_Object.set_frame(0)
        self.update_frame(self.objectList)

    def animation_oscillate(self):
        if self.current_Object.collected():
            self.current_Object.set_voxel_oscillate()
        elif self.VoxelBased:
            self.current_Object.voxels()[self.currentVoxel].set_oscillate()
        self.update_frame(self.objectList)

    def randomize_animated_repro(self):
        if self.current_Object.collected():
            self.current_Object.set_voxel_frames()
        elif self.VoxelBased:
            v = self.current_Object.voxels()[self.currentVoxel]
            if v.OBJ_repro and v.OBJ_repro.Frames > 1:
                frame = random.randint(0, v.OBJ_repro.Frames - 1)
                v.set_frame(frame)
        elif self.current_Object.OBJ_repro() and self.current_Object.OBJ_repro().Frames > 1:
            self.current_Object.set_frame()
        self.update_frame(self.objectList)

    def open_image_display(self, image):
        if self.msg_box_Image_panel != None and self.msg_box_Image_panel.winfo_exists():
            self.msg_box_Image_panel.lift_it()
            self.msg_box_Image_panel.focus_set()
        else:
            global sceneDir
            imageName = os.path.split(image)[-1]
            self.msg_box_Image_panel = messageBox.Image_Panel(parent = self.root, root = self, ok = 'Image panel',
                                                         T = imageName, imageFile = image,
                                                         default = "Image Display", sceneDir = sceneDir,
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def give_minor_level(self, level):
        self.minorlevel = level
        self.saveMinorHint()
        print("minorlevel", self.minorlevel)

    def get_minor_level_dialog(self):
        if self.msg_box_Minor_level != None and self.msg_box_Minor_level.winfo_exists():
            self.msg_box_Minor_level.lift_it()
            self.msg_box_Minor_level.focus_set()
        else:
            self.msg_box_Minor_level = messageBox.Check_Mark(parent = self.root, root = self, ok = 'give_minor_level',
                                                         T = "Get Subdivision", check_mark = self.minorlevel,
                                                         default = "Minor Level",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def set_object_name(self, n):
        self.current_Object.set_name(n)
        self.update_frame(self.objectList)

    def set_object_name_dialog(self):
        if self.msg_box_Object_name != None and self.msg_box_Object_name.winfo_exists():
            self.msg_box_Object_name.lift_it()
            self.msg_box_Object_name.focus_set()
            self.msg_box_Object_name.ok_button.focus()
        else:
            name = self.current_Object.name()
            self.msg_box_Object_name = messageBox.Object_name(parent = self.root, root = self, ok = 'set_object_name',
                                                         T = "Set Object Name", objectname = name,
                                                         font = self.sans8, default = "Set Object Name",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def get_canvas(self, e, w, h):
        global canvas_w, canvas_h
        self.canvas.configure(width = w, height = h)
        self.embed.configure(width = w, height = h)
        canvas_w = w
        canvas_h = h
        self.canvas.coords("Corner", canvas_w + offset_2w, canvas_h + offset_2h)
        self.tag = "Corner"
        self.CVar4.set(self.tag)
        self.CVar1.set("%sx%s" % (canvas_w, canvas_h))

        self.Screen.renew_objects(canvas_w, canvas_h)
        self.set_background(self.background_filename)
        self.update_frame(self.objectList)

    def set_canvas_size_dialog(self):
        if self.msg_box_Canvas_size != None and self.msg_box_Canvas_size.winfo_exists():
            self.msg_box_Canvas_size.lift_it()
            self.msg_box_Canvas_size.focus_set()
            self.msg_box_Canvas_size.ok_button.focus()
        else:
            self.msg_box_Canvas_size = messageBox.Canvas_size(parent = self.root, root = self, ok = 'get_canvas',
                                                         T = "Set Canvas Size", canvas_w = canvas_w, canvas_h = canvas_h,
                                                         font = self.sans8, default = "Set Canvas Size",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def set_canvas_size(self, w, h, update = True):
        global canvas_w, canvas_h
        self.canvas.configure(width = w, height = h)
        self.embed.configure(width = w, height = h)
        canvas_w = w
        canvas_h = h

        self.canvas.coords("Corner", canvas_w + offset_2w, canvas_h + offset_2h)
        self.tag = "Corner"

        self.Screen.renew_objects(canvas_w, canvas_h)
        if update:
            self.set_background(self.background_filename)
            self.update_frame(self.objectList)

    def Voxel_Info(self):
        object_intro = "This object has:\n"
        object_name = self.current_Object.name()
        object_image = self.current_Object.image()
        object_repro = self.current_Object.repro()
        object_texName = self.current_Object.texName()
        object_Frames = self.current_Object.Frames()
        object_voxels = len(self.current_Object.voxels())
        if object_repro:
            object_Faces = len(self.current_Object.OBJ_repro().faces)
        else:
            object_Faces = 0
        object_ground = self.groundImage
        direction = "%3.2f" % rad2deg(self.current_Object.get_direction())
        intro = "This voxel has:\n"
        index = self.currentVoxel
        image = self.current_Object.voxels()[self.currentVoxel].image
        repro = self.current_Object.voxels()[self.currentVoxel].repro
        texName = self.current_Object.voxels()[self.currentVoxel].texName
        Frames = self.current_Object.voxels()[self.currentVoxel].Frames
        if repro:
            Faces = len(self.current_Object.voxels()[self.currentVoxel].OBJ_repro.faces)
        else:
            Faces = 0
        Osc = self.current_Object.voxels()[self.currentVoxel].Oscillate
        Zipped = self.current_Object.voxels()[self.currentVoxel].zipped
        ground = self.current_Object.ground()

        msg = str(
            object_intro +
            "-------------\n" +
            "name\t" + str(object_name) + "\n" +
            "image\t" + str(object_image) + "\n" +
            "repro\t" + str(object_repro) + "\n" +
            "texName\t" + str(object_texName) + "\n" +
            "Frames\t" + str(object_Frames) + "\n" +
            "Faces\t" + str(object_Faces) + "\n" +
            "voxels\t" + str(object_voxels) + "\n" +
            "ground\t" + str(object_ground) + "\n" +
            "direction\t" + str(direction) + "\n" +
            "\n" +
            intro +
            "-------------\n" +
            "index\t" + str(index) + "\n" +
            "image\t" + str(image) + "\n" +
            "repro\t" + str(repro) + "\n" +
            "texName\t" + str(texName) + "\n" +
            "Frames\t" + str(Frames) + "\n" +
            "Faces\t" + str(Faces) + "\n" +
            "Oscillate\t" + str(Osc) + "\n" +
            "Zipped\t" + str(Zipped) + "\n" +
            "ground\t" + str(ground))
        return msg

    def About_This_Voxel(self):
        if self.AboutThisVoxel != None and self.AboutThisVoxel.winfo_exists():
            self.AboutThisVoxel.lift_it()
            self.AboutThisVoxel.focus_set()
        else:
            msg = self.Voxel_Info()
            self.AboutThisVoxel = messageBox.About_This_Voxel(parent = self.root, root = self, ok = 'Voxel_Info',
                                                                 T = "Worldpixel", info = msg,
                                                                 default = "Object and Voxel Info",
                                                                 RWidth = self.RWidth, RHeight = self.RHeight,
                                                                 bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def set_Smoothness(self, value):
        print("set_Smoothness", value)
        self.smooth = value
        self.perform_smoothing([self.current_Object,], self.smoothColors, self.smoothSizes)

    def Smooth_cleanup(self):
        self.current_Object

    def smooth_dial(self):
        if self.msg_box_Smooth != None and self.msg_box_Smooth.winfo_exists():
            self.msg_box_Smooth.lift_it()
            self.msg_box_Smooth.focus_set()
        else:
            self.current_Object.setup_Smooth_Arrays(self.smoothColors, self.smoothSizes)
            self.msg_box_Smooth = messageBox.Horizontal_Scale(parent = self.root, root = self, ok = 'set_Smoothness',
                                                         T = "Set Smooth", I = 100, L = "smooth", cleanup_function = "Smooth_cleanup",
                                                         font = self.sans8, default = "Smoothness dial",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)


    def set_Repro_Pos_Scale(self, px, py, sx, sy, sz):
        print(px, py, sx, sy, sz)
        if self.VoxelBased_repro:
            OBJ_Repro = self.current_Object.voxels()[self.currentVoxel].OBJ_repro
        else:
            OBJ_Repro = self.current_Object.OBJ_repro()
            if not OBJ_Repro:
                OBJ_Repro = self.current_Object.voxels()[self.currentVoxel].OBJ_repro
        if OBJ_Repro:
            OBJ_Repro.tune_Position_And_Scale((px, py, sx, sy, sz))
            self.update_frame(self.objectList)

    def Repro_Pos_Scale_dialog(self):
        if self.msg_box_Position_Scale_size != None and self.msg_box_Position_Scale_size.winfo_exists():
            self.msg_box_Position_Scale_size.lift_it()
            self.msg_box_Position_Scale_size.focus_set()
            self.msg_box_Position_Scale_size.ok_button.focus()
        else:
            if self.VoxelBased_repro:
                OBJ_Repro = self.current_Object.voxels()[self.currentVoxel].OBJ_repro
            else:
                OBJ_Repro = self.current_Object.OBJ_repro()
                if not OBJ_Repro:
                    OBJ_Repro = self.current_Object.voxels()[self.currentVoxel].OBJ_repro
            if OBJ_Repro:
                (px, py, sx, sy, sz) = OBJ_Repro.return_Pos_And_Scale()
            else:
                (px, py, sx, sy, sz) = (0, 0, 1.0, 1.0, 1.0)

            self.msg_box_Position_Scale_size = messageBox.Position_Scale_size(parent = self.root, root = self, ok = 'set_Repro_Pos_Scale',
                                                         T = "Set Pos Scale", sx = sx, sy = sy, sz = sz, px = px, py = py,
                                                         font = self.sans8, default = "Set Pos Scale",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def set_repro_rotation(self):
        if self.msg_box_repro_rotation != None and self.msg_box_repro_rotation.winfo_exists():
            self.msg_box_repro_rotation.lift_it()
            self.msg_box_repro_rotation.focus_set()
            self.msg_box_repro_rotation.ok_button.focus()
        else:
            self.msg_box_Pic_rotation = messageBox.Rotation_size(parent = self.root, root = self, ok = 'randomize_repro_spin',
                                                         T = "Set Repro Rotation Size", rotation = self.repro_random_rot,
                                                         font = self.sans8, default = "Set Repro Rotation Size",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def set_pic_rotation(self):
        if self.msg_box_Pic_rotation != None and self.msg_box_Pic_rotation.winfo_exists():
            self.msg_box_Pic_rotation.lift_it()
            self.msg_box_Pic_rotation.focus_set()
            self.msg_box_Pic_rotation.ok_button.focus()
        else:
            self.msg_box_Pic_rotation = messageBox.Rotation_size(parent = self.root, root = self, ok = 'set_pic_rot',
                                                         T = "Set Rotation Size", rotation = self.random_rot,
                                                         font = self.sans8, default = "Set Rotation Size",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def set_pic_rot(self, r):
        self.random_rot = r
        self.Screen.random_rot = r
        if self.current_Object.collected():
            init_images(self.current_Object.voxels()[self.currentVoxel].image, self.random_rot, self.RotCombine, self.ImageCombo)
            self.current_Object.set_voxel_images()
        elif self.VoxelBased:
            init_images(self.current_Object.voxels()[self.currentVoxel].image, self.random_rot, self.RotCombine, self.ImageCombo)
            self.current_Object.voxels()[self.currentVoxel].set_images()
        else:
            init_images(self.current_Object.image(), self.random_rot, self.RotCombine, self.ImageCombo)
            self.current_Object.set_images()
        self.update_frame(self.objectList)

    def randomize_repro_spin(self, rotation):
        self.repro_random_rot = rotation
        i = self.current_Object
        if i.collected():
            voxels = None
        elif self.VoxelBased_repro:
            voxels = [i.voxels()[i.highlighted()],]
        else:
            voxels = i.voxels()
        i.set_spin_random(self.repro_random_rot, voxels)
        self.update_frame(self.objectList)

    def set_vector_smooth(self, smooth):
        if smooth < 1:
            smooth = 1
        self.VectorSmooth = smooth

    def set_VectorSmooth(self):
        if self.msg_box_vector_smooth != None and self.msg_box_vector_smooth.winfo_exists():
            self.msg_box_vector_smooth.lift_it()
            self.msg_box_vector_smooth.focus_set()
            self.msg_box_vector_smooth.ok_button.focus()
        else:
            self.msg_box_vector_smooth = messageBox.Spin_size(parent = self.root, root = self, ok = 'set_vector_smooth',
                                                         T = "Modulate Smooth", rotation = self.VectorSmooth,
                                                         font = self.sans8, default = "Modulate VectorSmooth",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)


    def set_spin(self, spin):
        self.spin = spin
        i = self.current_Object
        if i.collected():
            voxels = None
        elif self.VoxelBased_repro:
            voxels = [i.voxels()[i.highlighted()],]
        else:
            voxels = i.voxels()
        i.set_spin(deg2rad(spin), voxels)

    def set_repro_spin(self):
        if self.msg_box_repro_spin != None and self.msg_box_repro_spin.winfo_exists():
            self.msg_box_repro_spin.lift_it()
            self.msg_box_repro_spin.focus_set()
            self.msg_box_repro_spin.ok_button.focus()
        else:
            self.msg_box_repro_spin = messageBox.Spin_size(parent = self.root, root = self, ok = 'set_spin',
                                                         T = "Set Repro Spin", rotation = self.spin,
                                                         font = self.sans8, default = "Set Repro Spin",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def randomize_spin_amount(self):
        i = self.current_Object
        if i.collected():
            voxels = None
        elif self.VoxelBased_repro:
            voxels = [i.voxels()[i.highlighted()],]
        else:
            voxels = i.voxels()
        i.set_spin_amount_random(voxels)

    def set_spin_amount(self, amount):
        self.spin_amount = amount
        i = self.current_Object
        if i.collected():
            voxels = None
        elif self.VoxelBased_repro:
            voxels = [i.voxels()[i.highlighted()],]
        else:
            voxels = i.voxels()
        i.set_spin_amount(deg2rad(amount), voxels)

    def set_repro_spin_amount(self):
        if self.msg_box_repro_spin_amount != None and self.msg_box_repro_spin_amount.winfo_exists():
            self.msg_box_repro_spin_amount.lift_it()
            self.msg_box_repro_spin_amount.focus_set()
            self.msg_box_repro_spin_amount.ok_button.focus()
        else:
            self.msg_box_repro_spin_amount = messageBox.Spin_size(parent = self.root, root = self, ok = 'set_spin_amount',
                                                         T = "Set Spin Amount", rotation = self.spin_amount,
                                                         font = self.sans8, default = "Set Spin Amount",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def set_scene_name(self, n):
        global sceneDir, previousScene
        previousScene = sceneDir
        sceneDir = n
        if os.path.exists(sceneDir):
            self.root.title("World Pixel (Exists, Load ...) " + sceneDir)
        else:
            self.root.title("World Pixel (New Name) " + sceneDir)

    def set_scene_name_dialog(self):
        if self.msg_box_Scene_name != None and self.msg_box_Scene_name.winfo_exists():
            self.msg_box_Scene_name.lift_it()
            self.msg_box_Scene_name.focus_set()
            self.msg_box_Scene_name.ok_button.focus()
        else:
            self.msg_box_Scene_name = messageBox.Scene_name(parent = self.root, root = self, ok = 'set_scene_name',
                                                         T = "Set Scene Name", filename = sceneDir,
                                                         font = self.sans8, default = "Set Scene Name",
                                                         RWidth = self.RWidth, RHeight = self.RHeight,
                                                         bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def save_frame_as_pict(self):
        self.wm_update = False
        if self.outPutDir is not None:
            currentDir = self.outPutDir
        else:
            currentDir = os.getcwd()
        fileName = "SingleFrame" + str(self.frame) + ".png"
        outPutFileName = asksaveasfilename(title = "Choose Pict FileName", initialdir = currentDir, initialfile = fileName)
        (outPutDir, fileName) = os.path.split(outPutFileName)
        if os.path.isdir(outPutDir):
            image = self.Screen[0]
            (w, h) = image.size
            background = None
            backgroundAlpha = self.backgroundAlpha
            if self.clearcolor_Compose:
                color = list(self.clear_color[:-1])
                alpha = 255 - color[-1]
                color.append(255)
                background = Image.new("RGBA", (w, h), tuple(color))
                #backgroundAlpha = Image.new('L', (w, h), color = alpha)
            if self.saveBackground and self.backgroundImage:
                if not  background:
                    background = Image.new("RGBA", (w, h))
                background.paste(self.backgroundImage, (0, 0), backgroundAlpha)
                img = Image.alpha_composite(background, image)
                img.save(outPutFileName)
            elif self.clearcolor_Compose:
                img = Image.alpha_composite(background, image)
                img.save(outPutFileName)
            else:
                image.save(outPutFileName)
            self.outPutDir = outPutDir
            self.CVar1.set("SingleFrame written into " + outPutDir + " directory!")
            print("file written to ", outPutDir)
        else:
            self.CVar1.set("SingleFrame not written!")
            print("SingleFrame not written!")
        self.wm_update = True

    def display_rendered(self):
        if len(self.AnimSequence) < 1:
            print("fill animation first!")
            return

        if self.SDL_bind:
            self.open_DragAndDropView(noimage = True)


        outPutDir    = self.output_folder
        outPutName   = self.output_filename
        outPutFormat = self.output_format
        animLength   = self.render_frames

        formatstring = "%0" + str(len(outPutFormat)) + "d"

        print(str(formatstring))

        self.stop_animation()
        self.stop_Rotation()
        frame = 0
        length = len(self.AnimSequence)
        
        self.setup_progress(animLength, RWidth = self.RWidth, RHeight = self.RHeight, downhill = True)

        anim = 0
        print(animLength)
        rate = 10 / float(fps)
        while anim <= animLength:
            for i in range(length):
                try:
                    imag1 = Image.open(outPutDir + outPutName + str(formatstring) % anim + ".png")
                    if imag1:
                        t = time.time()
                        self.display_a_frame(imag1)
                        t = time.time() - t
                        if t < rate:
                            time.sleep(rate - t)
                except(Exception) as detail:
                    print(detail)
                frame += 1
                anim += 1
                if anim > animLength:
                    break
                if frame > length:
                    frame = 0
                if self.progressbar == None:
                    return
                else:
                    self.progressbar.advance()
            if anim > animLength:
                break
        self.quit_progress()
        self.CVar2.set(str(len(self.AnimSequence)) + " frames played")

    def display_a_frame(self, image):
        if self.DragAndDropView != None and self.DragAndDropView.winfo_exists():
            canvas = self.DragAndDropView.canvas
        else:
            canvas = self.canvas
        if self.SDL_bind and not self.DragAndDropView:
            pygame.display.flip()
        else:
            self.screen = ImageTk.PhotoImage(image, 'r')
            canvas.delete('Screen')
            canvas.create_image(offset_2w, offset_2h, image = self.screen, anchor = tk.NW, tags = "Screen")
            canvas.update()

    def blit_to_screen(self):
        if self.SDL_bind:
            pygame.display.flip()
        else:
            self.screen = ImageTk.PhotoImage(self.Screen[0], 'r')
            self.canvas.delete('Screen')
            self.canvas.create_image(offset_2w, offset_2h, image = self.screen, anchor = tk.NW, tags = "Screen")
            self.canvas.tag_raise('Corner')
            self.canvas.update()

    def z_sort_objects(self, objects):
        o = []
        c = []
        d = 5.0 / (float(self.Depth_factor.get()) + 1.0)
        for i in objects:
            center = i.cube().give_center_parent()
            if d and center[-1] > d:
                continue
            else:
                o.append(i)
                c.append(center)
                
        min_list = []
        values = []
        values = [(-((center[0] + 1)**2 + (center[1] + 1)**2 + (center[2] - 100)**2), x) for center, x in zip(c, o)]
        values.sort(key = lambda tup: tup[0])
        min_list = [val for (key, val) in values]
        return min_list

    def undo_rest(self, objects):
        self.objectList = objects
        self.validate_Local()        

    def isolate_object(self, objects, update = True):
        self.current_Object = objects[0]
        self.objectList = [self.current_Object,]
        self.validate_Local()
        if update:
            self.update_frame(self.objectList)

    def toggle_ImageCombo(self):
        self.ImageCombo = self.Image_Combo.get()

    def set_rotation_combine(self):
        self.RotCombine = not self.RotCombine
        self.rot_Combine.set(self.RotCombine)

    def toggle_clear_color_Compose(self):
        self.clearcolor_Compose = self.clear_color_Compose.get()

    def toggle_save_background(self):
        self.saveBackground = self.save_Background.get()

    def set_draw_Cube(self, mode = True):
        for i in self.ObjectList:
            i.set_draw_Cube(mode)

    def toggle_draw_Cube_All(self):
        self.drawCube = not self.drawCube
        for i in self.ObjectList:
            i.set_draw_Cube(self.drawCube)
        self.update_object_frame(self.objectList)

    def toggle_draw_Cube(self):
        self.current_Object.toggle_draw_Cube()
        self.update_object_frame(self.objectList)

    def toggle_draft_Mode(self):
        self.current_Object.toggle_draft_Mode()
        self.update_frame(self.objectList)

    def validate_Local(self):
        for x, i in zip(self.Local, self.ObjectList):
            if i in self.objectList:
                x.set(True)
            else:
                x.set(False)

    def scroll_objects(self, direction):
        values = [(x.Name, x) for x in self.objectList]
        values.sort()
        objectList = [val for (key, val) in values]
        if len(objectList) > 1:
            index_to_select = objectList.index(self.current_Object)
            index_to_select += direction
            if index_to_select >= len(objectList):
                index_to_select = 0
            elif index_to_select < 0:
                index_to_select = len(objectList) - 1
            object_to_select = objectList[index_to_select]
            self.select_object(object_to_select)

    def toggle_object(self, object_to_toggle):
        if object_to_toggle in self.objectList:
            self.deselect_object(object_to_toggle)
        else:
            self.select_object(object_to_toggle)

    def deselect_object(self, object_to_deselect):
        if object_to_deselect in self.objectList:
            self.objectList.pop(self.objectList.index(object_to_deselect))
            if self.objectList:
                self.select_object(self.objectList[-1])
            else:
                self.update_frame(self.objectList)

    def update_objects(self):
        for i in self.objectList:
            i.clear_highlight()
            i.clear_illumination()
        #self.update_object_frame(self.objectList)

    def select_object(self, object_to_select, update = True):
        rest_of_the_objects = []
        for i in self.objectList:
            if i is not object_to_select:
                rest_of_the_objects.append(i)

        self.current_Object = object_to_select
        self.current_Object.set_picmap(True)
        self.currentVoxel = self.current_Object.highlighted()
        self.current_Object.get_highlight(self.currentVoxel)
        self.falloff = self.current_Object.falloff()
        self.checkFalloff.set(self.falloff)
        self.EntryVar1.set(self.currentVoxel)
        self.objectList = [object_to_select,] + rest_of_the_objects
        self.setup_numpy([object_to_select,])
        episode = self.ObjectList.index(self.current_Object)
        if self.Animation[episode] is not None:
            self.AnimSequence = self.Animation[episode]
        for i in self.objectList:
            episode = self.ObjectList.index(i)
            if self.Animation[episode] is None:
                self.Animation[episode] = self.AnimSequence.copy()
            i.set_depth(self.Depth)
            if i != self.current_Object:
                i.set_picmap(False)
                i.clear_highlight()
        if self.localCenter:
            if self.OBJ_bind:
                vector = self.current_Object.cube3d().get_local()
                self.angle = self.current_Object.cube3d().angle
            else:
                vector = self.current_Object.local()
                self.angle = self.current_Object.angle()
            self.EntryVar.set(vector)

        if update:
            self.validate_Local()
            self.sync_VoxelDim()
            self.update_object_frame(self.objectList)

    def give_array(self, x):
        return math.cos(x)

    def Vector_AnimSequence_random(self, objects = None, write = True, frame_go = True):
        if objects == None:
            objects = self.objectList
        self.setup_numpy(objects, force = True)

        try:
            i = self.ObjectList.index(self.current_Object)
            s = self.Animation[i].shape
        except:
            s = self.AnimSequence.shape

        level = self.current_Object[self.currentVoxel].level

        self.get_dimension()

        if self.synchronize:
            frames = self.animLength
            for i in self.objectList:
                if i is not self.current_Object:
                    i.set_highlighted(level)
                    i.setup_array(self.dim)
        else:
            frames = s[0]
        global Xdim, Ydim, Zdim
        (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()

        VectorAnimSequence = ones((frames, Xdim, Ydim, Zdim, 1), dtype = object)

        A1 = self.current_Object.animated_Cube()

        l = s[1] * s[2] * s[3]
        L = Xdim * Ydim * Zdim

        collected = self.current_Object.collected()
        if collected:
            locations = self.current_Object.get_portion_of_cube(Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
        else:
            locations = None

        f = 0
        f_2 = frames / 2
        for i in range(frames):
            a = zeros((Xdim, Ydim, Zdim, 1), dtype = list)
            for x in range(Xdim):
                f += 1
                for y in range(Ydim):
                    f += 1
                    for z in range(Zdim):
                        f += 1
                        F = f % 2
                        if F:
                            I = abs(f_2 - i)
                        else:
                            I = i
                        if locations != None:
                            if locations[x, y, z] != 0:
                                v = self.VectorAnimSequence[I][x, y, z][0]
                            else:
                                v = self.VectorAnimSequence[i][x, y, z][0]
                        else:
                            v = self.VectorAnimSequence[I][x, y, z][0]
                        a[x, y, z] = [v,]
            VectorAnimSequence[i] = a
        self.VectorAnimSequence = VectorAnimSequence
        if self.synchronize:
            for i in self.objectList:
                dim = i.get_dimension()
                if dim <= self.dim:
                    episode = self.ObjectList.index(i)
                    self.VectorAnimation[episode] = VectorAnimSequence
        else:
            i = self.ObjectList.index(self.current_Object)
            self.VectorAnimation[i] = VectorAnimSequence.copy()
        if frame_go:
            self.goto_animation_frame(objects, self.Time)
        self.CVar4.set("frames:" + str(self.animLength) + ",dimension:" + str(self.dim))
        print("Animation randomized!")
        if write:
            self.write_Vector_AnimSequence_file([self.current_Object,])

    def AnimSequence_random(self, objects = None, write = True, frame_go = True):
        if objects == None:
            objects = self.objectList
        self.setup_numpy(objects, force = True)

        try:
            i = self.ObjectList.index(self.current_Object)
            s = self.Animation[i].shape
        except:
            s = self.AnimSequence.shape

        level = self.current_Object[self.currentVoxel].level

        self.get_dimension()

        if self.synchronize:
            frames = self.animLength
            for i in self.objectList:
                if i is not self.current_Object:
                    i.set_highlighted(level)
                    i.setup_array(self.dim)
        else:
            frames = s[0]
        global Xdim, Ydim, Zdim
        (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()

        AnimSequence = ones((frames, Xdim, Ydim, Zdim, 2), dtype = object)

        A1 = self.current_Object.animated_Cube()

        l = s[1] * s[2] * s[3]
        L = Xdim * Ydim * Zdim

        collected = self.current_Object.collected()
        if collected:
            locations = self.current_Object.get_portion_of_cube(Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
        else:
            locations = None

        f = 0
        f_2 = frames / 2
        for i in range(frames):
            a = zeros((Xdim, Ydim, Zdim, 2), dtype = list)
            for x in range(Xdim):
                f += 1
                for y in range(Ydim):
                    f += 1
                    for z in range(Zdim):
                        f += 1
                        F = f % 2
                        if F:
                            I = abs(f_2 - i)
                        else:
                            I = i
                        if locations != None:
                            if locations[x, y, z] != 0:
                                v = self.AnimSequence[I][x, y, z][0]
                                C = self.AnimSequence[I][x, y, z][1]
                            else:
                                v = self.AnimSequence[i][x, y, z][0]
                                C = self.AnimSequence[i][x, y, z][1]
                        else:
                            v = self.AnimSequence[I][x, y, z][0]
                            C = self.AnimSequence[I][x, y, z][1]                            

                        a[x, y, z] = (v, C)
            AnimSequence[i] = a
        self.AnimSequence = AnimSequence
        if self.synchronize:
            for i in self.objectList:
                dim = i.get_dimension()
                if dim <= self.dim:
                    episode = self.ObjectList.index(i)
                    self.Animation[episode] = AnimSequence
        else:
            i = self.ObjectList.index(self.current_Object)
            self.Animation[i] = AnimSequence.copy()
        if frame_go:
            self.goto_animation_frame(objects, self.Time)
        self.CVar4.set("frames:" + str(self.animLength) + ",dimension:" + str(self.dim))
        print("Animation randomized!")
        if write:
            self.write_AnimSequence_file([self.current_Object,])

    def VectorAnimSequence_fill(self, objects = None, write = True, frame_go = True):
        if objects == None:
            objects = self.objectList
        self.setup_numpy(objects, force = True)

        try:
            i = self.ObjectList.index(self.current_Object)
            s = self.Animation[i].shape
        except:
            s = self.AnimSequence.shape

        level = self.current_Object[self.currentVoxel].level

        self.get_dimension()

        if self.synchronize:
            frames = self.animLength
            for i in self.objectList:
                if i is not self.current_Object:
                    i.set_highlighted(level)
                    i.setup_array(self.dim)
        else:
            frames = s[0]
        global Xdim, Ydim, Zdim
        (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()

        VectorAnimSequence = ones((frames, Xdim, Ydim, Zdim, 1), dtype = object)

        A1 = self.current_Object.animated_Cube()

        l = s[1] * s[2] * s[3]
        L = Xdim * Ydim * Zdim

        collected = self.current_Object.collected()
        if collected:
            locations = self.current_Object.get_portion_of_cube(Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
        else:
            locations = None

        c = level * 2
        f = 0.0
        step = pi * 2 / float(frames - 1)
        size = level * 2.0
        dim = self.dim
        self.setup_progress(frames)
        for i in range(frames):
            self.progressbar.advance("\ngenerating Vector Animation\n")
            a = zeros((Xdim, Ydim, Zdim, 1), dtype = list)
            for x in range(Xdim):
                f += step
                for y in range(Ydim):
                    f += step
                    for z in range(Zdim):
                        f += step
                        (X0, Y0, Z0) = eval(self.Vectorsentence)
                        X1 = 0
                        Y1 = 0
                        Z1 = 0
                        try:
                            C = self.AnimSequence[i][x, y, z][1]
                        except:
                            C = None
                        if C is not None:
                            X1 = 255 / float(C[0])
                            Y1 = 255 / float(C[1])
                            Z1 = 255 / float(C[2])
                        x_w0 = 1 / float(abs((Xdim / 2) - x) + self.VectorSmooth)
                        x_w1 = 1 - x_w0
                        y_w0 = 1 / float(abs((Ydim / 2) - y) + self.VectorSmooth)
                        y_w1 = 1 - y_w0
                        z_w0 = 1 / float(abs((Zdim / 2) - z) + self.VectorSmooth)
                        z_w1 = 1 - z_w0
                        X = X0 * x_w1 + X1 * x_w0
                        Y = Y0 * y_w1 + Y1 * y_w0
                        Z = Z0 * z_w1 + Z1 * z_w0

                        if locations is not None:
                            if locations[x, y, z] != 0:
                                V = [X, Y, Z]
                            else:
                                try:
                                    V = self.VectorAnimSequence[i][x, y, z][0]
                                except:
                                    V = None
                        else:
                            V = [X, Y, Z]
                        a[x, y, z] = [V,]
            VectorAnimSequence[i] = a
        self.quit_progress()
        self.VectorAnimSequence = VectorAnimSequence
        if self.synchronize:
            for i in self.objectList:
                dim = i.get_dimension()
                if dim <= self.dim:
                    episode = self.ObjectList.index(i)
                    self.VectorAnimation[episode] = VectorAnimSequence
        else:
            i = self.ObjectList.index(self.current_Object)
            self.VectorAnimation[i] = VectorAnimSequence.copy()
        if frame_go:
            self.goto_animation_frame(objects, self.Time)
        self.CVar4.set("frames:" + str(self.animLength) + ",dimension:" + str(self.dim))
        print("Animation filled!")
        if write:
            self.write_Vector_AnimSequence_file([self.current_Object,])

    def AnimSequence_fill(self, objects = None, write = True, frame_go = True, unravel = False):
        if objects == None:
            objects = self.objectList
        self.setup_numpy(objects, force = True)

        try:
            i = self.ObjectList.index(self.current_Object)
            s = self.Animation[i].shape
        except:
            s = self.AnimSequence.shape

        level = self.current_Object[self.currentVoxel].level

        self.get_dimension()

        if self.synchronize:
            frames = self.animLength
            for i in self.objectList:
                if i is not self.current_Object:
                    i.set_highlighted(level)
                    i.setup_array(self.dim)
        else:
            frames = s[0]
        global Xdim, Ydim, Zdim
        (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()

        AnimSequence = ones((frames, Xdim, Ydim, Zdim, 2), dtype = object)

        A1 = self.current_Object.animated_Cube()

        l = s[1] * s[2] * s[3]
        L = Xdim * Ydim * Zdim

        collected = self.current_Object.collected()
        if collected:
            locations = self.current_Object.get_portion_of_cube(Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
        else:
            locations = None

        a1 = self.AlphaEntryVar1.get()
        a2 = self.AlphaEntryVar2.get()
        (M2, N2) = self.func_0_1(255, a2)
        (M1, N1) = self.func_0_1(255, a1)

        c = level * 2
        f = 0.0
        step = pi * 2 / float(frames - 1)
        size = level * 2.0
        dim = self.dim
        self.setup_progress(frames)
        r = 0.0
        #r_step = (dim * 4) / float(frames)
        r_step = step * 4
        s_ = 0.0
        s_step = L / float(frames - 1)
        for i in range(frames):
            self.progressbar.advance("\ngenerating Animation\n")
            r += r_step
            s_ += s_step
            a = zeros((Xdim, Ydim, Zdim, 2), dtype = list)
            for x in range(Xdim):
                f += step
                for y in range(Ydim):
                    f += step
                    for z in range(Zdim):
                        f += step
                        if locations is not None:
                            if locations[x, y, z] != 0:
                                if unravel:
                                    (x_i, y_i, z_i) = eval(self.Unravelsentence)
                                    if self.X_r:
                                        x_r = (x_i - x) ** 2
                                    else:
                                        x_r = 0
                                    if self.Y_r:
                                        y_r = (y_i - y) ** 2
                                    else:
                                        y_r = 0
                                    if self.Z_r:
                                        z_r = (z_i - z) ** 2
                                    else:
                                        z_r = 0
                                    v = (2.0 / (sqrt(x_r + y_r + z_r) + 1)) * c
                                else:
                                    v = eval(self.sentence)
                                if v != None:
                                    if self.setColor:
                                        (m, n) = self.func_0_1(size, v)
                                        try:
                                            color = self.AnimSequence[i][x, y, z][1]
                                        except:
                                            color = None
                                        if color is None:
                                            try:
                                                voxel = A1[x + Xbound[0], y + Ybound[0], z + Zbound[0]]
                                                color = self.current_Object[voxel].color
                                            except:
                                                pass
                                        if color is not None:
                                            fgcolor =       (self.fgcolor[0] * M2 + color[0] * N2,
                                                             self.fgcolor[1] * M2 + color[1] * N2,
                                                             self.fgcolor[2] * M2 + color[2] * N2)
                                            bgcolor =       (self.bgcolor[0] * M1 + color[0] * N1,
                                                             self.bgcolor[1] * M1 + color[1] * N1,
                                                             self.bgcolor[2] * M1 + color[2] * N1)
                                            C =             (fgcolor[0] * m + bgcolor[0] * n,
                                                             fgcolor[1] * m + bgcolor[1] * n,
                                                             fgcolor[2] * m + bgcolor[2] * n)
                                        else:
                                            C =             (self.fgcolor[0] * m + self.bgcolor[0] * n,
                                                             self.fgcolor[1] * m + self.bgcolor[1] * n,
                                                             self.fgcolor[2] * m + self.bgcolor[2] * n)
                                    else:
                                        try:
                                            C = self.AnimSequence[i][x, y, z][1]
                                        except:
                                            C = None
                                else:
                                    try:
                                        v = self.AnimSequence[i][x, y, z][0]
                                        C = self.AnimSequence[i][x, y, z][1]
                                    except:
                                        v = None
                                        C = None
                            else:
                                try:
                                    v = self.AnimSequence[i][x, y, z][0]
                                    C = self.AnimSequence[i][x, y, z][1]
                                except:
                                    v = None
                                    C = None
                        else:
                            if unravel:
                                (x_i, y_i, z_i) = eval(self.Unravelsentence)
                                if self.X_r:
                                    x_r = (x_i - x) ** 2
                                else:
                                    x_r = 0
                                if self.Y_r:
                                    y_r = (y_i - y) ** 2
                                else:
                                    y_r = 0
                                if self.Z_r:
                                    z_r = (z_i - z) ** 2
                                else:
                                    z_r = 0
                                v = (2.0 / (sqrt(x_r + y_r + z_r) + 1)) * c
                            else:
                                v = eval(self.sentence)
                            C = None
                            if v != None:
                                if self.setColor:
                                    (m, n) = self.func_0_1(size, v)
                                    try:
                                        color = self.AnimSequence[i][x, y, z][1]
                                    except:
                                        color = None
                                    if color is None:
                                        try:
                                            voxel = A1[x + Xbound[0], y + Ybound[0], z + Zbound[0]]
                                            color = self.current_Object[voxel].color
                                        except:
                                            pass
                                    if color is not None:
                                        fgcolor =       (self.fgcolor[0] * M2 + color[0] * N2,
                                                         self.fgcolor[1] * M2 + color[1] * N2,
                                                         self.fgcolor[2] * M2 + color[2] * N2)
                                        bgcolor =       (self.bgcolor[0] * M1 + color[0] * N1,
                                                         self.bgcolor[1] * M1 + color[1] * N1,
                                                         self.bgcolor[2] * M1 + color[2] * N1)
                                        C =             (fgcolor[0] * m + bgcolor[0] * n,
                                                         fgcolor[1] * m + bgcolor[1] * n,
                                                         fgcolor[2] * m + bgcolor[2] * n)
                                    else:
                                        C =             (self.fgcolor[0] * m + self.bgcolor[0] * n,
                                                         self.fgcolor[1] * m + self.bgcolor[1] * n,
                                                         self.fgcolor[2] * m + self.bgcolor[2] * n)
                                else:
                                    try:
                                        C = self.AnimSequence[i][x, y, z][1]
                                    except:
                                        C = None
                        if not self.setShape:
                            v = None
                            if l == L:
                                try:
                                    v = self.AnimSequence[i][x, y, z][0]
                                except:
                                    pass
                        a[x, y, z] = (v, C)
            AnimSequence[i] = a
        self.quit_progress()
        self.AnimSequence = AnimSequence
        if self.synchronize:
            for i in self.objectList:
                dim = i.get_dimension()
                if dim <= self.dim:
                    episode = self.ObjectList.index(i)
                    self.Animation[episode] = AnimSequence
        else:
            i = self.ObjectList.index(self.current_Object)
            self.Animation[i] = AnimSequence.copy()
        if frame_go:
            self.goto_animation_frame(objects, self.Time)
        self.CVar4.set("frames:" + str(self.animLength) + ",dimension:" + str(self.dim))
        print("Animation filled!")
        if write:
            self.write_AnimSequence_file([self.current_Object,])

    def Vector_Animation_fill(self, objects = None, write = True, frame_go = True, smoothed = False):
        if objects == None:
            objects = self.objectList
        self.setup_numpy(objects, force = True)

        try:
            i = self.ObjectList.index(self.current_Object)
            s = self.Animation[i].shape
        except:
            s = self.AnimSequence.shape

        level = self.current_Object[self.currentVoxel].level

        self.get_dimension()

        if self.synchronize:
            frames = self.animLength
            for i in self.objectList:
                if i is not self.current_Object:
                    i.set_highlighted(level)
                    i.setup_array(self.dim)
        else:
            frames = s[0]
        global Xdim, Ydim, Zdim
        (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()

        episode = self.ObjectList.index(self.current_Object)
        try:
            AnimSequence = self.Animation[episode]
        except:
            AnimSequence = self.AnimSequence

        VectorAnimSequence = zeros((frames, Xdim, Ydim, Zdim, 1), dtype = object)

        A1 = self.current_Object.animated_Cube()

        l = s[1] * s[2] * s[3]
        L = Xdim * Ydim * Zdim

        collected = self.current_Object.collected()
        if collected:
            locations = self.current_Object.get_portion_of_cube(Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
        else:
            locations = None

        c = level * 2
        f = 0.0
        step = pi * 2 / float(frames - 1)
        size = level * 2.0
        dim = self.dim
        self.setup_progress(frames)
        for i in range(frames):
            self.progressbar.advance("\ngenerating Smooth Vector\n")
            a = zeros((Xdim, Ydim, Zdim, 1), dtype = list)
            for x in range(Xdim):
                f += step
                for y in range(Ydim):
                    f += step
                    for z in range(Zdim):
                        f += step
                        i_ = i - 1
                        v0 = AnimSequence[i_][x, y, z][0]
                        v1 = AnimSequence[i][x, y, z][0]
                        try:
                            speed = v1 - v0
                        except:
                            speed = 0
                        if x - 1 < 0:
                            x_ = Xdim - 1
                        else:
                            x_ = x - 1
                        v_0 = AnimSequence[i_][x_, y, z][0]
                        v_1 = AnimSequence[i][x_, y, z][0]
                        try:
                            speed_0 = v_1 - v_0
                        except:
                            speed_0 = 0
                        if x + 1 > Xdim - 1:
                            x__ = 0
                        else:
                            x__ = x + 1
                        v__0 = AnimSequence[i_][x__, y, z][0]
                        v__1 = AnimSequence[i][x__, y, z][0]
                        try:
                            speed_1 = v__1 - v__0
                        except:
                            speed_1 = 0
                        if speed - speed_0 > speed - speed_1:
                            X0 = speed - speed_0
                        elif speed - speed_0 < speed - speed_1:
                            X0 = speed - speed_1
                        else:
                            X0 = 0
                        if y - 1 < 0:
                            y_ = Ydim - 1
                        else:
                            y_ = y - 1
                        v_0 = AnimSequence[i_][x, y_, z][0]
                        v_1 = AnimSequence[i][x, y_, z][0]
                        try:
                            speed_0 = v_1 - v_0
                        except:
                            speed_0 = 0
                        if y + 1 > Ydim - 1:
                            y__ = 0
                        else:
                            y__ = y + 1
                        v__0 = AnimSequence[i_][x, y__, z][0]
                        v__1 = AnimSequence[i][x, y__, z][0]
                        try:
                            speed_1 = v__1 - v__0
                        except:
                            speed_1 = 0
                        if speed - speed_0 > speed - speed_1:
                            Y0 = speed - speed_0
                        elif speed - speed_0 < speed - speed_1:
                            Y0 = speed - speed_1
                        else:
                            Y0 = 0
                        if z - 1 < 0:
                            z_ = Zdim - 1
                        else:
                            z_ = z - 1
                        v_0 = AnimSequence[i_][x, y, z_][0]
                        v_1 = AnimSequence[i][x, y, z_][0]
                        try:
                            speed_0 = v_1 - v_0
                        except:
                            speed_0 = 0
                        if z + 1 > Zdim - 1:
                            z__ = 0
                        else:
                            z__ = z + 1
                        v__0 = AnimSequence[i_][x, y, z__][0]
                        v__1 = AnimSequence[i][x, y, z__][0]
                        try:
                            speed_1 = v__1 - v__0
                        except:
                            speed_1 = 0
                        if speed - speed_0 > speed - speed_1:
                            Z0 = speed - speed_0
                        elif speed - speed_0 < speed - speed_1:
                            Z0 = speed - speed_1
                        else:
                            Z0 = 0
                        if smoothed:
                            X1 = 0
                            Y1 = 0
                            Z1 = 0
                            try:
                                C = self.AnimSequence[i][x, y, z][1]
                            except:
                                C = None
                            if C is not None:
                                X1 = 255 / float(C[0])
                                Y1 = 255 / float(C[1])
                                Z1 = 255 / float(C[2])
                            x_w0 = 1 / float(abs((Xdim / 2) - x) + self.VectorSmooth)
                            x_w1 = 1 - x_w0
                            y_w0 = 1 / float(abs((Ydim / 2) - y) + self.VectorSmooth)
                            y_w1 = 1 - y_w0
                            z_w0 = 1 / float(abs((Zdim / 2) - z) + self.VectorSmooth)
                            z_w1 = 1 - z_w0
                            X = X0 * x_w1 + X1 * x_w0
                            Y = Y0 * y_w1 + Y1 * y_w0
                            Z = Z0 * z_w1 + Z1 * z_w0
                        else:
                            X = X0
                            Y = Y0
                            Z = Z0                            
                        if locations != None:
                            if locations[x, y, z] != 0:
                                V = [float(X), float(Y), float(Z)]
                            else:
                                try:
                                    V = self.VectorAnimSequence[i][x, y, z][0]
                                except:
                                    V = None
                        else:
                            V = [float(X), float(Y), float(Z)]
                        a[x, y, z] = [V,]
            VectorAnimSequence[i] = a
        self.quit_progress()
        self.VectorAnimSequence = VectorAnimSequence
        if self.synchronize:
            for i in self.objectList:
                dim = i.get_dimension()
                if dim <= self.dim:
                    episode = self.ObjectList.index(i)
                    self.VectorAnimation[episode] = VectorAnimSequence
        else:
            i = self.ObjectList.index(self.current_Object)
            self.VectorAnimation[i] = VectorAnimSequence.copy()
        if frame_go:
            self.goto_animation_frame(objects, self.Time)
        self.CVar4.set("frames:" + str(self.animLength) + ",dimension:" + str(self.dim))
        print("Vector Animation filled!")
        if write:
            self.write_Vector_AnimSequence_file([self.current_Object,])

    def print_VectorAnimation(self):
        print(self.VectorAnimSequence[0])

    def clear_component_animation(self, component):
        episode = self.ObjectList.index(self.current_Object)
        if self.current_Object.collected():
            self.get_dimension()
            self.current_Object.setup_array(self.dim, force = True)
            self.collected = self.current_Object.collected()
            S = self.current_Object.animated_Cube().shape
            (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
            self.current_Object.setup_array(self.dim, arrange = True)
            for i in self.collected:
                c = i.currency
                h = unravel_index(c, S)
                x = h[0] - Xbound[0]
                y = h[1] - Ybound[0]
                z = h[2] - Zbound[0]
                self.Animation[episode][:, x, y, z, component] = None
            self.current_Object.setup_array(self.dim, force = True)
        else:
            self.Animation[episode][:, :, :, :, component] = None
        self.AnimSequence = self.Animation[episode]

        self.write_AnimSequence_file([self.current_Object,])

    def get_dimension(self):
        level = self.current_Object[self.currentVoxel].level
        self.level.set(level)
        self.dim = int(1 / float(level))
        v = len(self.current_Object.voxels())
        s = self.AnimSequence.shape
        self.CVar3.set("self.dim:" + str(self.dim) + " / Voxels:" + str(v) + " / level:" + str(level) + " / s[1]:" + str(s[1]))

    def reset_voxels(self, objects):
        for i in objects:
            i.reset_all_voxels()
        self.update_frame(objects)

    def manifest_grays(self, objects):
        self.current_Object.shift_colors_reset()
        self.current_Object.manifest_grays(self.R, self.G, self.B)
        self.update_frame(objects)

    def manifest_color(self, objects):
        self.current_Object.shift_colors_reset()
        self.current_Object.manifest_color(self.R, self.G, self.B)
        self.update_frame(objects)

    def reset_matrix(self, objects):
        self.get_dimension()
        for i in objects:
            v = i.setup_array(self.dim)
            i.reset_matrix()
            if i == self.current_Object:
                self.currentVoxel = v
        self.update_frame(objects)

    def toggle_smooth_colors(self):
        self.smoothColors = not self.smoothColors
        self.smooth_Colors.set(self.smoothColors)

    def toggle_smooth_sizes(self):
        self.smoothSizes = not self.smoothSizes
        self.smooth_Sizes.set(self.smoothSizes)

    def perform_smoothing(self, objects, smoothColors, smoothSizes):
        for i in objects:
            i.perform_smoothing(self.smooth, smoothColors, smoothSizes)
        self.update_frame(self.objectList)

    def write_Vector_AnimSequence_file(self, objects):
        currentDir = animDir
        path = os.path.join(folders, sceneDir, currentDir)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
                return
        fileName = "vec_anim"
        fileNames = []
        for i in objects:
            dim = i.get_dimension()
            episode = self.ObjectList.index(i)
            try:
                VectorAnimSequence = self.VectorAnimation[episode]
            except:
                continue
            if VectorAnimSequence is None:
                continue
            s = VectorAnimSequence.shape
            filename = fileName + str(episode) + "_" + str(dim) + ".num"
            try:
                VectorAnimSequence.dump(os.path.join(path, filename))
                fileNames.append(filename)
                print(filename + " written!")
            except(Exception) as detail:
                print("Exception", detail)
        self.CVar1.set(str(fileNames) + " written into " + currentDir + " directory!")

    def write_AnimSequence_file(self, objects):
        currentDir = animDir
        path = os.path.join(folders, sceneDir, currentDir)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
                return
        fileName = "anim"
        fileNames = []
        for i in objects:
            dim = i.get_dimension()
            episode = self.ObjectList.index(i)
            try:
                AnimSequence = self.Animation[episode]
            except:
                continue
            if AnimSequence is None:
                continue
            s = AnimSequence.shape
            filename = fileName + str(episode) + "_" + str(dim) + ".num"
            try:
                #with open(os.path.join(path, filename), "wb") as f:
                    #f.write(str(AnimSequence.tolist()))
                AnimSequence.dump(os.path.join(path, filename))
                    #f.close()
                fileNames.append(filename)
                print(filename + " written!")
            except(Exception) as detail:
                print("Exception", detail)
        self.CVar1.set(str(fileNames) + " written into " + currentDir + " directory!")

    def write_sync_animation(self, colocated = False):
        currentDir = animDir
        path = os.path.join(folders, sceneDir, currentDir)
        if not os.path.exists(path):
            return
        dim = self.current_Object.get_dimension()
        fileName = "anim"
        fileName_1 = "vec_anim"
        episode = self.ObjectList.index(self.current_Object)
        filename = fileName + str(episode) + "_" + str(dim) + ".num"
        filename_1 = fileName_1 + str(episode) + "_" + str(dim) + ".num"
        path_0 = os.path.join(path, filename)
        path_1 = os.path.join(path, filename_1)
        if os.path.isfile(path_0):
            animexists = True
            try:
                AnimSequence = self.Animation[episode]
            except:
                animexists = False
        else:
            animexists = False
        if os.path.isfile(path_1):
            vectexists = True
            try:
                VectorAnimation = self.VectorAnimation[episode]
            except:
                vectexists = False
        else:
            vectexists = False

        conform = self.current_Object.conform_position() + self.current_Object.local_conform()

        fileNames = []
        objects = []
        for i in self.objectList[1:]:
            Dim = i.get_dimension()
            Episode = self.ObjectList.index(i)
            Conform = i.conform_position() + i.local_conform()
            if colocated:
                if str(conform) != str(Conform):
                    continue
            if Dim == dim:
                if animexists:
                    filename = fileName + str(Episode) + "_" + str(Dim) + ".num"
                    try:
                        AnimSequence.dump(os.path.join(path, filename))
                        fileNames.append(filename)
                        print(filename + " written!")
                        if i not in objects:
                            objects.append(i)
                    except(Exception) as detail:
                        print("Exception", detail)
                if vectexists:
                    filename_1 = fileName_1 + str(Episode) + "_" + str(Dim) + ".num"
                    try:
                        VectorAnimation.dump(os.path.join(path, filename_1))
                        fileNames.append(filename_1)
                        print(filename_1 + " written!")
                        if i not in objects:
                            objects.append(i)
                    except(Exception) as detail:
                        print("Exception", detail)
        self.CVar1.set(str(fileNames) + " written into " + currentDir + " directory!")
        if self.SDL_bind:
            if self.VBOFrames:
                self.toggle_Frames()
                
        self.load_into_AnimSequence(objects)
        if self.vectorAnim and self.SDL_bind:
            self.load_Vectors_into_AnimSequence(objects)
        if self.SDL_bind:
            if not self.VBOFrames:
                self.toggle_Frames()

    def load_Vectors_into_AnimSequence(self, objects, dialog = False, update = True):
        currentDir = os.path.join(folders, sceneDir, animDir)
        fileName = "vec_anim"
        fileNames = []
        if dialog:
            (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
            dim = self.current_Object.get_dimension()
            episode = self.ObjectList.index(objects[0])
            fileName = "vec_anim"
            filename = fileName + str(episode) + "_" + str(dim) + ".num"
            filename = askopenfilename(initialdir = currentDir,
                                       initialfile = filename,
                                       filetypes = (("Numpy file", "*.num")
                                                   ,("All files", "*.*")))
            path = os.path.join(currentDir, filename)

            if not os.path.isfile(path):
                return

            Animation_pick = path + str(os.stat(path).st_mtime)
            if Animation_pick == self.VectorAnimation_pick[episode]:
                return
            try:
                n = load(path)
                print(filename + " opened and read!")
            except(Exception) as detail:
                print(filename + " not opened!", detail)
                return

        if self.synchronize:
            objects = self.objectList
            if not dialog and objects:
                (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
                dim = self.current_Object.get_dimension()
                level = self.current_Object[self.currentVoxel].level
                for i in objects:
                    if i is not self.current_Object:
                        i.set_highlighted(level)
                        i.setup_array(dim)
                episode = self.ObjectList.index(objects[0])
                fileName = "vec_anim"
                filename = fileName + str(episode) + "_" + str(dim) + ".num"

                path = os.path.join(currentDir, filename)

                if not os.path.isfile(path):
                    return

                Animation_pick = path + str(os.stat(path).st_mtime)
                if Animation_pick == self.VectorAnimation_pick[episode]:
                    return
                try:
                    n = load(path)
                    print(filename + " opened and read!")
                except(Exception) as detail:
                    print(filename + " not opened!", detail)
                    return

        for i in objects:
            episode = self.ObjectList.index(i)
            dim = i.get_dimension()
            if self.synchronize and dim > self.dim:
                continue
            if not dialog and not self.synchronize:
                (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = i.give_active_bounds()
                filename = fileName + str(episode) + "_" + str(dim) + ".num"
                path = os.path.join(currentDir, filename)

                if not os.path.isfile(path):
                    continue

                Animation_pick = path + str(os.stat(path).st_mtime)
                if Animation_pick == self.VectorAnimation_pick[episode]:
                    continue

                try:
                    n = load(path)
                    print(filename + " opened and read!")
                except(Exception) as detail:
                    print(filename + " not opened!", detail)
                    continue
            v = i.setup_array(dim)

            if i == self.current_Object:
                self.currentVoxel = v

            fileNames.append(filename)
            if i == self.current_Object:
                self.VectorAnimSequence = n
            self.VectorAnimation[episode] = n
            self.VectorAnimation_pick[episode] = path + str(os.stat(path).st_mtime)
        if dialog:
            self.write_Vector_AnimSequence_file([self.current_Object,])
        self.CVar1.set("loading " + str(fileNames) + " successful!")
        if update:
            self.EntryVar3.set(self.Time)

    def load_into_AnimSequence(self, objects, dialog = False, update = True):
        currentDir = os.path.join(folders, sceneDir, animDir)
        fileName = "anim"
        fileNames = []
        if dialog:
            (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
            dim = self.current_Object.get_dimension()
            episode = self.ObjectList.index(objects[0])
            fileName = "anim"
            filename = fileName + str(episode) + "_" + str(dim) + ".num"
            filename = askopenfilename(initialdir = currentDir,
                                       initialfile = filename,
                                       filetypes = (("Numpy file", "*.num")
                                                   ,("All files", "*.*")))
            path = os.path.join(currentDir, filename)

            if not os.path.isfile(path):
                return

            Animation_pick = path + str(os.stat(path).st_mtime)
            if Animation_pick == self.Animation_pick[episode]:
                return
            try:
                if (pyversion >= 3):
                    n = load(path, allow_pickle = True)
                else:
                    n = load(path)
                print(filename + " opened and read!")
            except(Exception) as detail:
                print(filename + " not opened!", detail)
                return

        if self.synchronize:
            objects = self.objectList
            if not dialog and objects:
                (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
                dim = self.current_Object.get_dimension()
                level = self.current_Object[self.currentVoxel].level
                for i in objects:
                    if i is not self.current_Object:
                        i.set_highlighted(level)
                        i.setup_array(dim)
                episode = self.ObjectList.index(objects[0])
                fileName = "anim"
                filename = fileName + str(episode) + "_" + str(dim) + ".num"

                path = os.path.join(currentDir, filename)

                if not os.path.isfile(path):
                    return

                Animation_pick = path + str(os.stat(path).st_mtime)
                if Animation_pick == self.Animation_pick[episode]:
                    return
                try:
                    if (pyversion < 3):
                        n = load(path)
                    else:
                        n = load(path, allow_pickle = True)
                    print(filename + " opened and read!")
                except(Exception) as detail:
                    print(filename + " not opened!", detail)
                    return

        for i in objects:
            episode = self.ObjectList.index(i)
            dim = i.get_dimension()
            if self.synchronize and dim > self.dim:
                continue
            if not dialog and not self.synchronize:
                (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = i.give_active_bounds()
                filename = fileName + str(episode) + "_" + str(dim) + ".num"
                path = os.path.join(currentDir, filename)

                if not os.path.isfile(path):
                    continue

                Animation_pick = path + str(os.stat(path).st_mtime)
                if Animation_pick == self.Animation_pick[episode]:
                    continue

                try:
                    n = load(path)
                    print(filename + " opened and read!")
                except(Exception) as detail:
                    print(filename + " not opened!", detail)
                    continue
            v = i.setup_array(dim)

            if i == self.current_Object:
                self.currentVoxel = v

            fileNames.append(filename)
            if i == self.current_Object:
                self.AnimSequence = n
            self.Animation[episode] = n
            self.Animation_pick[episode] = path + str(os.stat(path).st_mtime)
        if dialog:
            self.write_AnimSequence_file([self.current_Object,])
        self.CVar1.set("loading " + str(fileNames) + " successful!")
        if update:
            self.EntryVar3.set(self.Time)

    def crossfade_vector_animations(self, dialog = False, filename_0 = "", filename_1 = ""):
        objects = self.objectList
        currentDir = os.path.join(folders, sceneDir, animDir)
        fileName = "vec_anim"
        episode = self.ObjectList.index(objects[0])
        dim = self.current_Object.get_dimension()
        fileNames = []
        if dialog:
            (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
            fileName = "vec_anim"
            filename_0 = fileName + str(episode) + "_" + str(dim) + ".num"
            filename_0 = askopenfilename(initialdir = currentDir,
                                         initialfile = filename_0,
                                         filetypes = (("Numpy file", "*.num")
                                                     ,("All files", "*.*")))
            print(filename_0)
            fileNames.append(filename_0)

            filename_1 = fileName + str(episode + 1) + "_" + str(dim) + ".num"
            filename_1 = askopenfilename(initialdir = currentDir,
                                         initialfile = filename_1,
                                         filetypes = (("Numpy file", "*.num")
                                                     ,("All files", "*.*")))
            print(filename_1)
            fileNames.append(filename_1)
        elif filename_0 and filename_1:
            pass
        else:
            self.query_anim_folder_files(self.crossfade_vector_animations, fileName, episode, dim, currentDir)
        path_0 = os.path.join(currentDir, filename_0)
        path_1 = os.path.join(currentDir, filename_1)

        if os.path.isfile(path_0) and os.path.isfile(path_1):
            pass
        else:
            return

        try:
            n_0 = load(path_0)
            print(filename_0 + " opened and read!")
        except(Exception) as detail:
            print(filename_0 + " not opened!", detail)
            return

        try:
            n_1 = load(path_1)
            print(filename_1 + " opened and read!")
        except(Exception) as detail:
            print(filename_1 + " not opened!", detail)
            return
        (frames_0, X_0, Y_0, Z_0, t_0) = n_0.shape
        (frames_1, X_1, Y_1, Z_1, t_1) = n_1.shape

        VectorAnimSequence = zeros((frames_0, X_0, Y_0, Z_0, t_0), dtype = object)

        print("frames_0", frames_0)
        F = frames_0 / 2.0
        for f in range(frames_0):
            if f >= frames_1:
                break
            for x in range(X_0):
                if x >= X_1:
                    break
                for y in range(Y_0):
                    if y >= Y_1:
                        break
                    for z in range(Z_0):
                        if z >= Z_1:
                            break
                        v_0 = n_0[f, x, y, z, 0]
                        v_1 = n_1[f, x, y, z, 0]
                        m_0 = abs(F - f) / float(F)
                        m_1 = 1.0 - m_0
                        if v_0 is not None and v_1 is not None:
                            VectorAnimSequence[f, x, y, z, 0] = array(v_0) * m_0 + array(v_1) * m_1
                        else:
                            try:
                                VectorAnimSequence[f, x, y, z, 0] = self.VectorAnimSequence[f, x, y, z, 0]
                            except:
                                pass

        self.VectorAnimation[episode] = VectorAnimSequence
        self.VectorAnimation_pick[episode] = path_0 + str(os.stat(path_0).st_mtime)
        self.write_Vector_AnimSequence_file([self.current_Object,])
        self.CVar1.set("crossfade " + str(fileNames) + " successful!")
        self.EntryVar3.set(self.Time)

    def crossfade_animations(self, dialog = False, filename_0 = "", filename_1 = ""):
        objects = self.objectList
        currentDir = os.path.join(folders, sceneDir, animDir)
        fileName = "anim"
        episode = self.ObjectList.index(objects[0])
        dim = self.current_Object.get_dimension()
        fileNames = []
        if dialog:
            (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
            fileName = "anim"
            filename_0 = fileName + str(episode) + "_" + str(dim) + ".num"
            filename_0 = askopenfilename(initialdir = currentDir,
                                         initialfile = filename_0,
                                         filetypes = (("Numpy file", "*.num")
                                                     ,("All files", "*.*")))
            print(filename_0)
            fileNames.append(filename_0)

            filename_1 = fileName + str(episode + 1) + "_" + str(dim) + ".num"
            filename_1 = askopenfilename(initialdir = currentDir,
                                         initialfile = filename_1,
                                         filetypes = (("Numpy file", "*.num")
                                                     ,("All files", "*.*")))
            print(filename_1)
            fileNames.append(filename_1)
        elif filename_0 and filename_1:
            pass
        else:
            self.query_anim_folder_files(self.crossfade_animations, fileName, episode, dim, currentDir)
        path_0 = os.path.join(currentDir, filename_0)
        path_1 = os.path.join(currentDir, filename_1)

        if os.path.isfile(path_0) and os.path.isfile(path_1):
            pass
        else:
            return

        try:
            n_0 = load(path_0)
            print(filename_0 + " opened and read!")
        except(Exception) as detail:
            print(filename_0 + " not opened!", detail)
            return

        try:
            n_1 = load(path_1)
            print(filename_1 + " opened and read!")
        except(Exception) as detail:
            print(filename_1 + " not opened!", detail)
            return
        (frames_0, X_0, Y_0, Z_0, t_0) = n_0.shape
        (frames_1, X_1, Y_1, Z_1, t_1) = n_1.shape

        AnimSequence = zeros((frames_0, X_0, Y_0, Z_0, t_0), dtype = object)
        AnimSequence.fill(None)
        print("frames_0", frames_0)
        F = frames_0 / 2.0
        for f in range(frames_0):
            if f >= frames_1:
                break
            for x in range(X_0):
                if x >= X_1:
                    break
                for y in range(Y_0):
                    if y >= Y_1:
                        break
                    for z in range(Z_0):
                        if z >= Z_1:
                            break
                        s_0 = n_0[f, x, y, z, 0]
                        c_0 = n_0[f, x, y, z, 1]
                        s_1 = n_1[f, x, y, z, 0]
                        c_1 = n_1[f, x, y, z, 1]
                        m_0 = abs(F - f) / float(F)
                        m_1 = 1.0 - m_0
                        if self.setShape and s_0 is not None and s_1 is not None:
                            AnimSequence[f, x, y, z, 0] = s_0 * m_0 + s_1 * m_1
                        else:
                            try:
                                AnimSequence[f, x, y, z, 0] = self.AnimSequence[f, x, y, z, 0]
                            except:
                                pass
                        if self.setColor and c_0 is not None and c_1 is not None:
                            AnimSequence[f, x, y, z, 1] = array(c_0) * m_0 + array(c_1) * m_1
                        else:
                            try:
                                AnimSequence[f, x, y, z, 1] = self.AnimSequence[f, x, y, z, 1]
                            except:
                                pass

        self.Animation[episode] = AnimSequence
        self.Animation_pick[episode] = path_0 + str(os.stat(path_0).st_mtime)
        self.write_AnimSequence_file([self.current_Object,])
        self.CVar1.set("crossfade " + str(fileNames) + " successful!")
        self.EntryVar3.set(self.Time)


    def load_frame_levels(self, objects):
        outPutFormat = self.output_format
        formatstring = "%0" + str(len(outPutFormat)) + "d"

        frame = 0
        path = os.path.join(folders, sceneDir, object_dir)
        for i in objects:
            dimensions = i.get_dimensions()
            for dim in dimensions:
                v = i.setup_array(dim)
                name = i.Name + "_" + str(dim) + "_"
                filename = name + str(formatstring) % frame + ".txt"
                try:
                    f = open(os.path.join(path, filename), "r")
                    n = eval(f.read())
                    f.close()
                    print(filename + " loaded!")
                except:
                    print(filename + " not opened!")
                    continue
                (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = i.give_active_bounds()
                try:
                    N = array(n, dtype = list).reshape(Xdim, Ydim, Zdim, 2)
                except(Exception) as detail:
                    print("frame not in shape!", detail)
                    try:
                        N = array(n, dtype = list).reshape(dim, dim, dim, 2)
                    except(Exception) as detail:
                        print("frame not loaded!", detail)
                        continue
                i.load_frame(N, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)

    def load_frame(self, objects, frame = None, object_name = False):
        if frame == None:
            frame = self.Time
        if object_name:
            path = os.path.join(folders, sceneDir, object_dir)
        else:
            name = "frame"
            path = folders
        outPutFormat = self.output_format
        formatstring = "%0" + str(len(outPutFormat)) + "d"
        Names = []
        for i in objects:
            dim = i.get_dimension()
            v = i.setup_array(dim)
            if i == self.current_Object:
                self.currentVoxel = v
            if object_name:
                name = i.Name + "_"
            filename = name + str(formatstring) % frame + ".txt"
            try:
                f = open(os.path.join(path, filename), "r")
                n = eval(f.read())
                f.close()
                print(filename + " loaded!")
            except:
                print(filename + " not opened!")
                continue
            (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = i.give_active_bounds()
            try:
                N = array(n, dtype = list).reshape(Xdim, Ydim, Zdim, 2)
            except(Exception) as detail:
                print("frame not in shape!", detail)
                try:
                    N = array(n, dtype = list).reshape(dim, dim, dim, 2)
                except(Exception) as detail:
                    print("frame not loaded!", detail)
                    continue
            Names.append(filename)
            i.load_frame(N, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
        self.CVar1.set("loading " + str(Names) + " successful!")
        self.update_frame(self.objectList)

    def interpolate_Frame(self, frame):
        return 0.1

    def AnimSequence_fill_frames(self, frames, objects = None):
        path = os.path.join(folders, sceneDir, keyframeDir)
        dirs = os.listdir(path)
        outPutFormat = self.output_format
        l = len(outPutFormat)
        dirs.sort()
        if self.time_list and dirs:
            Frames = []
            keyframes = []
            for i in dirs:
                try:
                    index = int(i[-l-4:-4])
                except:
                    continue
                if index in self.time_list:
                    keyframes.append(i)
                    Frames.append(index)
        else:
            return
        global Xdim, Ydim, Zdim

        (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()

        arrayL = Xdim * Ydim * Zdim

        Frame_array = [0] * (frames + 2)

        Frame_id = [0] * (frames + 2)

        Raw_array = []

        Id_array = []

        if keyframes:
            for x, i in zip(Frames, keyframes):
                try:
                    f = open(os.path.join(path, i), "r")
                    n = eval(f.read())
                    f.close()
                    print("loading frame " + i + " successful!")
                except:
                    print("loading frame " + i + " failed")
                    continue
                if len(n) == arrayL:
                    Frame_array[x] = n
                    Frame_id[x] = id(Frame_array[x])
                    Raw_array.append(Frame_array[x])
                    Id_array.append(id(Frame_array[x]))
                else:
                    print("this frame was not fit for current resolution!")
        else:
            return

        print("Id_array", Id_array)

        if not Raw_array:
            print("keyframes did not fit")
            return

        i = Frame_id.index(Id_array[0])
        prev = array(Frame_array[i], dtype = list).reshape(Xdim, Ydim, Zdim, 2)
        index = Id_array.index(Frame_id[i]) + 1
        if index == len(Raw_array):
            index = 0
        R = Raw_array[index]
        I = Frame_id.index(id(R))
        steps = I - i
        if steps < 0:
            steps = frames + i
        frame = array(R, dtype = list).reshape(Xdim, Ydim, Zdim, 2)

        if i > 0:
            p = prev
            prev = frame
            frame = p
            steps = i
            print("reversed", steps)
            print("starting with frames prev : %d, next %d"% (I, i))
        else:
            print("starting with frames prev : %d, next %d"% (i, I))

        if objects == None:
            objects = self.objectList
        self.setup_numpy(objects, force = True)
        episode = self.ObjectList.index(self.current_Object)
        Animation = self.Animation[episode]
        AnimSequence = ones((frames, Xdim, Ydim, Zdim, 2), dtype = object)
        level = self.current_Object[self.currentVoxel].level
        c = 0
        self.setup_progress(frames)
        for i in range(frames):
            self.progressbar.advance("\ngenerating Keyframe Animation\n")
            if type(Frame_array[i]) == type([]):
                c = 0
                prev = array(Frame_array[i], dtype = list).reshape(Xdim, Ydim, Zdim, 2)
                index = Id_array.index(Frame_id[i]) + 1
                print("index 1", index)
                if index == len(Raw_array):
                    index = 0 #index - 1 #0
                print("index 2", index)
                R = Raw_array[index]
                I = Frame_id.index(id(R))
                """
                when no more keyframes in timeline
                steps has negative value, but we need wrap this value over the remaining frames
                and add together
                """
                steps = I - i
                if steps < 0:
                    steps = frames - i
                frame = array(R, dtype = list).reshape(Xdim, Ydim, Zdim, 2)
                if Frame_array[i] is R:
                    print("we got one keyframe", steps, i)
                else:
                    print("we got more than one keyframe", steps, i)
            a = zeros((Xdim, Ydim, Zdim, 2), dtype = list)
            for x in range(Xdim):
                for y in range(Ydim):
                    for z in range(Zdim):
                        if steps > 0:
                            if self.setShape and prev[x, y, z][0] is not None and frame[x, y, z][0] is not None:
                                v = prev[x, y, z][0] + (frame[x, y, z][0] - prev[x, y, z][0]) * (float(c) / float(steps))
                            else:
                                try:
                                    v = Animation[i][x, y, z][0]
                                except:
                                    v = None
                            if self.setColor and prev[x, y, z][1] is not None and frame[x, y, z][1] is not None:
                                C = list(map(int, (array(prev[x, y, z][1]) + (array(frame[x, y, z][1]) - array(prev[x, y, z][1])) * (float(c) / float(steps)))))
                            else:
                                try:
                                    C = Animation[i][x, y, z][1]
                                except:
                                    C = None
                        else:
                            if self.setShape:
                                v = frame[x, y, z][0]
                            else:
                                try:
                                    v = Animation[i][x, y, z][0]
                                except:
                                    v = None
                            if self.setColor:
                                C = frame[x, y, z][1]
                            else:
                                try:
                                    C = Animation[i][x, y, z][1]
                                except:
                                    C = None
                        a[x, y, z] = (v, C)
                        """
                        prev cancels out when subtraction is multiplyed with one
                        through the steps c nears to steps and division equals to one finally
                        """
            AnimSequence[i] = a
            c += 1
        self.quit_progress()
        self.AnimSequence = AnimSequence
        i = self.ObjectList.index(self.current_Object)
        self.Animation[i] = AnimSequence

        self.CVar4.set("frames:" + str(frames) + ",dimension:" + str(self.dim))
        print("Animation filled!")

        self.write_AnimSequence_file([self.current_Object,])

    def load_key_frames_into_AnimSequence(self):
        if not self.playing_animation:
            f = self.animLength - 1
            self.AnimSequence_fill_frames(f)
            self.frame = self.Time
        self.toggle_animation()

    def write_key_frames(self):
        print("write_key_frames")
        if self.time_list:
            path = os.path.join(folders, sceneDir, keyframeDir)
            name = "key_frames.txt"
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except:
                    print("cannot create directory")
                    return
            try:
                f = open(os.path.join(path, name), "w")
                f.write(str(self.time_list))
                f.close()
                print("key_frames written")
                self.CVar1.set("key_frames written into " + path + " directory!")
                return True
            except:
                print("key_frames.txt not written!")
                self.CVar1.set("key_frames.txt not written!")
                return False

    def load_key_frames(self):
        path = os.path.join(folders, sceneDir, keyframeDir)
        name = "key_frames.txt"
        try:
            f = open(os.path.join(path, name), "r")
            n = list(eval(f.read()))
            f.close()
            print("key_frames loaded!")
            self.CVar1.set("key_frames loaded")
        except(Exception) as detail:
            print("key_frames.txt not loaded!", detail)
            self.CVar1.set("key_frames.txt not loaded!")
            return

        if len(n) > 0:
            self.place_keyframes(n)

    def delete_key_frames(self):
        for i in self.keyframes:
            i.place_forget()
        self.keyframes = []
        self.time_list = []
        self.time_keyed = {}

    def place_keyframes(self, N):
        for i in N:
            self.Time = i
            self.write_key_frame(True)
        self.Time_factor.set(self.Time)

    def from_keyframe(self, frame, paste = False):
        name = "frame"
        path = os.path.join(folders, sceneDir, keyframeDir)
        outPutFormat = self.output_format
        formatstring = "%0" + str(len(outPutFormat)) + "d"
        Name = name + str(formatstring) % frame + ".txt"
        try:
            f = open(os.path.join(path, Name), "r")
            n = eval(f.read())
            f.close()
            print("file open successful")
        except:
            print("file not opened!")
            return None
        if n[0][0] == None:
            shape = False
        elif type(n[0][0]) == type(0.1):
            print("its float")
            shape = True
        else:
            shape = False
        if n[0][1] == None:
            color = False
        elif type(n[0][1]) == tuple:
            print("its tuple")
            color = True
        else:
            color = False
        if color and shape:
            image = self.colorsandshape
        elif color:
            image = self.colorimage
        elif shape:
            image = self.shapeimage
        else:
            image = self.emptyshape

        if paste:
            s = self.AnimSequence.shape
            try:
                N = array(n, dtype = list).reshape(s[1], s[2], s[3], s[4])
                print("shape is good")
                return image, N
            except:
                print("shape is not good")
                return (image, None)
        else:
            return image

    def paste_keyframe(self, Time):
        print("paste_keyframe", Time)
        try:
            (image, data) = self.pasteframe
        except(Exception) as detail:
            print("nothing keyframe copied", detail)
            return
        if data is not None:
            (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
            self.current_Object.load_frame(data, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
            self.write_key_frame(image = image)
            self.update_frame(self.objectList)

    def copy_keyframe(self, Time):
        print("copy_keyframe", Time)
        if Time in self.time_list:
            keyframe = self.time_keyed[Time]
            print(keyframe)
            print("keyframe exists")
            self.pasteframe = self.from_keyframe(Time, True)

    def delete_KeyFrame(self):
        if self.Time in self.time_keyed:
            keyframe = self.time_keyed[self.Time]
            keyframe.place_forget()
            if keyframe in self.keyframes:
                self.time_list.pop(self.keyframes.index(keyframe))
                self.keyframes.pop(self.keyframes.index(keyframe))

    def write_key_frame(self, place_keyframes = False, image = None):
        if place_keyframes:
            success = True
            image = self.from_keyframe(self.Time)
        else:
            if not self.writeKeyFrame:
                return
            success = self.write_frame([self.current_Object,], key_frame = True)

        if self.Time > self.animLength:
            self.Time = self.animLength - 1

        if success and self.Time not in self.time_list:

            def popup(event, t, color, shape):
                self.stop_animation()
                self.Time = t
                self.Time_factor.set(self.Time)
                self.setColor = color
                self.setShape = shape
                self.set_Color.set(self.setColor)
                self.set_Shape.set(self.setShape)
                self.shape_menu.post(event.x_root, event.y_root)

            def delete_key_tick(t):
                if self.setColor and self.setShape:
                    keyframe.place_forget()
                    if keyframe in self.keyframes:
                        self.time_list.pop(self.keyframes.index(keyframe))
                        self.keyframes.pop(self.keyframes.index(keyframe))
                else:
                    self.Time = t
                    self.Time_factor.set(self.Time)
                    self.write_key_frame()

            if not image:
                if self.setColor and self.setShape:
                    image = self.colorsandshape
                elif self.setColor:
                    image = self.colorimage
                elif self.setShape:
                    image = self.shapeimage
                else:
                    image = self.emptyshape

            keyframe = tk.Button(master = self.f4, text = "", width = 0,
                                 command = lambda t = self.Time: delete_key_tick(t), image = image,
                                 bg = widget_bg, highlightbackground = widget_hg, fg = widget_fg, activebackground = widget_ag)

            keyframe.bind('<Enter>',
                          lambda e, c = None,
                          m = "%d, click to delete" % self.Time: self.takefocus1(e, c, m))

            keyframe.bind('<Button-3>', lambda e, t = self.Time,
                          c = self.setColor, s = self.setShape: popup(e, t, c, s))

            frame = self.Time / float(timeticks)
            keyframe.place(relx = frame, rely = 0.5, anchor = tk.CENTER)
            self.keyframes.append(keyframe)
            self.time_list.append(self.Time)
            self.time_keyed[self.Time] = keyframe
        elif success:
            if not image:
                if self.setColor and self.setShape:
                    image = self.colorsandshape
                elif self.setColor:
                    image = self.colorimage
                elif self.setShape:
                    image = self.shapeimage
                else:
                    image = self.emptyshape
            keyframe = self.time_keyed[self.Time]
            keyframe.configure(image = image)
        self.current_Object.setup_array(self.dim, force = True)

    def write_frame_levels(self, objects):
        outPutFormat = self.output_format
        formatstring = "%0" + str(len(outPutFormat)) + "d"

        frame = 0
        path = os.path.join(folders, sceneDir, object_dir)

        for i in objects:
            dimensions = i.get_dimensions()
            for dim in dimensions:
                v = i.setup_array(dim)
                v0 = i.write_frame(self.setShape, self.setColor)
                name = i.Name + "_" + str(dim) + "_"
                filename = name + str(formatstring) % frame + ".txt"
                try:
                    f = open(os.path.join(path, filename) , "w")
                    f.write(str(v0))
                    f.close()
                except:
                    print("file not written!")

    def write_frame(self, objects, key_frame = False, object_name = False):
        print('WRITE FRAME')
        outPutFormat = self.output_format
        formatstring = "%0" + str(len(outPutFormat)) + "d"
        if key_frame:
            frame = self.Time
            path = os.path.join(folders, sceneDir, keyframeDir)
            name = "frame"
        elif object_name:
            frame = 0
            path = os.path.join(folders, sceneDir, object_dir)
        else:
            frame = 0
            path = "Folders/"
            name = "frame"
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
                return
        for i in objects:
            dim = i.get_dimension()
            arranged = i.validate_animated_Cube()
            if arranged:
                v = i.setup_array(dim, force = True)
            else:
                v = i.setup_array(dim)
            if i == self.current_Object:
                self.currentVoxel = v
            v0 = i.write_frame(self.setShape, self.setColor)
            if object_name:
                name = i.Name + "_"
            filename = name + str(formatstring) % frame + ".txt"
            try:
                f = open(os.path.join(path, filename) , "w")
                f.write(str(v0))
                f.close()
                self.CVar1.set("list written into " + path + " directory!")
                if key_frame:
                    return True
            except:
                print("file not written!")
                self.CVar1.set("file not written!")
                return False

    def set_shape(self, shape = None, radius = None, gradient = None, objects = []):
        self.get_dimension()
        A1 = self.current_Object.animated_Cube()
        (X1, Y1, Z1) = A1.shape
        global Xdim, Ydim, Zdim
        (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.current_Object.give_active_bounds()
        a = ones((Xdim, Ydim, Zdim, 2), dtype = object)
        (X, Y, Z, T) = a.shape
        l = X * Y * Z
        level = self.level.get()
        size = level * 2.0
        c = float(self.dim) / 2.0
        a1 = self.AlphaEntryVar1.get()
        a2 = self.AlphaEntryVar2.get()
        (M2, N2) = self.func_0_1(255, a2)
        (M1, N1) = self.func_0_1(255, a1)
        if self.fitPlace:
            step_x = level * (X1 / float(Xdim)) * 2.0
            step_y = level * (Y1 / float(Ydim)) * 2.0
            step_z = level * (Z1 / float(Zdim)) * 2.0
        else:
            step_x = size
            step_y = size
            step_z = size

        x1 = (step_x / 2.0) - 1.0
        for x in range(X):
            y1 = (step_y / 2.0) - 1.0
            for y in range(Y):
                z1 = (step_z / 2.0) - 1.0
                for z in range(Z):
                    if shape == 1:
                        v = sqrt(x1**2 + y1**2 + z1**2) * level
                    elif shape == 2:
                        v = level / sqrt(x1**2 + y1**2 + z1**2)
                    elif radius:
                        if sqrt(x1**2 + y1**2 + z1**2) < radius:
                            v = size
                        else:
                            v = 0.0
                    elif gradient == 0:
                        v = (float(x * y * z) / l) * size + level
                    elif gradient == "x":
                        v = (float(x) / X) * level + level
                    elif gradient == "y":
                        v = (float(y) / Y) * level + level
                    elif gradient == "z":
                        v = (float(z) / Z) * level + level
                    (m, n) = self.func_0_1(size, v)
                    if self.setShape:
                        voxel = A1[x + Xbound[0], y + Ybound[0], z + Zbound[0]]
                        s2 = self.current_Object[voxel].size
                        S2 = s2 * M2
                        S1 = size * N1
                        a[x, y, z][0] = S2 * m + S1 * n
                    else:
                        a[x, y, z][0] = v

                    if self.setColor:
                        voxel = A1[x + Xbound[0], y + Ybound[0], z + Zbound[0]]
                        color = self.current_Object[voxel].color
                        fgcolor =       (self.fgcolor[0] * M2 + color[0] * N2,
                                         self.fgcolor[1] * M2 + color[1] * N2,
                                         self.fgcolor[2] * M2 + color[2] * N2)
                        bgcolor =       (self.bgcolor[0] * M1 + color[0] * N1,
                                         self.bgcolor[1] * M1 + color[1] * N1,
                                         self.bgcolor[2] * M1 + color[2] * N1)
                        a[x, y, z][1] = (fgcolor[0] * m + bgcolor[0] * n,
                                         fgcolor[1] * m + bgcolor[1] * n,
                                         fgcolor[2] * m + bgcolor[2] * n)
                    else:
                        a[x, y, z][1] = None
                    z1 += step_z
                y1 += step_y
            x1 += step_x

        self.current_Object.load_frame(a, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
        self.write_key_frame()
        self.update_frame(objects)

    def truncate_voxels(self):
        for i in self.objectList:
            i.delete_voxels_below()
            print(i.Name + " voxels truncated")
        gc.collect()

    def truncate_voxels_and_arrays(self):
        for i in self.objectList:
            i.delete_voxels_below()
            i.delete_invisible_arrays()
            print(i.Name + " voxels and arrays truncated")
        gc.collect()

    def truncate_repros(self, update = True):
        filename = os.path.join(folders, obj_files, "Cube.obj")
        faces = obj_loader.load(filename)
        print("polys", len(faces))
        if self.SDL_bind:
            for key, OBJ_repro in self.Screen.objFileNames.items():
                OBJ_repro.cleanup()
                OBJ_repro.__init__(faces)
                if self.Screen.VBO:
                    OBJ_repro.set_up_vertex_array()
                else:
                    OBJ_repro.set_up_display_list()
        gc.collect()
        if update:
            self.update_frame(self.objectList)

    def truncate_textures(self, update = True):
        if self.SDL_bind:
            self.Screen.delete_display_list()
            self.Screen.texNamesList = {}
        gc.collect()
        if update:
            self.update_frame(self.objectList)

    def init_OBJ_repro(self, update = True):
        filename = os.path.join(folders, obj_files, "Cube.obj")
        self.repro = filename
        if filename in self.Screen.objFileNames and self.useLoaded:
            self.OBJ_repro = self.Screen.objFileNames[filename]
        else:
            faces = obj_loader.load(filename)
            print("polys", len(faces))
            self.OBJ_repro = obj_loader.obj_transform(faces)
            self.Screen.objFileNames[filename] = self.OBJ_repro
            self.Screen.obj_transforms.append(self.OBJ_repro)

        for i in self.ObjectList:
            i.set_repro(self.repro, self.OBJ_repro, None, None)
        if self.SDL_bind and self.OBJ_repro:
            if self.Screen.VBO:
                if not self.OBJ_repro.VBO:
                    self.OBJ_repro.set_up_vertex_array()
            elif not self.OBJ_repro.objdisplayList:
                self.OBJ_repro.set_up_display_list()
        self.write_objects_pic(PICC, True)
        if update:
            self.update_frame(self.objectList)

    def make_unique(self, objects):
        self.current_Object.make_unique()
        self.update_frame(objects)
        self.get_dimension()

    def arrange_Animated_Cube(self):
        self.currentVoxel = self.current_Object.setup_array(self.dim, True)
        self.EntryVar1.set(self.currentVoxel)

    def setup_numpy(self, objects, force = False):
        for i in objects:
            dim = i.get_dimension()
            v = i.setup_array(dim, force = force)
            if i == self.current_Object:
                self.currentVoxel = v
        self.get_dimension()

    def print_invisible_voxels(self):
        self.current_Object.print_invisible_voxels()

    def print_bounds(self, objects):
        for i in objects:
            (X, Y, Z, Xdim, Ydim, Zdim) = i.give_active_bounds()
            print("Xdim, Ydim, Zdim", Xdim, Ydim, Zdim)
            print("x min max", X[0], X[-1])
            print("y min max", Y[0], Y[-1])
            print("z min max", Z[0], Z[-1])

    def print_array(self):
        self.current_Object.print_array()

    def set_rotation_amount(self, amount):
        self.Rotation_Amount = amount
        if self.OBJ_bind:
            self.current_Object.cube3d().set_direction(amount)
        else:
            objects = []
            position = self.current_Object.conform_position() + self.current_Object.local_conform()
            for i in self.ObjectList:
                p = i.conform_position() + i.local_conform()
                if (p[0] == position[0] and
                    p[1] == position[1] and
                    p[2] == position[2]):
                    objects.append(i)
            for i in objects:
                i.set_direction(amount)

    def undo_view(self, objects, move_only = False, update = True):
        if self.Zoomed:
            self.Zoomed = False
            self.tunein_Ground()
            self.toggle_Shadows(True, False)
            self.undo_rest(self.isolate_rest)
        else:
            return
        for i in objects:
            if move_only:
                i.undo_zoom_screen(self.level.get())
                i.reset_pan()
            else:
                i.undo_zoom_screen(self.level.get(), self.Depth)
                i.reset_pan()
        if self.localCenter:
            for i in objects:
                i.restore_angle()
            self.angle = self.current_Object.angle()
            self.EntryVar4.set(ceil(rad2deg(self.angle)))
        if self.SDL_bind:
            if not self.VBOFrames:
                self.toggle_Frames()
        if update:
            if self.LockAngle:
                conform = self.current_Object.conform_position() + self.current_Object.local_conform()
                objectList = []
                for i in self.objectList:
                    Conform = i.conform_position() + i.local_conform()
                    if str(conform) == str(Conform):
                        objectList.append(i)
            else:
                objectList = self.objectList
            self.sync_voxels(objects = objectList)
            self.update_object_frame(objects)

    def reset_pan(self, objects):
        for i in objects:
            i.reset_pan()
        self.update_object_frame(objects)

    def switch_Zoomed(self):
        if self.Zoomed:
            self.undo_view(self.ObjectList)
        else:
            self.zoom_to_selected(self.ObjectList)

    def zoom_to_selected(self, objects, resetview = False, move_only = False, restore = False):
        if self.SDL_bind:
            if self.VBOFrames:
                self.toggle_Frames()
        if not self.Zoomed:
            self.Zoomed = True
            self.GroundList = []
            for i in self.ObjectList:
                ground = i.draw_Ground()
                self.GroundList.append(ground)
            self.toggle_Ground(False, False)
            self.toggle_Shadows(False, False)
            self.isolate_rest = self.objectList
            self.isolate_object(self.objectList, False)
        else:
            return
        if self.localCenter:
            for i in objects:
                i.store_angle()
            self.reset_rotation_all()
        if resetview:
            self.currentVoxel = self.current_Object.get_biggest_pixel()
            self.current_Object.get_highlight(self.currentVoxel)
        current = self.current_Object[self.currentVoxel]
        for i in objects:
            if move_only:
                i.move_to_the_screen(current)
            else:
                i.move_to_the_screen(current, self.Depth, restore = restore)
        self.update_object_frame(objects)

    def reset_rotation_all(self):
        self.angle = 0
        self.EntryVar4.set(0)
        for i in self.objectList:
            if self.OBJ_bind:
                i.cube3d().set_angle(self.angle)
            else:
                i.set_angle(self.angle)
        self.EntryVar4.set(0)

    def reset_position(self, objects, update = True):
        if self.syncPositions:
            objects = self.objectList
        if not self.OBJ_bind:
            for i in objects:
                i.reset_position()
        if update:
            self.update_object_frame(self.objectList)

    def add_positions(self, objects):
        if self.syncPositions:
            objects = self.objectList
        if self.localCenter:
            for i in objects:
                center = i.give_center(self.vector, self.c_baked)
                i.set_center(center)
                i.add_conform_positions()
            self.update_object_frame(self.objectList)

    def highlight_collection(self, objects):
        self.current_Object.highlight_collection()
        self.update_frame(objects)

    def invert_collected(self, objects):
        self.current_Object.invert_collected()
        self.update_frame([self.current_Object,])

    def select_child_voxels(self, objects, append):
        self.current_Object.select_child_voxels(append)
        self.select_closest(self.objectList)
        print("select child voxels")
        self.CVar1.set("child voxels selected!")

    def select_child_voxel(self, objects):
        try:
            N = self.current_Object[self.currentVoxel].voxels[0].currency
            r = self.current_Object[self.currentVoxel]
        except:
            return
        if N >= 0 and N < len(self.current_Object.voxels()):
            self.currentVoxel = N
            self.current_Object.get_highlight(self.currentVoxel)
            self.setup_numpy(objects)
            self.update_frame(objects)
            self.EntryVar1.set(self.currentVoxel)

    def select_super(self, objects):
        try:
            N = self.current_Object[self.currentVoxel].parent.currency
        except:
            return
        if N >= 0 and N < len(self.current_Object.voxels()):
            self.currentVoxel = N
            self.current_Object.get_highlight(self.currentVoxel)
            self.setup_numpy(objects)
            self.update_frame(objects)
            self.EntryVar1.set(self.currentVoxel)

    def clear_collected(self, objects):
        if self.current_Object.collected() == []:
            self.current_Object.remove_highlight()
        else:
            self.current_Object.clear_collected()
        self.update_frame(objects)

    def select_closest(self, objects):
        self.currentVoxel = self.current_Object.select_closest()
        self.EntryVar1.set(self.currentVoxel)
        self.setup_numpy(objects)
        self.update_frame(objects)

    def update_time_factor(self):
        self.stop_animation()
        self.Time = self.Time_factor.get()
        self.currentFrame = self.Time
        self.EntryVar3.set(str(self.currentFrame))

    def update_scale_factor(self, objects):
        self.Scale = self.Scale_factor.get()
        if self.falloff:
            self.current_Object.affect_neighbours(self.Scale, self.currentVoxel)
        else:
            self.current_Object.update_voxels_scale(self.Scale, self.currentVoxel)
        self.update_frame(objects)

    def update_depth_factor(self, e):
        d = self.Depth_factor.get()
        if d == 0:
            self.Depth = 0
        else:
            self.Depth = 5 / d
        print(self.Depth)
        for i in self.objectList:
            i.set_depth(self.Depth)
        self.update_frame(self.objectList)

    def select_all(self, objects):
        self.current_Object.highlight_all()
        self.update_frame(objects)

    def refine_levels(self, to_the_level = False):
        T = time.time()
##        if self.OBJ_bind:
##            self.toggle_OBJ_Mode()
        dim = self.get_dimension()
        self.setup_numpy([self.current_Object,])
        if self.syncLevels and len(self.objectList) > 1:
            if SDL_bind:
                VBOFrames = False
                if self.VBOFrames:
                    VBOFrames = True
                    self.toggle_Frames()
            collection = self.current_Object.get_collection()
            level = self.current_Object.voxels()[self.currentVoxel].level
            conform = self.current_Object.conform_position()# + self.current_Object.local_conform()
            print("conform", conform)
            for i in self.objectList:
                c = None
                if i is not self.current_Object:
                    C = i.conform_position()# + i.local_conform()
                    print("C", C)
                    if (abs(C[0] - conform[0]) < 2.0 and
                        abs(C[1] - conform[1]) < 2.0 and
                        abs(C[2] - conform[2]) < 2.0):
                        c = i.set_collection(collection)
                    else:
                        continue
                else:
                    c = i.collected()
                    if c is None or not c:
                        c = [self.current_Object.voxels()[self.currentVoxel],]
                i.refine_highlighted_level(level, c, self.Zippedspawn)

            if SDL_bind:
                if VBOFrames:
                    self.toggle_Frames()
            self.currentVoxel = 0
        else:
            self.currentVoxel = self.current_Object.refine_highlighted(to_the_level, self.Zippedspawn)
        self.EntryVar1.set(self.currentVoxel)
        self.setup_numpy(self.objectList)
        self.sync_VoxelDim()
        self.update_object_frame(self.objectList)
        self.create_backup_frame()
        t = time.time()
        print("time elapsed ", t - T)

    def sync_VoxelDim(self):
        self.Voxel = self.current_Object.voxels()[self.currentVoxel].Currency
        self.Dim = self.dim
        self.voxel_string = "%d %d" % (self.Dim, self.Voxel + 1)
        success = self.update_Voxel_string()
        if success:
            self.EntryVar0.set(self.voxel_string)

    def update_coord_string(self, objects):
        v = self.currentVoxel
        self.currentVoxel = self.current_Object.select_through_xyz(self.coords, self.level.get())
        self.current_Object.get_highlight(self.currentVoxel)
        self.EntryVar1.set(self.currentVoxel)
        if v == self.currentVoxel:
            return False
        else:
            return True

    def update_object_frame(self, objects):
        if self.localCenter:
            center = None
            vector = None
            angle = "self"
        else:
            center = self.center
            vector = self.vector
            angle = self.angle
        for i in self.objectList:
            if self.localCenter:
                #i.rotate3d_vector(center = (0, 0, 0), vector = self.vector, angle = self.c_baked)
                i.bake_xyz_rotation()
            if self.rotation_way == 'axis':
                i.rotate3d_vector(center = center, vector = vector, angle = angle)
            elif self.rotation_way == 'x':
                i.rotate3d_x(center = center, x_angle = angle)
            elif self.rotation_way == 'y':
                i.rotate3d_y(center = center, y_angle = angle)
            elif self.rotation_way == 'z':
                i.rotate3d_z(center = center, z_angle = angle)
            if self.localCenter:
                i.restore_xyz_baked()
##                if self.localRefresh:
##                    self.localRefresh = False
##                    i.move_to_conform(i.conform_position())

        self.EntryVar1.set(self.currentVoxel)
        self.EntryVar4.set("%3.2f"%rad2deg(self.angle))
        #self.update_frame(self.objectList)

    def select_expand(self):
        print("select_expand")
        self.setup_numpy([self.current_Object,])
        self.current_Object.select_expand()
        self.update_frame(self.objectList)

    def select_same_highlight(self):
        dim = self.current_Object.get_dimension()
        level = 1.0 / float(dim)
        c = self.current_Object[self.currentVoxel].Currency
        objectList = []
        for i in self.objectList:
            if i is not self.current_Object:
                if i.select_Level(dim):
                    objectList.append(i)
        print([o.Name for o in objectList])
        for i in objectList:
            v = i.select_same_Currency(c, level)
            print(v)
            if v is not None:
                i.get_highlight(v)
        self.update_frame(self.objectList)

    def select_same_level(self):
        self.current_Object.selectSameLevel()
        self.update_frame(self.objectList)

    def highlight_slice(self, objects):
        o = []
        for i in self.objectList:
            if i is not self.current_Object:
                o.append(i)
        self.current_Object.clear_collected()
        for O in o:
            c = self.current_Object.return_slice_with(O, self.level.get())
            self.current_Object.append_collection(c)
        self.current_Object.validate_highlight()
        self.current_Object.highlight_collection()
        self.update_frame(objects)

    def raise_levels(self):
        self.currentVoxel = self.current_Object.raise_levels()
        self.setup_numpy(self.objectList)
        self.update_object_frame(self.objectList)
        #self.current_Object.highlight_all()
        self.create_backup_frame()

    def collapse_highlighted_voxels(self):
        if self.syncLevels and len(self.objectList) > 1:
            if SDL_bind:
                VBOFrames = False
                if self.VBOFrames:
                    VBOFrames = True
                    self.toggle_Frames()
            collection = self.current_Object.get_collection()
            conform = self.current_Object.conform_position()# + self.current_Object.local_conform()
            for i in self.objectList:
                c = None
                if i is not self.current_Object:
                    C = i.conform_position()# + i.local_conform()
                    if (abs(C[0] - conform[0]) < 2.0 and
                        abs(C[1] - conform[1]) < 2.0 and
                        abs(C[2] - conform[2]) < 2.0):
                        c = i.set_collection(collection)
                        i.remove_highlighted_level(c)
                    else:
                        continue
                else:
                    c = i.collected()
                    if c is None or not c:
                        c = [self.current_Object.voxels()[self.currentVoxel],]
                    self.currentVoxel = i.remove_highlighted_level(c)
            if SDL_bind:
                if VBOFrames:
                    self.toggle_Frames()
        else:
            self.currentVoxel = self.current_Object.remove_highlighted(self.currentVoxel)
        self.setup_numpy(self.objectList)
        self.sync_VoxelDim()
        self.update_object_frame(self.objectList)
        self.get_dimension()

    def highlight_voxels(self):
        self.current_Object.highlight_tree(self.currentVoxel)
        self.update_frame(self.objectList)

    def set_axis(self, way, update = True):
        self.stop_Rotation()
        if way == "axis":
            self.Axis.set(0)
            if self.previousVector is not None:
                self.EntryVar.set(self.previousVector)
                self.previousVector = None
        elif way == "x":
            if self.previousVector is None:
                self.previousVector = self.current_Object.local()
            self.Axis.set(1)
            self.EntryVar.set("1 0 0")
        elif way == "y":
            if self.previousVector is None:
                self.previousVector = self.current_Object.local()
            self.Axis.set(2)
            self.EntryVar.set("0 1 0")
        elif way == "z":
            if self.previousVector is None:
                self.previousVector = self.current_Object.local()
            self.Axis.set(3)
            self.EntryVar.set("0 0 1")
        self.rotation_way = way
        if update:
            self.update_object_frame(self.objectList)

    def enter_button(self, event, msg):
        self.CVar1.set(msg)

    def spawn_voxels(self):
        self.currentVoxel = self.current_Object[self.currentVoxel].spawn_sub_voxels(True)
        self.current_Object.validate_voxels()
        self.current_Object.get_highlight(self.currentVoxel)
        self.setup_numpy(self.objectList)
        if self.OBJ_bind:
            self.toggle_OBJ_Mode()
        self.update_object_frame(self.objectList)

    def collect_voxels(self):
        if self.syncLevels:
            if SDL_bind:
                VBOFrames = False
                if self.VBOFrames:
                    VBOFrames = True
                    self.toggle_Frames()
            current = self.current_Object.get_current()
            conform = self.current_Object.conform_position()# + self.current_Object.local_conform()
            for i in self.objectList:
                c = None
                if i is not self.current_Object:
                    C = i.conform_position()# + i.local_conform()
                    if (abs(C[0] - conform[0]) < 2.0 and
                        abs(C[1] - conform[1]) < 2.0 and
                        abs(C[2] - conform[2]) < 2.0):
                        c = i.put_current(current)
                    else:
                        continue
                    if c is not None:
                        i.clear_collected()
                        c.collect_voxels()
                else:
                    c = i.voxels()[self.currentVoxel]
                    if c is not None:
                        i.clear_collected()
                        self.currentVoxel = c.collect_voxels()
            if SDL_bind:
                if VBOFrames:
                    self.toggle_Frames()
        else:
            self.current_Object.clear_collected()
            self.currentVoxel = self.current_Object[self.currentVoxel].collect_voxels()
        self.current_Object.get_highlight(self.currentVoxel)
        self.setup_numpy(self.objectList)
        self.update_object_frame(self.objectList)

    def move_conform(self, vec, objects):
        if self.syncPositions:
            objects = self.objectList
        if not self.OBJ_bind:
            for i in objects:
                i.move_conform(vec)
            self.update_object_frame(self.objectList)

    def move_around(self, vec, objects):
        for i in objects:
            i.move_around(vec)
        self.update_frame(self.objectList)

    def delete_voxel(self):
        self.popvoxel = self.current_Object.delete_voxel([self.currentVoxel,])
        self.update_frame([self.current_Object,])

    def delete_voxels(self):
        self.currentVoxel = self.current_Object.delete_voxels()
        self.update_frame([self.current_Object,])

    def insert_voxels(self, n, v):
        if self.popvoxel != None:
            self.current_Object.insert_voxels(n, [self.popvoxel,])
            self.update_frame([self.current_Object,])
            self.popvoxel = None

    def scroll_UnravelSentence(self, event):
        print(platform, event.keycode)
        amount = 0
        if event.keycode == 111:
            amount = -1
        elif event.keycode == 116:
            amount = 1
        elif event.keycode == 38:
            amount = -1
        elif event.keycode == 40:
            amount = 1
        elif platform == 'cygwin' or platform == 'linux2':
            if event.num == 5:
                amount = 1
            elif event.num == 4:
                amount = -1
        elif platform != 'darwin':
            amount = -event.delta / 120
        else:
            amount = event.delta
            if amount < 0: amount = -1
            if amount > 0: amount = 1

        N = self.Unravelsentence_id
        N += amount

        if N >= len(self.Unravelsentences):
            N = 0
        if N < 0:
            N = len(self.Unravelsentences) - 1
        self.Unravelsentence_id = N
        self.Unravelsentence = self.Unravelsentences[int(N)]
        self.EntryVar_4.set(self.Unravelsentence)

    def scroll_VectorSentence(self, event):
        print(platform, event.keycode)
        amount = 0
        if event.keycode == 111:
            amount = -1
        elif event.keycode == 116:
            amount = 1
        elif event.keycode == 38:
            amount = -1
        elif event.keycode == 40:
            amount = 1
        elif platform == 'cygwin' or platform == 'linux2':
            if event.num == 5:
                amount = 1
            elif event.num == 4:
                amount = -1
        elif platform != 'darwin':
            amount = -event.delta / 120
        else:
            amount = event.delta
            if amount < 0: amount = -1
            if amount > 0: amount = 1

        N = self.Vectorsentence_id
        N += amount

        if N >= len(self.Vectorsentences):
            N = 0
        if N < 0:
            N = len(self.Vectorsentences) - 1
        self.Vectorsentence_id = N
        self.Vectorsentence = self.Vectorsentences[int(N)]
        self.EntryVar_3.set(self.Vectorsentence)

    def scroll_Sentence(self, event):
        print(platform, event.keycode)
        amount = 0
        if event.keycode == 111:
            amount = -1
        elif event.keycode == 116:
            amount = 1
        elif event.keycode == 38:
            amount = -1
        elif event.keycode == 40:
            amount = 1
        elif platform == 'cygwin' or platform == 'linux2':
            if event.num == 5:
                amount = 1
            elif event.num == 4:
                amount = -1
        elif platform != 'darwin':
            amount = -event.delta / 120
        else:
            amount = event.delta
            if amount < 0: amount = -1
            if amount > 0: amount = 1

        N = self.sentence_id
        N += amount

        if N >= len(self.sentences):
            N = 0
        if N < 0:
            N = len(self.sentences) - 1
        self.sentence_id = N
        self.sentence = self.sentences[int(N)]
        self.EntryVar2.set(self.sentence)

    def scroll_entry0(self, event):
        amount = 0
        if event.keycode == 111:
            amount = 1
        elif event.keycode == 116:
            amount = -1
        elif event.keycode == 38:
            amount = 1
        elif event.keycode == 40:
            amount = -1
        elif platform == 'cygwin' or platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta
            if amount < 0: amount = -1
            if amount > 0: amount = 1
        n = self.EntryVar0.get()
        N = n.split(" ")
        try:
            (self.Dim, self.Voxel) = (int(N[0]), int(N[1]) - 1)
        except:
            return
        i = self.Entry0.index(tk.INSERT)
        print(str(i))
        d = math.log(self.Dim, 2)
        if i >= 0 and i < len(N[0]) + 1:
            d += amount
        if i >= len(N[0]) + 1 and i < len(N[0]) + len(N[1]) + 2:
            self.Voxel += amount

        self.Voxel = abs(self.Voxel)

        self.Dim = 2**d

        Amount = self.Dim**3

        if self.Voxel >= Amount:
            self.Voxel = Amount - 1

        self.voxel_string = "%d %d" % (self.Dim, self.Voxel + 1)

        success = self.update_Voxel_string()
        if success:
            self.EntryVar0.set(self.voxel_string)
            self.update_frame(self.objectList)

    def update_Voxel_string(self):
        success = self.current_Object.select_by_VoxelDim(self.Dim, self.Voxel)
        return success

    def scroll_entry5(self, event):
        amount = 0
        if event.keycode == 111:
            amount = 1
        elif event.keycode == 116:
            amount = -1
        elif event.keycode == 38:
            amount = 1
        elif event.keycode == 40:
            amount = -1
        elif platform == 'cygwin' or platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta
            if amount < 0: amount = -1
            if amount > 0: amount = 1
        n = self.EntryVar5.get()
        N = n.split(" ")
        try:
            (x, y, z) = (float(N[0]), float(N[1]), float(N[2]))
        except:
            return
        level = self.level.get()
        i = self.Entry5.index(tk.INSERT)
        print(str(i))
        if i >= 0 and i < len(N[0]) + 1:
            x += level * amount * 2
        if i >= len(N[0]) + 1 and i < len(N[0]) + len(N[1]) + 2:
            y += level * amount * 2
        if i >= len(N[0]) + len(N[1]) + 2 and i < len(N[0]) + len(N[1]) + len(N[2]) + 3:
            z += level * amount * 2
        self.coords = (x, y, z)
        self.coord_string = "%1.7f %1.7f %1.7f" % self.coords
        success = self.update_coord_string([self.current_Object,])
        if success:
            self.EntryVar5.set(self.coord_string)

    def scroll_entry4(self, event):
        amount = 0
        if platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform == 'cygwin':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta
        n = self.EntryVar4.get()
        try:
            N = float(n)
            self.axis_rotation = False
        except:
            return
        N = deg2rad(N)
        N += amount * self.Rotation_Amount
        self.EntryVar4.set("%3.2f"%rad2deg(N))

    def scroll_time(self, event):
        amount = 0
        if platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform == 'cygwin':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta

        if amount > 0:
            amount = 1
        else:
            amount = -1
        if self.playing_animation:
            self.stop_animation()
        N = self.Time
        N = N + amount
        s = self.AnimSequence.shape
        if N > self.animLength:
            N = 0
        if N < 0:
            N = self.animLength - 1
        self.currentFrame = N
        self.Time = N
        self.frame = self.Time
        self.Time_factor.set(self.Time)

    def scroll_entry3(self, event):
        amount = 0
        if platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform == 'cygwin':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta

        if amount > 0:
            amount = 1
        else:
            amount = -1
        if self.playing_animation:
            self.stop_animation()
            n = self.frame
        else:
            n = self.EntryVar3.get()
        try:
            N = int(n)
        except:
            return
        N = N + amount
        s = self.AnimSequence.shape
        if N > self.animLength:
            N = 0
        if N < 0:
            N = self.animLength - 1
        self.EntryVar3.set(N)
        self.currentFrame = N
        self.Time = N
        #self.Time_factor.set(self.Time)

    def scroll_entry(self, event):
        amount = 0
        if platform == 'cygwin' or platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta
        n = self.EntryVar1.get()
        try:
            N = int(n)
        except:
            return
        N = N + amount
        if N >= 0 and N < len(self.current_Object.voxels()):
            self.EntryVar1.set(N)

    def scroll_depth(self, event):
        amount = 0
        if platform == 'cygwin' or platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta
        if amount < 0:
            amount = -1
        elif amount > 0:
            amount = 1
        amount = float(amount) / float(10.0)
        d = self.Depth_factor.get()
        d -= amount
        self.Depth_factor.set(d)
        self.update_depth_factor(event)

    def scroll_scale(self, event, objects):
        amount = 0
        if platform == 'cygwin' or platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta
        if amount < 0:
            amount = -1
        elif amount > 0:
            amount = 1
        amount = float(amount) / float(10.0)
        self.Scale += amount
        self.Scale_factor.set(self.Scale)
        self.update_scale_factor(objects)

    def scroll_embed(self, event, objects):
        amount = 0
        if platform == 'linux2':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform == 'cygwin':
            if event.num == 5:
                amount = -1
            elif event.num == 4:
                amount = 1
        elif platform != 'darwin':
            amount = event.delta / 120
        else:
            amount = event.delta
        if amount < 0:
            amount = -1
        elif amount > 0:
            amount = 1
        if self.syncPositions:
            objects = self.objectList
        if not self.OBJ_bind:
            for i in objects:
                i.move_conform((0, 0, float(amount) * self.level.get() * 2.0))
        self.update_object_frame(self.objectList)

    def takefocus1(self, event, c, msg):
        if c != None:
            c.focus_set()
        self.CVar1.set(msg)

    def takefocus3(self, event, c, msg):
        c.focus_set()
        success = self.current_Object.select_by_VoxelDim(self.Dim, self.Voxel)
        if success:
            self.currentVoxel = self.current_Object.highlighted()
            self.CVar1.set(msg)
            self.update_frame(self.objectList)

    def takefocus2(self, event, c, msg):
        c.focus_set()
        self.CVar1.set(msg)
        self.currentVoxel = self.EntryVar1.get()
        self.EntryVar1.set(str(self.currentVoxel))

    def shorten_entry_4(self, e, m, c):
        n = self.EntryVar4.get()
        try:
            N = float(n)
        except:
            return
        self.angle = deg2rad(N)
        if self.OBJ_bind:
            self.current_Object.cube3d().set_angle(self.angle)
        elif self.LockAngle:
            self.current_Object.set_angle(self.angle)
            conform = self.current_Object.conform_position() + self.current_Object.local_conform()
            for i in self.objectList[1:]:
                Conform = i.conform_position() + i.local_conform()
                if str(conform) == str(Conform):
                    i.set_angle(self.angle)
        else:
            self.current_Object.set_angle(self.angle)
        self.update_object_frame(self.objectList)

    def shorten_Unravelsentence(self, e, m, c):
        global Xdim, Ydim, Zdim
        n = self.EntryVar_4.get()
        print(n)
        s_ = 0
        r = 0
        L = Xdim * Ydim * Zdim
        x, y, z = 0, 0, 0
        i, f, c = 0.0, 0.0, 0.0
        s = self.AnimSequence.shape
        level = self.current_Object[self.currentVoxel].level
        c = level * 2
        f = 0.0
        step = pi * 2 / float(s[0])
        try:
            eval(n)
            self.Unravelsentence = n
        except(Exception) as detail:
            print(detail)
            return

    def shorten_Vectorsentence(self, e, m, c):
        global Xdim, Ydim, Zdim
        n = self.EntryVar_3.get()
        print(n)
        x, y, z = 0, 0, 0
        i, f, c = 0.0, 0.0, 0.0
        s = self.AnimSequence.shape
        level = self.current_Object[self.currentVoxel].level
        c = level * 2
        f = 0.0
        step = pi * 2 / float(s[0])
        try:
            eval(n)
            self.Vectorsentence = n
        except(Exception) as detail:
            print(detail)
            return

    def shorten_sentence(self, e, m, c):
        global Xdim, Ydim, Zdim
        n = self.EntryVar2.get()
        print(n)
        x, y, z = 0, 0, 0
        i, f, c = 0.0, 0.0, 0.0
        s = self.AnimSequence.shape
        level = self.current_Object[self.currentVoxel].level
        c = level * 2
        f = 0.0
        step = pi * 2 / float(s[0])
        try:
            eval(n)
            self.sentence = n
        except(Exception) as detail:
            print(detail)
            return

    def shorten_entry_3(self, e, m, c):
        n = self.EntryVar3.get()
        try:
            N = int(n)
        except:
            return
        self.currentFrame = N
        self.Time = N
        #self.Time_factor.set(self.Time)
        self.goto_animation_frame(self.objectList, N)

    def goto_animation_entry(self):
        s = self.AnimSequence.shape
        if self.Time < s[0]:
            self.EntryVar3.set(self.Time)

    def update_entry_0(self, e, m, c):
        n = self.EntryVar0.get()
        N = n.split(" ")
        try:
            (self.Dim, self.Voxel) = (int(N[0]), int(N[1]) - 1)
            self.voxel_string = "%d %d" % (self.Dim, self.Voxel + 1)
            success = self.update_Voxel_string()
            if success:
                self.EntryVar0.set(self.voxel_string)
            self.update_frame(self.objectList)
        except:
            return

    def shorten_entry_0(self, e, m, c):
        n = self.EntryVar0.get()
        N = n.split(" ")
        try:
            (self.Dim, self.Voxel) = (int(N[0]), int(N[1]) - 1)
        except:
            return

    def shorten_entry_5(self, e, m, c):
        n = self.EntryVar5.get()
        N = n.split(" ")
        try:
            self.coords = (float(N[0]), float(N[1]), float(N[2]))
        except:
            return

    def shorten_entry_1(self, e, m, c):
        n = self.EntryVar1.get()
        try:
            N = int(n)
        except:
            return
        if N >= 0 and N < len(self.current_Object.voxels()):
            self.currentVoxel = N
            self.current_Object.get_highlight(N)
            self.coords = self.current_Object[self.currentVoxel].get_position()
            self.coord_string = "%1.7f %1.7f %1.7f" % self.coords
            self.EntryVar5.set(self.coord_string)
            self.update_frame(self.objectList)

    def shorten_entry(self, e, m, c):
        n = self.EntryVar.get()
        N = n.split(" ")
        try:
            vector = (float(N[0]), float(N[1]), float(N[2]))
            if self.OBJ_bind:
                self.current_Object.cube3d().set_vector(vector)
            elif self.LockAngle:
                self.current_Object.set_vector(vector)
                conform = self.current_Object.conform_position() + self.current_Object.local_conform()
                for i in self.objectList[1:]:
                    Conform = i.conform_position() + i.local_conform()
                    if str(conform) == str(Conform):
                        i.set_vector(vector)
            else:
                self.current_Object.set_vector(vector)
            if not self.localCenter:
                self.vector = vector
        except:
            pass

    def goto_frame(self):
        self.stop_animation()
        width = self.f4.winfo_width() - 2 * 19
        mouse_x = self.f4.winfo_pointerx()
        left = self.f4.winfo_rootx()
        pointer = mouse_x - left - 5
        print(pointer, mouse_x, width)
        frame = int(float(pointer) / float(width) * self.animLength) - 1
        if frame < 0:
            frame = 0
        elif frame > self.animLength:
            frame = self.animLength
        print(frame)
        self.Time = frame
        self.Time_factor.set(self.Time)
        self.EntryVar3.set(frame)
        self.shorten_entry_3(0, 0, 0)

    def mouse_move_set(self, e, n):
        if n == 1:
            color = self.color1
        else:
            color = self.color2
        rgb = color['background']
        rgb = rgb[1:]
        (r, g, b) = hextorgb(rgb)
        self.movecolor = (r, g, b)

    def mouse_move_color(self, e, n):
        if n == 1:
            color = self.color1
            color_font = self.color_font1
            c = 'color'
        else:
            color = self.color2
            color_font = self.color_font2
            c = 'color1'
        (r, g, b) = self.movecolor
        R = r + e.x - 35
        G = g + e.x - 35
        B = b + e.x - 35
        if R > 255: R = 255
        if G > 255: G = 255
        if B > 255: B = 255
        if R < 0: R = 0
        if G < 0: G = 0
        if B < 0: B = 0
        currentcolor = (R, G, B)
        bg = "#%02x%02x%02x" % currentcolor
        color['background'] = bg
        color_font(bg, c)

    def mouse_move(self, e):
        e.x -= offset_2w
        e.y -= offset_2h
        self.mouse_x = e.x
        self.mouse_y = e.y
##        if self.SDL_bind:
##            self.embed.focus_set()
        l = self.Screen.pixelmap_picking.get_array()
        global backup_linecolor
        try:
            m = l[e.x, e.y]
            if m in self.ObjectIndexList:
                for i in self.objectList:
                    if i.index() == m:
                        backup_linecolor = i
                        i.cube().highlight_line()
                self.update_frame(self.objectList)
            elif backup_linecolor:
                for i in self.objectList:
                    i.cube().normal_line()
                backup_linecolor = None
                self.update_frame(self.objectList)
        except:
            return

    def mouseup(self, e):
        e.x -= offset_2w
        e.y -= offset_2h
        l = self.Screen.pixelmap_picking.get_array()
        m = l[e.x, e.y] - 1
        print(e.x, e.y, m)

    def mousedown(self, e):
        e.x -= offset_2w
        e.y -= offset_2h
        l = self.Screen.pixelmap_picking.get_array()
        m = l[e.x, e.y] - 1

        if m > -1:
            self.currentVoxel = m
            self.current_Object.get_highlight(m)
            self.update_frame(self.objectList)

        s = self.Screen.pixelmap_picking.get_array().shape
        l = self.Screen.pixelmap_picking.get_array()
        p = dtype(uint8)

        img1 = Image.fromarray(l)
        self.Screen.surface.fill(img1)
        self.blit_to_screen()


        """
        R = ""
        for x in range(s[0])[::20]:
            C = ""
            for y in range(s[1])[::20]:
                p = l[y, x] - 1
                C += str(p) + " "
            R += C + "\n"

        with open("Folders/bitmask.txt", "w") as f:
            f.write(R)
            f.close()
            print("file written")
            self.CVar1.set("bitmask written into Folders directory!")
        """
        print(e.x, e.y, m)

    def stop_Rotation(self):
        if self.axis_rotation == True:
            #self.EntryVar4.set("%3.2f"%rad2deg(self.angle))
            self.axis_rotation = False
            if self.idle_id != None:
                self.root.after_cancel(self.idle_id)
                self.idle_done = True
                self.idle_id = None

    def toggle_Rotation(self):
        t = time.time()
        print(t - self.time)
        self.time = t
        if self.axis_rotation == True:
            if self.localCenter:
                if self.OBJ_bind:
                    c = self.current_Object.cube3d().angle
                else:
                    c = self.current_Object.angle()
            else:
                c = self.angle
            self.EntryVar4.set("%3.2f"%rad2deg(c))
            self.axis_rotation = False
            if self.idle_id != None:
                self.root.after_cancel(self.idle_id)
                self.idle_done = True
                self.idle_id = None
            if self.DragAndDropView != None and self.DragAndDropView.winfo_exists():
                img = self.refresh_image()
                self.DragAndDropView.refresh_image(img)
        else:
            self.axis_rotation = True
            self.update_objects()
            self.idle()

    def update_frame(self, objects):
        level = self.current_Object[self.currentVoxel].level
        self.level.set(level)
        N = self.current_Object.name()
        p = self.current_Object.position()
        c = self.current_Object.conform_position()
        C = len(self.current_Object.collected())
        self.CVar2.set('name:' + N + ' C:' + str(C) + ' pos:' + str(p) + 'cpos:' + str(c))
        if not self.axis_rotation:
            if self.SDL_bind:
                if self.update_wm:
                    self.update_wm = None
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            else:
                if platform == 'darwin':
                    if self.DragAndDropView != None and self.DragAndDropView.winfo_exists():
                        self.Screen.surface.fill(self.clear_color)
                    else:
                        self.Screen.surface.blit(self.Screen.backgroundImage, (0, 0))
                else:
                    self.Screen.surface.fill(self.clear_color)
                self.Screen.pixelmap_picking.init_pic()
            z_sorted = self.z_sort_objects(objects)
            if self.Background:
                self.Screen.draw_background()
            if self.Shadows:
                for i in z_sorted:
                    i.render_shadows()
            for i in z_sorted:
                i.render(self.groundAll, self.vectorAnim)
            self.current_Object.draw_selection_rect()
            self.blit_to_screen()

    def idle(self):
        if self.axis_rotation == True:
            if not self.everyframe:
                self.angle += self.Rotation_Amount
            self.idle_id = self.root.after(delay_ms, self.idle)
            if not self.idle_done:
                #print("visited")
                return
            #print("scored")
            if self.everyframe:
                self.angle += self.Rotation_Amount

            self.idle_done = False
            if self.SDL_bind:
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            else:
                if platform == 'darwin':
                    if self.DragAndDropView != None and self.DragAndDropView.winfo_exists():
                        self.Screen.surface.fill(self.clear_color)
                    else:
                        self.Screen.surface.blit(self.Screen.backgroundImage, (0, 0))
                else:
                    self.Screen.surface.fill(self.clear_color)
                self.Screen.pixelmap_picking.init_pic()

            z_sorted = self.z_sort_objects(self.objectList)
            if self.localCenter:
                center = None
                vector = None
                angle = None
            else:
                center = self.center
                vector = self.vector
                angle = self.angle
            for i in self.objectList:

                if self.localCenter:
                    #i.rotate3d_vector(center = (0, 0, 0), vector = self.vector, angle = self.c_baked)
                    i.bake_xyz_rotation()
                if self.rotation_way == 'axis':
                    i.rotate3d_vector(center = center, vector = vector, angle = angle)
                elif self.rotation_way == 'x':
                    i.rotate3d_x(center = center, x_angle = angle)
                elif self.rotation_way == 'y':
                    i.rotate3d_y(center = center, y_angle = angle)
                elif self.rotation_way == 'z':
                    i.rotate3d_z(center = center, z_angle = angle)

                if self.localCenter:
                    i.restore_xyz_baked()
            if self.Background:
                self.Screen.draw_background()
            if self.Shadows:
                for i in z_sorted:
                    i.render_shadows()

            for i in z_sorted:
                i.render(self.groundAll, self.vectorAnim)

            self.current_Object.draw_selection_rect()

            if self.highlight_mouse:
                l = self.Screen.pixelmap_picking.get_array()
                try:
                    m = l[self.mouse_x, self.mouse_y] - 1
                    if m > -1:
                        self.currentVoxel = m
                        self.current_Object.get_highlight(m)
                except(Exception) as detail:
                    print(detail)

            self.blit_to_screen()
            self.idle_done = True

    def stop_animation(self):
        if self.playing_animation:
            self.animation_frames_done = True
            self.playing_animation = False
            if self.animation_id != None:
                self.root.after_cancel(self.animation_id)
            self.currentFrame = self.frame
            self.EntryVar3.set(self.currentFrame)
            self.Time = self.currentFrame
            self.Time_factor.set(self.Time)
            if self.DragAndDropView != None and self.DragAndDropView.winfo_exists():
                img = self.refresh_image()
                self.DragAndDropView.refresh_image(img)

    def AnimSequence_render(self, objects):
        if self.SDL_bind:
            if self.VBOFrames:
                self.toggle_Frames()
        self.load_into_AnimSequence(objects)
        if self.vectorAnim and self.SDL_bind:
            self.load_Vectors_into_AnimSequence(objects)
        if self.SDL_bind:
            if not self.VBOFrames:
                self.toggle_Frames()
        if len(self.AnimSequence) < 1:
            print("fill animation first!")
            return

##        if self.SDL_bind:
##            self.toggle_SDL_Mode()

        outPutDir    = self.output_folder
        outPutName   = self.output_filename
        outPutFormat = self.output_format
        animLength   = self.render_frames
        startFrame   = self.start_frame

        formatstring = "%0" + str(len(outPutFormat)) + "d"

        print(str(formatstring))

        self.stop_animation()
        self.stop_Rotation()
        self.update_objects()
        frame = 0
        length = len(self.AnimSequence) - 1
        self.setup_progress(animLength, start = startFrame)
        anim = startFrame
        if self.localCenter:
            angle = self.c_baked
            C = None
        else:
            angle = self.angle
            C = 0
        print(animLength)
        Xbound = {}
        Ybound = {}
        Zbound = {}
        Xdim = {}
        Ydim = {}
        Zdim = {}

        self.clear_highlight(False)

        for i in objects:
            j = self.ObjectList.index(i)
            (Xbound[j], Ybound[j], Zbound[j], Xdim[j], Ydim[j], Zdim[j]) = i.give_active_bounds()
        while anim <= animLength:
            for i in self.AnimSequence:
                if self.SDL_bind:
                    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
                else:
                    if platform == 'darwin':
                        if self.DragAndDropView != None and self.DragAndDropView.winfo_exists():
                            self.Screen.surface.fill(self.clear_color)
                        else:
                            self.Screen.surface.blit(self.Screen.backgroundImage, (0, 0))
                    else:
                        self.Screen.surface.fill(self.clear_color)
                    self.Screen.pixelmap_picking.init_pic()
                Data = i
                z_sorted = self.z_sort_objects(objects)
                for j in objects:
                    if self.anim_sequence:
                        episode = self.ObjectList.index(j)
                        AnimSequence = self.Animation[episode]
                        try:
                            data = AnimSequence[frame]
                        except:
                            data = Data
                        if self.colorShifter:
                            j.load_frame_size(data, Xbound[episode], Ybound[episode], Zbound[episode],
                                         Xdim[episode], Ydim[episode], Zdim[episode])
                        else:
                            j.load_frame(data, Xbound[episode], Ybound[episode], Zbound[episode],
                                         Xdim[episode], Ydim[episode], Zdim[episode])
                        if self.vectorAnim and self.SDL_bind:
                            try:
                                v_data = self.VectorAnimation[episode][frame]
                            except:
                                continue
                            j.load_vector_frame(v_data, Xbound[episode], Ybound[episode], Zbound[episode],
                                         Xdim[episode], Ydim[episode], Zdim[episode])
                    if self.animation_rotate:
                        c = None
                        if self.object_centers:
                            #j.rotate3d_vector(center = (0, 0, 0), vector = self.vector, angle = self.c_baked)
                            if not self.localCenter:
                                c = j.give_center_parent(-1)
                            j.bake_xyz_rotation()
                            j.rotate3d_vector(center = c, vector = None, angle = C)
                            j.restore_xyz_baked()
                        else:
                            j.rotate3d_vector(center = c, vector = self.vector, angle = C)
                if self.Background:
                    self.Screen.draw_background()
                if self.Shadows:
                    for j in z_sorted:
                        j.render_shadows()

                if self.colorShifter:
                    for j in z_sorted:
                        j.shift_colors(self.R, self.G, self.B)

                for j in z_sorted:
                    j.render(self.groundAll, self.vectorAnim)

                if self.followrender:
                    self.blit_to_screen()
#
                image = self.Screen[0]
                (w, h) = image.size
                background = None
                backgroundAlpha = self.backgroundAlpha
                if self.clearcolor_Compose:
                    color = list(self.clear_color[:-1])
                    alpha = 255 - color[-1]
                    color.append(255)
                    background = Image.new("RGBA", (w, h), tuple(color))
                    #backgroundAlpha = Image.new('L', (w, h), color = alpha)
                if self.saveBackground and self.backgroundImage:
                    if not  background:
                        background = Image.new("RGBA", (w, h))
                    background.paste(self.backgroundImage, (0, 0), backgroundAlpha)
                    img = Image.alpha_composite(background, image)
                elif self.clearcolor_Compose:
                    img = Image.alpha_composite(background, image)
                else:
                    img = image
                img.save(outPutDir + outPutName + str(formatstring) % anim + ".png")

#                    
                frame += 1
                anim += 1
                if anim > animLength:
                    break
                if not self.localCenter:
                    C += self.Rotation_Amount
                if frame >= length:
                    frame = 0
                if self.progressbar == None:
                    return
                else:
                    self.progressbar.advance()
            if anim > animLength:
                break
        self.quit_progress()
        self.angle = self.current_Object.angle()
        self.EntryVar4.set(str(rad2deg(self.angle)))
        self.CVar2.set(str(len(self.AnimSequence)) + " frames rendered")

    def play_AnimSequence(self, objects):
        self.load_key_frames_into_AnimSequence()
        if not self.playing_animation:
            self.playing_animation = True
            Xbound = {}
            Ybound = {}
            Zbound = {}
            Xdim = {}
            Ydim = {}
            Zdim = {}
            for i in objects:
                j = self.ObjectList.index(i)
                (Xbound[j], Ybound[j], Zbound[j], Xdim[j], Ydim[j], Zdim[j]) = i.give_active_bounds()
            self.play_animation_frames(objects, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)

    def start_animation(self, objects, load = True):
        self.setup_numpy(objects)
        if load:
            self.load_into_AnimSequence(objects, update = False)
            if self.vectorAnim and self.SDL_bind:
                self.load_Vectors_into_AnimSequence(objects, update = False)
        if not self.playing_animation:
            Xbound = {}
            Ybound = {}
            Zbound = {}
            Xdim = {}
            Ydim = {}
            Zdim = {}
            self.update_objects()
            for i in objects:
                j = self.ObjectList.index(i)
                (Xbound[j], Ybound[j], Zbound[j], Xdim[j], Ydim[j], Zdim[j]) = i.give_active_bounds()
            self.playing_animation = True
            self.play_animation_frames(objects, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)

    def toggle_animation(self):
        if self.playing_animation:
            self.stop_animation()
            self.update_objects()
        else:
            self.clear_highlight(False)
            self.start_animation(self.objectList)

    def goto_animation_frame(self, objects, frame):
        if self.Time < len(self.AnimSequence):
            self.frame = self.Time

        if self.SDL_bind:
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        else:
            if platform == 'darwin':
                if self.DragAndDropView != None and self.DragAndDropView.winfo_exists():
                    self.Screen.surface.fill(self.clear_color)
                else:
                    self.Screen.surface.blit(self.Screen.backgroundImage, (0, 0))
            else:
                self.Screen.surface.fill(self.clear_color)
            self.Screen.pixelmap_picking.init_pic()
        if not self.playing_animation:
            self.frame = frame
            z_sorted = self.z_sort_objects(objects)
            for i in z_sorted:
                (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = i.give_active_bounds()
                episode = self.ObjectList.index(i)
                AnimSequence = self.Animation[episode]
                if AnimSequence is None:
                    continue
                if self.frame >= len(AnimSequence):
                    continue
                try:
                    data = AnimSequence[self.frame]
                except:
                    continue
                if self.colorShifter:
                    i.load_frame_size(data, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
                    i.shift_colors(self.R, self.G, self.B)
                else:
                    i.load_frame(data, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
                if self.vectorAnim and self.SDL_bind:
                    try:
                        v_data = self.VectorAnimation[episode][self.frame]
                    except:
                        continue
                    i.load_vector_frame(v_data, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim)
            if self.Background:
                self.Screen.draw_background()
            if self.Shadows:
                for i in z_sorted:
                    i.render_shadows()

            for i in z_sorted:
                i.render(self.groundAll, self.vectorAnim)

            self.current_Object.draw_selection_rect()

            self.blit_to_screen()
            self.CVar2.set('Frame :' + str(self.frame))

    def play_animation_frames(self, objects, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim):
        if not self.everyframe:
            self.frame += 1
        self.animation_id = self.root.after(delay_ms, lambda:self.play_animation_frames(objects, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim))
        if not self.animation_frames_done:
            return
        if self.everyframe:
            self.frame += 1
        if self.frame >= len(self.AnimSequence) - 1:
            self.frame = 0
        self.animation_frames_done = False
        if self.SDL_bind:
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        else:
            if platform == 'darwin':
                if self.DragAndDropView != None and self.DragAndDropView.winfo_exists():
                    self.Screen.surface.fill(self.clear_color)
                else:
                    self.Screen.surface.blit(self.Screen.backgroundImage, (0, 0))
            else:
                self.Screen.surface.fill(self.clear_color)
            self.Screen.pixelmap_picking.init_pic()
        if self.playing_animation:
            z_sorted = self.z_sort_objects(objects)
            for i in z_sorted:
                episode = self.ObjectList.index(i)
                AnimSequence = self.Animation[episode]
                if AnimSequence is None:
                    continue
                if self.frame >= len(AnimSequence):
                    continue
                try:
                    data = AnimSequence[self.frame]
                except:
                    continue

                if self.colorShifter:
                    i.load_frame_size(data, Xbound[episode], Ybound[episode], Zbound[episode], Xdim[episode], Ydim[episode], Zdim[episode])
                    i.shift_colors(self.R, self.G, self.B)
                else:
                    i.load_frame(data, Xbound[episode], Ybound[episode], Zbound[episode], Xdim[episode], Ydim[episode], Zdim[episode])
                if self.vectorAnim and self.SDL_bind:
                    try:
                        v_data = self.VectorAnimation[episode][self.frame]
                    except:
                        continue
                    i.load_vector_frame(v_data, Xbound[episode], Ybound[episode], Zbound[episode],
                                 Xdim[episode], Ydim[episode], Zdim[episode])
            if self.Background:
                self.Screen.draw_background()
            if self.Shadows:
                for i in z_sorted:
                    i.render_shadows()

            for i in z_sorted:
                i.render(self.groundAll, self.vectorAnim)

            self.current_Object.draw_selection_rect()

            self.blit_to_screen()
            self.CVar2.set('Frame :' + str(self.frame))
            self.animation_frames_done = True

    def every_frame_toggle(self):
        self.everyframe = not self.everyframe
        self.Every_Frame.set(self.everyframe)

    def toggle_X_R(self, value = None):
        if value is None:
            self.X_r = not self.X_r
        else:
            self.X_r = value
        self.X_R.set(self.X_r)

    def toggle_Y_R(self, value = None):
        if value is None:
            self.Y_r = not self.Y_r
        else:
            self.Y_r = value
        self.Y_R.set(self.Y_r)

    def toggle_Z_R(self, value = None):
        if value is None:
            self.Z_r = not self.Z_r
        else:
            self.Z_r = value
        self.Z_R.set(self.Z_r)

    def toggle_R(self, value = None):
        if value is None:
            self.R = not self.R
        else:
            self.R = value
        self.R_.set(self.R)

    def toggle_G(self, value = None):
        if value is None:
            self.G = not self.G
        else:
            self.G = value
        self.G_.set(self.G)

    def toggle_B(self, value = None):
        if value is None:
            self.B = not self.B
        else:
            self.B = value
        self.B_.set(self.B)

    def toggle_color_Shifter(self, value = None):
        if value is None:
            self.colorShifter = not self.colorShifter
        else:
            self.colorShifter = value
        self.color_Shifter.set(self.colorShifter)

    def wm_configure(self, e):
        if self.wm_update:
            self.stop_animation()
            self.stop_Rotation()
            if self.SDL_bind:
                if self.update_wm == None:
                    self.update_wm = self.root.after(1000, lambda:self.update_frame(self.objectList))
            state = self.root.state()

    def menu_exit(self):
        print('menu_destroy')
        global hpos, border
        if hpos == 0:
            for i in self.m_frames:
                try:
                    self.root.tk.call('wm', 'deiconify', i)
                    self.root.tk.call('wm', 'geometry', i,  "%dx220+%d+0" % (self.hstep - border, hpos))
                    hpos += self.hstep
                except:
                    pass
            hpos = self.pos_H
        else:
            for i in self.m_frames:
                try:
                    self.root.tk.call('wm', 'withdraw', i)
                except:
                    pass
            self.pos_H = hpos
            hpos = 0

    def postmenu(self, me, m, menu = None):
        '''
        WM_DELETE_WINDOW disables closing of opened popups, use q-key, when in focus
        When main application is in focus, use Alt+q to close all menu windows in tearoff
        '''
        print(me, m)
        print(self.m_frames1)
        global hpos, wm_frame
        def hop():
            pass
        try:
            wm_frame = self.root.tk.call('wm', 'frame', me)
            print(wm_frame)
            if menu in self.m_frames1:
                pass
            else:
                self.root.tk.call('wm', 'resizable', m,  '0', '1')
                self.root.tk.call('wm', 'geometry', m,  "%dx500+%d+0" % (self.hstep - border, hpos))

                hpos += self.hstep
                self.m_frames.append(m)
                self.m_frames1.append(menu)
        except():
            pass

    def CleanupVoxels(self, event):
        self.truncate_repros(False)

    def alert_CleanupVoxelsRepro(self):
        if self.msg_box_VoxelsRepro != None and self.msg_box_VoxelsRepro.winfo_exists():
            self.msg_box_VoxelsRepro.lift_it()
            self.msg_box_VoxelsRepro.focus_set()
            self.msg_box_VoxelsRepro.ok_button.focus()
        else:
            self.msg_box_VoxelsRepro = messageBox.MessageBox(parent = self.root, root = self, ok = 'CleanupVoxels',
                                                             T = "Low Memory Warning",
                                                             default = "Clean Voxels Repros?",
                                                             RWidth = self.RWidth, RHeight = self.RHeight,
                                                             bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def set_LocalCenterWithSave(self, event):
        if not self.localCenter:
            self.local_Center.set(True)
            self.toggle_local_Center()
        self.save_all_files()

    def alert_LocalCenter(self):
        if self.msg_box_LocalCenter != None and self.msg_box_LocalCenter.winfo_exists():
            self.msg_box_LocalCenter.lift_it()
            self.msg_box_LocalCenter.focus_set()
            self.msg_box_LocalCenter.ok_button.focus()
        else:
            self.msg_box_LocalCenter = messageBox.MessageBox(parent = self.root, root = self, ok = 'set_LocalCenterWithSave',
                                                             T = "Set Local Center?",
                                                             default = "Before Saving",
                                                             RWidth = self.RWidth, RHeight = self.RHeight,
                                                             bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def exit_self(self, event):
        if self.msg_box_quit_app != None and self.msg_box_quit_app.winfo_exists():
            self.msg_box_quit_app.lift_it()
            self.msg_box_quit_app.focus_set()
            self.msg_box_quit_app.ok_button.focus()
        else:
            self.msg_box_quit_app = messageBox.MessageBox(parent = self.root, root = self, ok = 'callback_exit',
                                                             T = "Exit App?",
                                                             default = "Leave Worldpixel app?",
                                                             RWidth = self.RWidth, RHeight = self.RHeight,
                                                             bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def about_self(self):
        if self.about_box_app != None and self.about_box_app.winfo_exists():
            self.about_box_app.lift_it()
            self.about_box_app.focus_set()
            self.about_box_app.ok_button.focus()
        else:
            self.about_box_app = messageBox.AboutBox(parent = self.root, root = self, ok = 'callback_sound',
                                                             T = "Who is Worldpixel?",
                                                             default = "Allan Kiipli (c)",
                                                             RWidth = self.RWidth, RHeight = self.RHeight,
                                                             bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def callback_sound(self, event):
        print("callback sound")

    def setup_help(self):
        if self.helpbox != None and self.helpbox.winfo_exists():
            self.helpbox.lift_it()
            self.helpbox.focus_set()
        else:
            self.helpbox = messageBox.HelpBox(parent = self.root, root = self, ok = 'Sound Loader Help',
                                                                 T = "Worldpixel",
                                                                 default = "-------------",
                                                                 RWidth = self.RWidth, RHeight = self.RHeight,
                                                                 bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def readme_txt(self):
        filename = "Folders/Source/README.txt"
        if platform == 'darwin':
            subprocess.call(['open', '--', filename])
        elif platform == 'linux2':
            subprocess.call(['gnome-open', filename])
        elif platform == 'win32':
            filename = filename.replace('/', '\\')
            subprocess.call(['notepad', filename])
        elif platform == 'cygwin':
            filename = filename.replace('\\', '/')
            filename = filename.split('/')
            if filename[1] == 'cygdrive':
                filename[2] += ':'
                filename = filename[2:]
            filename = '\\'.join(filename)
            subprocess.call(['notepad', filename])

    def special_flag(self, n):
        self.specialFlag = n
        self.special_Flag.set(self.specialFlag)
        self.Screen.SPECIAL_FLAG = self.Flags[n]
        self.update_frame(self.objectList)

    def open_folder(self, folder):
        if platform == 'darwin':
            subprocess.call(['open', '--', folder])
        elif platform == 'linux2':
            subprocess.call(['gnome-open', folder])
        elif platform == 'win32':
            folder = folder.replace('/', '\\')
            subprocess.call(['explorer', folder])
        elif platform == 'cygwin':
            folder = folder.replace('\\', '/')
            folder = folder.split('/')
            if folder[1] == 'cygdrive':
                folder[2] += ':'
                folder = folder[2:]
            folder = '\\'.join(folder)
            subprocess.call(['explorer', folder])

    def configure_output(self):
        if self.confbox != None and self.confbox.winfo_exists():
            self.confbox.lift_it()
            self.confbox.focus_set()
        else:
            n = (self.output_folder, self.output_filename, self.output_format, self.render_frames, self.start_frame,
                 self.animation_rotate, self.anim_sequence, self.object_centers)
            self.confbox = messageBox.RenderDialog(parent = self.root, root = self, ok = 'configure_func',
                                                                 T = "Worldpixel", n = n,
                                                                 default = "paths",
                                                                 RWidth = self.RWidth, RHeight = self.RHeight,
                                                                 bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def configure_func(self, n):
        self.output_folder        = n[0]
        if self.output_folder[-1] != '/':
            self.output_folder += '/'
        self.output_filename      = n[1]
        self.output_format        = n[2]
        self.render_frames        = n[3]
        self.start_frame          = n[4]
        self.animation_rotate     = n[5]
        self.anim_sequence        = n[6]
        self.object_centers       = n[7]
        path = os.path.join(self.output_folder)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
                return
        try:
            f = open("Folders/config.txt", "w")
            f.write(str(n))
            f.close()
        except:
            print("config not written!")

    def configure_raster(self):
        if self.confbox != None and self.confbox.winfo_exists():
            self.confbox.lift_it()
            self.confbox.focus_set()
        else:
            n = (self.raster_begin, self.raster_end, self.raster_step, self.raster_revolve)
            self.confbox = messageBox.RasterDialog(parent = self.root, root = self, ok = 'configure_func_raster',
                                                                 T = "Worldpixel", n = n, animLength = 100,
                                                                 default = "Raster",
                                                                 RWidth = self.RWidth, RHeight = self.RHeight,
                                                                 bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)
    def configure_func_raster(self, n):
        self.raster_begin    = n[0]
        self.raster_end      = n[1]
        self.raster_step     = n[2]
        self.raster_revolve  = n[3]
        try:
            f = open("Folders/config1.txt", "w")
            f.write(str(n))
            f.close()
        except:
            print("config not written!")

    def refresh_image(self):
        self.lock.acquire()
        img1 = self.Screen[0]
        img = ImageTk.PhotoImage(img1, 'r')
        self.lock.release()
        return img

    def anim_folder_func(self, callback, fileName_0, fileName_1):
        if fileName_0 and fileName_1:
            callback(False, fileName_0, fileName_1)

    def query_anim_folder_files(self, callback, fileName, episode, dim, path):
        if self.crossfadebox != None and self.crossfadebox.winfo_exists():
            self.crossfadebox.lift_it()
            self.crossfadebox.focus_set()
        else:
            self.crossfadebox = messageBox.CrossFadeBox(parent = self.root, root = self, ok = self.anim_folder_func,
                                                                 c = callback, f = fileName, e = episode, d = dim,
                                                                 T = "Worldpixel", p = path,
                                                                 default = "crossfade", font = self.sans8,
                                                                 RWidth = self.RWidth, RHeight = self.RHeight,
                                                                 bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def open_DragAndDropView(self, noimage = False):
        if noimage:
            img = None
        else:
            img = self.refresh_image()
        if self.DragAndDropView != None and self.DragAndDropView.winfo_exists():
            self.DragAndDropView.lift_it(img)
            self.DragAndDropView.focus_set()
        else:
            self.DragAndDropView = DragAndDrop.DragAndDropWindow(parent = self.root, root = self, ok = self.drag_to_canvas,
                                                                 refresh = self.refresh_image,
                                                                 T = "Worldpixel", canvas_w = canvas_w, canvas_h = canvas_h,
                                                                 image = img, default = "Voxels",
                                                                 RWidth = self.RWidth, RHeight = self.RHeight,
                                                                 bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)


    def give_url_string(self, s, return_func):
        return_func(s)

    def open_Url_Filename(self, return_func):
        if self.Url_Filename != None and self.Url_Filename.winfo_exists():
            self.Url_Filename.lift_it(img)
            self.Url_Filename.focus_set()
        else:
            self.Url_Filename = messageBox.Url_Name(parent = self.root, root = self, ok = self.give_url_string,
                                                                 T = "Worldpixel", return_func = return_func,
                                                                 default = "Voxels",
                                                                 RWidth = self.RWidth, RHeight = self.RHeight,
                                                                 bg = widget_bg, hg = widget_hg, ag = widget_ag, fg = widget_fg)

    def callback_exit(self, event):
        if self.idle_id != None:
            self.root.after_cancel(self.idle_id)
        if self.animation_id != None:
            self.root.after_cancel(self.animation_id)
        for i in self.objectList:
            i.join()
        self.root.destroy()
        #sys.exit()

class colorbar():
    N = []
    def __init__(self):
        global nr
        if noPIL == False:
            nr += 1
            self.N.append(palettes[nr])
            palette = ("palette%s" % palettes[nr])
            palette = palette + ".PNG"
            img0 = Image.open(palette_folder + palette)
            img1 = img0.resize((strip_W, strip_H), Image.ANTIALIAS)
            pix = img1.load()
            img = ImageTk.PhotoImage(img1, 'r')
            self.pixload = pix
        else:
            nr += 1
            palette = ("palette%s" % nr)
            palette = palette + ".GIF"
            img1 = open(palette_folder + palette, "rb")
            img2 = base64.encodestring(img1.read())
            img = tk.PhotoImage(data = img2)
            img1.close()
        self.img1 = img1
        self.img = img

class PasteFrame():
    def __init__(self):
        self.image = None
        self.data = None

    def __setitem__(self, image, frame):
        self.image = image
        self.data = frame

    def __getitem__(self):
        return (self.image, self.data)

class cursor():
    def __init__(self, c):
        if noPIL == False:
            cursor = (c + "1")
            cursor = cursor + ".PNG"
            img1 = Image.open(cursor_folder + cursor)
            img = ImageTk.PhotoImage(img1, 'r')
        else:
            cursor = (c + "1")
            cursor = cursor + ".GIF"
            img1 = open(cursor_folder + cursor, "rb")
            img2 = base64.encodestring(img1.read())
            img = tk.PhotoImage(data = img2)
            img1.close()
        self.img = img
        self.x = 0
        self.y = 0

def debug():
    app = tk_App()

if __name__ == "__main__":
    app = tk_App()
