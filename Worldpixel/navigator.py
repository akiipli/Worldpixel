#!python
#
# Worldpixel
# authors: A. Kiipli
#

import sys
import os
import inspect

cmd_folder = "Folders/imgstall/"
print('Worldpixel', cmd_folder)
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

try:
    import embedphoto
except(Exception) as detail:
    print('E1', detail)
    class embedimg():
        def __init__(self):
            self.icon_gif = """"""
            self.square   = """"""
            self.center   = """"""
            self.censym   = """"""
    embedphoto = embedimg()

try:
    from PIL import Image, ImageTk
    from PIL import ImageDraw
    file_extension = "jpg"
    noPIL = False
except:
    file_extension = "gif"
    noPIL = True

pyversion = sys.version_info[0]
platform = sys.platform
sysversion = sys.version

if pyversion < 3:
    import Tkinter as tk
    import tkFont
else:
    import tkinter as tk
    import tkinter.font as tkFont

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

canvas_w = 120
canvas_h = 240

offset_w = 2
offset_h = 2

class animation3d():
    def __init__(self, master, row, column, rowspan, bg, CVar1, transformed_func, scroll_time):
        self.CVar1 = CVar1
        self.frame = tk.Frame(master, bg = widget_bg)
        self.frame.grid(row = row, column = column, rowspan = rowspan)

        self.symZ = False
        self.sym_Z = tk.BooleanVar()
        self.sym_Z.set(self.symZ)

        self.symY = False
        self.sym_Y = tk.BooleanVar()
        self.sym_Y.set(self.symY)

        self.symX = False
        self.sym_X = tk.BooleanVar()
        self.sym_X.set(self.symX)
        
        self.z_symmetry = tk.Checkbutton(self.frame, text = "Z", variable = self.sym_Z, bg = widget_bg, activebackground = widget_ag,
                                         highlightbackground = widget_bg, selectcolor = widget_bg, command = self.toggle_sym_z)
        self.z_symmetry.grid(row = 0, column = 0)
        self.y_symmetry = tk.Checkbutton(self.frame, text = "Y", variable = self.sym_Y, bg = widget_bg, activebackground = widget_ag,
                                         highlightbackground = widget_bg, selectcolor = widget_bg, command = self.toggle_sym_y)
        self.y_symmetry.grid(row = 1, column = 0)
        self.x_symmetry = tk.Checkbutton(self.frame, text = "X", variable = self.sym_X, bg = widget_bg, activebackground = widget_ag,
                                         highlightbackground = widget_bg, selectcolor = widget_bg, command = self.toggle_sym_x)
        self.x_symmetry.grid(row = 2, column = 1)
        self.canvas = tk.Canvas(self.frame, width = canvas_w, height = canvas_h, bg = bg)
        self.canvas.grid(row = 0, column = 1, rowspan = 2)

        if noPIL == True:
            self.square = tk.PhotoImage(data = embedphoto.square)
            self.center = tk.PhotoImage(data = embedphoto.center)
            self.censym = tk.PhotoImage(data = embedphoto.censym)
        else:
            square = Image.open(cmd_folder + "square.png")
            self.square = ImageTk.PhotoImage(square)
            center = Image.open(cmd_folder + "center.png")
            self.center = ImageTk.PhotoImage(center)
            censym = Image.open(cmd_folder + "censym.png")
            self.censym = ImageTk.PhotoImage(censym)

        self.x = 60
        self.z = 60
        self.y = 180

        self.canvas.bind('<Enter>', lambda e, c = self.canvas, m = "p - place transformed OBJ": self.takefocus1(e, c, m))        
        self.canvas.bind('<B1-Motion>', self.move_image_position)
        self.canvas.bind('<Button-1>', self.down)
        self.canvas.bind('<ButtonRelease-1>', self.up)
        self.canvas.bind('<p>', lambda e, f = transformed_func: self.call_tfunc(f, self.x, self.y, self.z))
        self.canvas.bind('<Left>', lambda e: self.move_square(-1, 0))
        self.canvas.bind('<Right>', lambda e: self.move_square(1, 0))
        self.canvas.bind('<Up>', lambda e: self.move_square(0, -1))
        self.canvas.bind('<Down>', lambda e: self.move_square(0, 1))

        self.canvas.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.canvas.bind('<<scrollwheel>>', lambda e: scroll_time(e))

        self.tag = None

    def call_tfunc(self, f, x, y, z):
        
        x = (x - 60) / float(60) * 2.0
        z = (z - 60) / float(60) * 2.0
        y = (y - 180) / float(-60) * 2.0
        print("call_tfunc", x, y, z)
        symX = 0
        symY = 0
        symZ = 0
        if self.symX:
            if x < 0:
                symX = -1
            else:
                symX = 1
        if self.symY:
            if y < 0:
                symY = -1
            else:
                symY = 1
        if self.symZ:
            if z < 0:
                symZ = -1
            else:
                symZ = 1
        f(None, x, y, z, symX, symY, symZ)

    def toggle_sym_x(self):
        self.symX = not self.symX
        self.sym_X.set(self.symX)
        print("toggle_sym_x", self.symX)
        if self.symX:
            x = 60 - (self.x - 60)
            self.canvas.create_image(x + offset_w, self.z + offset_h, image = self.censym, anchor = tk.CENTER, tags = "CenXTop")
            self.canvas.create_image(x + offset_w, self.y + offset_h, image = self.censym, anchor = tk.CENTER, tags = "CenXFront")
            if self.symY:
                y = 180 - (self.y - 180)
                self.canvas.create_image(x + offset_w, y + offset_h, image = self.censym, anchor = tk.CENTER, tags = "CenXYFront")
            if self.symZ:
                z = 60 - (self.z - 60)
                self.canvas.create_image(x + offset_w, z + offset_h, image = self.censym, anchor = tk.CENTER, tags = "CenXZTop")
        else:
            self.canvas.delete("CenXTop")
            self.canvas.delete("CenXFront")
            self.canvas.delete("CenXYFront")
            self.canvas.delete("CenXZTop")
        self.canvas.update()

    def toggle_sym_y(self):
        self.symY = not self.symY
        self.sym_Y.set(self.symY)
        print("toggle_sym_y", self.symY)
        if self.symY:
            y = 180 - (self.y - 180)
            self.canvas.create_image(self.x + offset_w, y + offset_h, image = self.censym, anchor = tk.CENTER, tags = "CenYFront")
            if self.symX:
                x = 60 - (self.x - 60)
                self.canvas.create_image(x + offset_w, y + offset_h, image = self.censym, anchor = tk.CENTER, tags = "CenXYFront")
        else:
            self.canvas.delete("CenYFront")
            self.canvas.delete("CenXYFront")
        self.canvas.update()

    def toggle_sym_z(self):
        self.symZ = not self.symZ
        self.sym_Z.set(self.symZ)
        print("toggle_sym_z", self.symZ)
        if self.symZ:
            z = 60 - (self.z - 60)
            self.canvas.create_image(self.x + offset_w, z + offset_h, image = self.censym, anchor = tk.CENTER, tags = "CenZTop")
            if self.symX:
                x = 60 - (self.x - 60)
                self.canvas.create_image(x + offset_w, z + offset_h, image = self.censym, anchor = tk.CENTER, tags = "CenXZTop")
        else:
            self.canvas.delete("CenZTop")
            self.canvas.delete("CenXZTop")
        self.canvas.update()

    def initarea(self):
        self.canvas.create_image(30 + offset_w, 30 + offset_h, image = self.square, anchor = tk.NW, tags = "SquareTop", state = tk.DISABLED)
        self.canvas.create_image(30 + offset_w, 150 + offset_h, image = self.square, anchor = tk.NW, tags = "SquareFront", state = tk.DISABLED)
        self.canvas.create_text(30 + offset_w, 20 + offset_h, text = "top", justify = tk.LEFT, tags = "Top", state = tk.DISABLED)
        self.canvas.create_text(30 + offset_w, 140 + offset_h, text = "front", justify = tk.LEFT, tags = "Front", state = tk.DISABLED)
        self.canvas.create_image(60 + offset_w, 60 + offset_h, image = self.center, anchor = tk.CENTER, tags = "CenTop")
        self.canvas.create_image(60 + offset_w, 180 + offset_h, image = self.center, anchor = tk.CENTER, tags = "CenFront")
        self.canvas.update()

    def takefocus1(self, event, c, msg):
        if c != None:
            c.focus_set()
        self.CVar1.set(msg)

    def move_square(self, x, y):
        mouse_x = self.canvas.winfo_pointerx()
        mouse_y = self.canvas.winfo_pointery()
        l = self.canvas.winfo_rootx()
        r = self.canvas.winfo_rooty()
        X = mouse_x - l
        Y = mouse_y - r

        enclosed = self.canvas.find_enclosed(X - 20, Y - 20, X + 20, Y + 20)

        if len(enclosed) > 0:
            for i in enclosed:
                t = self.canvas.gettags(i)[0]
                if t == 'CenTop' or t == 'CenFront':
                    self.tag = t
                    break
        else:
            closest = self.canvas.find_closest(x, y)
            for i in closest:
                t = self.canvas.gettags(i)[0]
                if t == 'CenTop' or t == 'CenFront':
                    self.tag = t
                    break
        
        x = self.x + x
        if x < 0:
            x = 0
        if x > 120:
            x = 120
        if self.tag == 'CenTop':
            y = self.z + y
            if y < 0:
                y = 0
            if y > 120:
                y = 120
            self.x = x
            self.z = y
        if self.tag == 'CenFront':
            y = self.y + y
            if y < 120:
                y = 120
            if y > 240:
                y = 240
            self.x = x
            self.y = y
        if self.tag == 'CenTop':
            self.canvas.coords('CenTop', (x + offset_w, y + offset_h))
            self.canvas.coords('CenFront', (x + offset_w, self.y + offset_h))
            if self.symX:
                x = 60 - (self.x - 60)
                self.canvas.coords('CenXTop', (x + offset_w, y + offset_h))
                self.canvas.coords('CenXFront', (x + offset_w, self.y + offset_h))
            if self.symY:
                y = 180 - (self.y - 180)
                self.canvas.coords('CenYFront', (self.x + offset_w, y + offset_h))
                if self.symX:
                    self.canvas.coords('CenXYFront', (x + offset_w, y + offset_h))
            if self.symZ:
                z = 60 - (self.z - 60)
                self.canvas.coords('CenZTop', (self.x + offset_w, z + offset_h))
                if self.symX:
                    self.canvas.coords('CenXZTop', (x + offset_w, z + offset_h))
                    
        elif self.tag == 'CenFront':
            self.canvas.coords('CenTop', (x + offset_w, self.z + offset_h))
            self.canvas.coords('CenFront', (x + offset_w, y + offset_h))
            if self.symX:
                x = 60 - (self.x - 60)
                self.canvas.coords('CenXTop', (x + offset_w, self.z + offset_h))
                self.canvas.coords('CenXFront', (x + offset_w, y + offset_h))
            if self.symY:
                y = 180 - (self.y - 180)
                self.canvas.coords('CenYFront', (self.x + offset_w, y + offset_h))
                if self.symX:
                    self.canvas.coords('CenXYFront', (x + offset_w, y + offset_h))
            if self.symZ:
                z = 60 - (self.z - 60)
                self.canvas.coords('CenZTop', (self.x + offset_w, z + offset_h))
                if self.symX:
                    self.canvas.coords('CenXZTop', (x + offset_w, z + offset_h))        

    def move_image_position(self, event):
        x = event.x
        y = event.y
        if x < 0:
            x = 0
        if x > 120:
            x = 120
        if self.tag == 'CenTop':
            if y < 0:
                y = 0
            if y > 120:
                y = 120
            self.x = x
            self.z = y
        if self.tag == 'CenFront':
            if y < 120:
                y = 120
            if y > 240:
                y = 240
            self.x = x
            self.y = y
        if self.tag == 'CenTop':
            self.canvas.coords('CenTop', (x + offset_w, y + offset_h))
            self.canvas.coords('CenFront', (x + offset_w, self.y + offset_h))
            if self.symX:
                x = 60 - (self.x - 60)
                self.canvas.coords('CenXTop', (x + offset_w, y + offset_h))
                self.canvas.coords('CenXFront', (x + offset_w, self.y + offset_h))
            if self.symY:
                y = 180 - (self.y - 180)
                self.canvas.coords('CenYFront', (self.x + offset_w, y + offset_h))
                if self.symX:
                    self.canvas.coords('CenXYFront', (x + offset_w, y + offset_h))
            if self.symZ:
                z = 60 - (self.z - 60)
                self.canvas.coords('CenZTop', (self.x + offset_w, z + offset_h))
                if self.symX:
                    self.canvas.coords('CenXZTop', (x + offset_w, z + offset_h))
                    
        elif self.tag == 'CenFront':
            self.canvas.coords('CenTop', (x + offset_w, self.z + offset_h))
            self.canvas.coords('CenFront', (x + offset_w, y + offset_h))
            if self.symX:
                x = 60 - (self.x - 60)
                self.canvas.coords('CenXTop', (x + offset_w, self.z + offset_h))
                self.canvas.coords('CenXFront', (x + offset_w, y + offset_h))
            if self.symY:
                y = 180 - (self.y - 180)
                self.canvas.coords('CenYFront', (self.x + offset_w, y + offset_h))
                if self.symX:
                    self.canvas.coords('CenXYFront', (x + offset_w, y + offset_h))
            if self.symZ:
                z = 60 - (self.z - 60)
                self.canvas.coords('CenZTop', (self.x + offset_w, z + offset_h))
                if self.symX:
                    self.canvas.coords('CenXZTop', (x + offset_w, z + offset_h))

    def down(self, event):
        x = event.x
        y = event.y

        enclosed = self.canvas.find_enclosed(x - 20, y - 20, x + 20, y + 20)
        print('enclosed', enclosed)

        if len(enclosed) > 0:
            for i in enclosed:
                t = self.canvas.gettags(i)[0]
                if t == 'CenTop' or t == 'CenFront':
                    self.tag = t
                    break
        else:
            closest = self.canvas.find_closest(x, y)
            print('closest', closest)
            for i in closest:
                t = self.canvas.gettags(i)[0]
                if t == 'CenTop' or t == 'CenFront':
                    self.tag = t
                    break

        if x < 0:
            x = 0
        if x > 120:
            x = 120
        if self.tag == 'CenTop':
            if y < 0:
                y = 0
            if y > 120:
                y = 120
        if self.tag == 'CenFront':
            if y < 120:
                y = 120
            if y > 240:
                y = 240
        if self.tag == 'CenTop':
            self.x = x
            self.z = y
        elif self.tag == 'CenFront':
            self.x = x
            self.y = y

        if self.tag == 'CenTop':
            self.canvas.coords('CenTop', (x + offset_w, y + offset_h))
            self.canvas.coords('CenFront', (x + offset_w, self.y + offset_h))
        elif self.tag == 'CenFront':
            self.canvas.coords('CenTop', (x + offset_w, self.z + offset_h))
            self.canvas.coords('CenFront', (x + offset_w, y + offset_h))

    def up(self, event):
        x = event.x
        y = event.y
        if x < 0:
            x = 0
        if x > 120:
            x = 120
        if self.tag == 'CenTop':
            if y < 0:
                y = 0
            if y > 120:
                y = 120
        if self.tag == 'CenFront':
            if y < 120:
                y = 120
            if y > 240:
                y = 240
        if self.tag == 'CenTop':
            self.x = x
            self.z = y
        elif self.tag == 'CenFront':
            self.x = x
            self.y = y

