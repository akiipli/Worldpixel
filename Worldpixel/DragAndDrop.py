#python
#
#DragAndDrop
#Summel (c) 2014
#A. Kiipli
#---------------
#
#Any included librarys maintain their rights, but this
#code is provided as is.
#If you copy and paste this code, you need to understand
#what it does.

import os
import sys
import threading
import re
import subprocess

pyversion = sys.version_info[0]

if pyversion < 3:
    import Tkinter as tk
else:
    import tkinter as tk

pyversion = sys.version_info[0]
platform = sys.platform
sysversion = sys.version

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
        self.callback(None, self.item, X, Y, data)

    def bindtarget(self):
        self.dnd.bindtarget(self.item, 'text/uri-list', '<Drag>', self.drag, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
        self.dnd.bindtarget(self.item, 'text/uri-list', '<DragEnter>', self.drag_enter, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
        self.dnd.bindtarget(self.item, 'text/uri-list', '<Drop>', self.drop, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y','%D'))

class DragAndDropWindow(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, refresh = None, T = "OK or not", canvas_w = None, canvas_h = None,
                 image = None, default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.query_image = refresh
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.image = image
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        self.canvas = tk.Canvas(self, width = canvas_w, height = canvas_h, bg = bg)
        if self.image is not None:
            self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW, tags = "Screen")
        self.canvas.pack()

        if platform == 'linux2':
            self.dnd = DnD(self.parent)
        else:
            self.dnd = TkDND(self.parent) 

        if platform == 'linux2':
            self.canvasbind = Dnd(self.canvas, self.drag_to_canvas, self.dnd)
            self.canvasbind.bindtarget()
        else:
            self.dnd.bindtarget(self.canvas, self.drag_to_canvas, 'text/uri-list')


        self.canvas.bind('<B1-Motion>', self.root.move_image_position)
        self.canvas.bind('<Button-1>', lambda e, t = 1: self.root.down(e, t))
        self.canvas.bind('<ButtonRelease-1>', self.root.up)
        self.canvas.bind('<Shift_L>', self.root.shift_press)
        self.canvas.bind('<Control_L>', self.root.control_press)
        self.canvas.bind('<KeyRelease>', self.root.key_release)
        self.canvas.bind('<KeyPress>', self.root.key_down)

        self.canvas.bind('<Alt-Left>', lambda e, t = 7: self.root.canvas_move_keys(t, "left"))
        self.canvas.bind('<Alt-Right>', lambda e, t = 7: self.root.canvas_move_keys(t, "right"))
        self.canvas.bind('<Alt-Up>', lambda e, t = 7: self.root.canvas_move_keys(t, "up"))
        self.canvas.bind('<Alt-Down>', lambda e, t = 7: self.root.canvas_move_keys(t, "down"))

        self.canvas.bind('<Alt-Shift-Left>', lambda e, t = 1: self.root.canvas_move_keys(t, "left"))
        self.canvas.bind('<Alt-Shift-Right>', lambda e, t = 1: self.root.canvas_move_keys(t, "right"))
        self.canvas.bind('<Alt-Shift-Up>', lambda e, t = 1: self.root.canvas_move_keys(t, "up"))
        self.canvas.bind('<Alt-Shift-Down>', lambda e, t = 1: self.root.canvas_move_keys(t, "down"))
       
        self.canvas.bind('<Left>', lambda e: self.root.move_conform((-self.root.level.get() * 2.0, 0, 0), [self.root.current_Object,]))
        self.canvas.bind('<Right>', lambda e: self.root.move_conform((self.root.level.get() * 2.0, 0, 0), [self.root.current_Object,]))
        self.canvas.bind('<Up>', lambda e: self.root.move_conform((0, self.root.level.get() * 2.0, 0), [self.root.current_Object,]))
        self.canvas.bind('<Down>', lambda e: self.root.move_conform((0, -self.root.level.get() * 2.0, 0), [self.root.current_Object,]))
        self.canvas.bind('<Delete>', lambda e: self.root.delete_voxels())
        self.canvas.bind('<Control-Delete>', lambda e: self.root.delete_voxel())
        
        self.canvas.bind('<Insert>', lambda e, v = self.root.popvoxel: self.root.insert_voxels(0, [v,]))
        self.canvas.bind('<space>', lambda e: self.root.toggle_Rotation())
        
        self.canvas.bind('<Control-c>', lambda e: self.root.copy_selection())
        self.canvas.bind('<Control-v>', lambda e: self.root.paste_selection())

        self.canvas.bind('<Shift-L>', lambda e: self.root.toggle_local())
        self.canvas.bind('<Shift-F>', lambda e: self.root.toggle_front_View())

        self.canvas.bind('<Shift-A>', lambda e: self.root.add_positions([self.current_Object,]))
        self.canvas.bind('<Shift-R>', lambda e: self.root.reset_position([self.current_Object,]))
        self.canvas.bind('<Shift-O>', lambda e: self.root.toggle_SDL_Mode())

        self.canvas.bind('<Control-n>', lambda e: self.root.set_scene_name_dialog())
        self.canvas.bind('<Control-s>', lambda e: self.root.save_all_files())
        self.canvas.bind('<Control-l>', lambda e: self.root.load_object_scene())
        
        self.canvas.bind('<Control-Left>', lambda e: self.root.move_around((-self.root.level.get(), 0, 0), self.root.ObjectList))
        self.canvas.bind('<Control-Right>', lambda e: self.root.move_around((self.root.level.get(), 0, 0), self.root.ObjectList))
        self.canvas.bind('<Control-Up>', lambda e: self.root.move_around((0, self.root.level.get(), 0), self.root.ObjectList))
        self.canvas.bind('<Control-Down>', lambda e: self.root.move_around((0, -self.root.level.get(), 0), self.root.ObjectList))
        self.canvas.bind('<Shift-Up>', lambda e: self.root.move_around((0, 0, self.root.level.get()), self.root.ObjectList))
        self.canvas.bind('<Shift-Down>', lambda e: self.root.move_around((0, 0, -self.root.level.get()), self.root.ObjectList))
        self.canvas.bind('<Escape>', lambda e: self.root.clear_collected(self.root.objectList))
        self.canvas.bind('<Control-i>', lambda e: self.root.invert_collected(self.root.ObjectList))
        self.canvas.bind('<f>', lambda e: self.root.find_neighbours(self.root.falloff))

        self.canvas.bind('<plus>', lambda e: self.root.refine_levels(True))
        self.canvas.bind('<minus>', lambda e: self.root.collect_voxels())

        self.canvas.bind('<Control-plus>', lambda e: self.root.tune_voxels_size(1.1))
        self.canvas.bind('<Control-minus>', lambda e: self.root.tune_voxels_size(0.9))
        self.canvas.bind('<Shift-D>', lambda e: self.root.display_rendered())

        self.canvas.bind('<Control-Shift-Z>', lambda e: self.root.switch_Zoomed())

        self.canvas.bind('<l>', lambda e: self.root.toggle_Lights())
        self.canvas.bind('<w>', lambda e: self.root.toggle_Wire())
        self.canvas.bind('<g>', lambda e: self.root.toggle_GroundAll())
        self.canvas.bind('<b>', lambda e: self.root.toggle_Background())
        self.canvas.bind('<p>', lambda e: self.root.toggle_animation())
        self.canvas.bind('<t>', lambda e: self.root.toggle_textures())
        self.canvas.bind('<c>', lambda e: self.root.toggle_draw_Cube_All())
        self.canvas.bind('<s>', lambda e: self.root.toggle_Shadows())
        self.canvas.bind('<d>', lambda e: self.root.toggle_draft_Mode())
        self.canvas.bind('<i>', lambda e: self.root.goto_Imagefile())
        self.canvas.bind('<k>', lambda e: self.root.select_same_highlight())

        self.canvas.bind('<y>', lambda e: self.root.toggle_Propagate())

        self.canvas.bind('<Prior>', lambda e: self.root.scroll_objects(-1))
        self.canvas.bind('<Next>', lambda e: self.root.scroll_objects(1))

        self.canvas.bind('<m>', lambda e: self.root.select_same_level())
        self.canvas.bind("0", lambda e: self.root.toggle_Lightsource(0))
        self.canvas.bind("1", lambda e: self.root.toggle_Lightsource(1))

        self.canvas.bind('<Return>', lambda e: self.root.write_key_frame())

        self.canvas.bind('<Enter>', lambda e, c = self.canvas, m = "Set keyboard focus": self.takefocus1(e, c, m))

        self.canvas.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
 
        self.canvas.bind('<<scrollwheel>>', lambda e: self.root.scroll_embed(e, [self.root.current_Object,]))

        self.canvas.bind('<Motion>', self.root.mouse_move)


        self.canvas.bind('<o>', lambda e = None: self.update_image())

        self.bind('<q>', lambda e = None: self.destroy())
        
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, 0, 0))
        self.focus_set()

    def lift_it(self, img):
        self.refresh_image(img)
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def takefocus1(self, event, c, msg):
        if c != None:
            c.focus_set()
        self.root.CVar1.set(msg)
        self.update_image()

    def update_image(self):
        img = self.query_image()
        self.refresh_image(img)

    def refresh_image(self, img):
        self.image = img
        self.canvas.delete("Screen")
        self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW, tags = "Screen")
        self.canvas.update()

    def drag_to_canvas(self, event, widget = None, X = 0, Y = 0, data = None):
        print(widget, X, Y, data)
        self.callback(event, widget, X, Y, data)
        self.update_image()
