#python
#
#messageBox
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

import urllib
import validators

pyversion = sys.version_info[0]

if pyversion < 3:
    import Tkinter as tk
    import Queue
    from tkFileDialog import askdirectory
    from tkFileDialog import askopenfilename
    from tkFileDialog import asksaveasfilename
else:
    import tkinter as tk
    import queue as Queue
    from tkinter.filedialog import askdirectory
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename

pyversion = sys.version_info[0]
platform = sys.platform
sysversion = sys.version

try:
    from PIL import Image, ImageTk, ImageChops
    from PIL import ImageDraw, ImageFont
    file_extension = "jpg"
    noPIL = False
except:
    file_extension = "gif"
    noPIL = True

def open_folder(folder):
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

class Separator():
    def __init__(self, master, grid = None, place = None, width = None, bg = None, **kw):
        self.master = master
        self.grid = grid
        self.kw = kw
        self.w = width
        self.place = place
        self.separator = None
        self.background = bg

    def Place(self):
        if self.place == True:
            self.PlaceSeparator(**self.kw)
        elif self.grid == True:
            self.GriddedSeparator(**self.kw)
        else:    
            self.PackedSeparator(**self.kw)
            
    def Separator(self):
        self.separator = tk.Frame(self.master, relief = 'sunken', width = self.w, height = 2, bd = 1, bg = self.background)
        return self.separator

    def PackedSeparator(self, **kw):
        f = self.Separator()
        f.pack(padx = 5, pady = 5, **kw)

    def GriddedSeparator(self, **kw):
        f = self.Separator()
        f.grid(padx = 5, pady = 5, **kw)

    def PlaceSeparator(self, **kw):
        f = self.Separator()
        f.place(**kw)

class RasterDialog(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", n = None, animLength = 100,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")

        self.animLength = animLength

        self.EntryVar = []
        
        self.EntryVar.insert(0, tk.StringVar())
        self.EntryVar.insert(1, tk.StringVar())
        self.EntryVar.insert(2, tk.StringVar())
        self.EntryVar.insert(3, tk.StringVar())
        
        self.EntryVar[0].trace("w", lambda a, b, c, r = 0: self.change_Var(r))
        self.EntryVar[1].trace("w", lambda a, b, c, r = 1: self.change_Var(r))
        self.EntryVar[2].trace("w", lambda a, b, c, r = 2: self.change_Var(r))
        self.EntryVar[3].trace("w", lambda a, b, c, r = 3: self.change_Var(r))

        self.begin     = n[0]
        self.end       = n[1]
        self.step      = n[2]
        self.turn      = n[3]

        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 3, sticky = tk.NW, padx = 5, pady = 5)

        self.n = list(n)

        self.readVars()
        
        label_begin = tk.Label(frame, text = "Begin", width = 10, bg = bg, activebackground = ag, highlightbackground = hg, fg = fg, relief = tk.RAISED)
        label_begin.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        set_entry_1 = tk.Entry(master = frame, textvariable = self.EntryVar[0], width = 30, highlightbackground = hg)
        set_entry_1.grid(row = 1, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        set_entry_1.bind('<Return>', lambda e: self.EntryVar_confirm(0))
        
        label_end = tk.Label(frame, text = "End", width = 10, bg = bg, activebackground = ag, highlightbackground = hg, fg = fg, relief = tk.RAISED)
        label_end.grid(row = 2, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        set_entry_2 = tk.Entry(master = frame, textvariable = self.EntryVar[1], width = 30, highlightbackground = hg)
        set_entry_2.grid(row = 2, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        set_entry_2.bind('<Return>', lambda e: self.EntryVar_confirm(1))
        
        label_step = tk.Label(frame, text = "Step", width = 10, bg = bg, activebackground = ag, highlightbackground = hg, fg = fg, relief = tk.RAISED)
        label_step.grid(row = 3, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        set_entry_3 = tk.Entry(master = frame, textvariable = self.EntryVar[2], width = 30, highlightbackground = hg)
        set_entry_3.grid(row = 3, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        set_entry_3.bind('<Return>', lambda e: self.EntryVar_confirm(2))

        label_turn = tk.Label(frame, text = "Truns", width = 10, bg = bg, activebackground = ag, highlightbackground = hg, fg = fg, relief = tk.RAISED)
        label_turn.grid(row = 4, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        set_entry_4 = tk.Entry(master = frame, textvariable = self.EntryVar[3], width = 30, highlightbackground = hg)
        set_entry_4.grid(row = 4, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        set_entry_4.bind('<Return>', lambda e: self.EntryVar_confirm(3))

        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.confirm(e, f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.confirm(e, f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 5, column = 0, sticky = tk.NE, padx = 5, pady = 5)
        
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.bind('<Right>', lambda e = None: load_button.focus())
        cancel_button.grid(row = 5, column = 1, sticky = tk.NW, padx = 5, pady = 5)

        load_button = tk.Button(frame, text = "Load", width = 10, command = lambda: self.load_config(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_button.bind('<Return>', lambda e = None: self.load_config())
        load_button.bind('<Left>', lambda e = None: cancel_button.focus())
        load_button.grid(row = 5, column = 2, sticky = tk.NW, padx = 5, pady = 5)
        
        self.bind('<Escape>', lambda e = None: self.destroy())
        
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/2 - 125, self.RHeight/2 - 10))
        self.focus_set()
        self.grab_set()
        ok_button.focus()
        self.ok_button = ok_button

    def load_config(self):
        try:
            with open("Folders/config1.txt", "r") as f:
                n = eval(f.read())
                print(n)
                self.n = n
            self.begin     = self.n[0]
            self.end       = self.n[1]
            self.step      = self.n[2]
            self.turn      = self.n[3]
            self.EntryVar[0].set(self.n[0])
            self.EntryVar[1].set(self.n[1])
            self.EntryVar[2].set(self.n[2])
            self.EntryVar[3].set(self.n[3])
        except:
            print("load_config not successful!")

    def EntryVar_confirm(self, n):
        self.ok_button.focus()

    def change_Var(self, n):
        d = self.EntryVar[n].get()
        try:
            d = int(d)
        except:
            print("no integer")
            return
        if d >= 0 and d <= self.animLength:
            self.n[n] = d

    def readVars(self):
        self.n[0] = self.begin
        self.n[1] = self.end
        self.n[2] = self.step
        self.n[3] = self.turn
        self.EntryVar[0].set(self.n[0])
        self.EntryVar[1].set(self.n[1])
        self.EntryVar[2].set(self.n[2])
        self.EntryVar[3].set(self.n[3])

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def confirm(self, e, f):
        eval('self.root.' + f + '(self.n)')
        self.destroy()

class RenderDialog(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", n = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")

        self.n = list(n)

        self.EntryVar = []
        
        self.EntryVar.insert(0, tk.StringVar())
        self.EntryVar.insert(1, tk.StringVar())
        self.EntryVar.insert(2, tk.StringVar())
        self.EntryVar.insert(3, tk.StringVar())
        self.EntryVar.insert(4, tk.StringVar())
        
        self.EntryVar[0].trace("w", lambda a, b, c, r = 0: self.change_Var(r))
        self.EntryVar[1].trace("w", lambda a, b, c, r = 1: self.change_Var(r))
        self.EntryVar[2].trace("w", lambda a, b, c, r = 2: self.change_Var(r))
        self.EntryVar[3].trace("w", lambda a, b, c, r = 3: self.change_Var(r))
        self.EntryVar[4].trace("w", lambda a, b, c, r = 4: self.change_Var(r))

        self.anim_entry = [tk.BooleanVar(),
                           tk.BooleanVar(),
                           tk.BooleanVar()]

        self.anim_entry[0].set(n[5])
        self.anim_entry[1].set(n[6])
        self.anim_entry[2].set(n[7])

        self.checkmark = [n[5], n[6], n[7]]

        self.directory     = n[0]
        self.filename      = n[1]
        self.numbers       = n[2]
        self.frames        = n[3]
        self.start         = n[4]
        
        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 3, sticky = tk.NW, padx = 5, pady = 5)

        self.C_1 = tk.Checkbutton(master = frame1, command = lambda: self.check(0), text = "rotate",
            variable = self.anim_entry[0], onvalue = True, offvalue = False, width = 10,
            height = 1, background = bg, highlightbackground = hg, activebackground = ag)
        self.C_1.pack(side = tk.RIGHT, fill = "x")

        self.C_2 = tk.Checkbutton(master = frame1, command = lambda: self.check(1), text = "animate",
            variable = self.anim_entry[1], onvalue = True, offvalue = False, width = 10,
            height = 1, background = bg, highlightbackground = hg, activebackground = ag)
        self.C_2.pack(side = tk.RIGHT, fill = "x")

        self.C_3 = tk.Checkbutton(master = frame1, command = lambda: self.check(2), text = "centers",
            variable = self.anim_entry[2], onvalue = True, offvalue = False, width = 10,
            height = 1, background = bg, highlightbackground = hg, activebackground = ag)
        self.C_3.pack(side = tk.RIGHT, fill = "x")

        self.readVars()
        
        set_directory = tk.Button(frame, text = "Directory", width = 10, command = lambda: self.setdirectory(),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        set_directory.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        set_entry_1 = tk.Entry(master = frame, textvariable = self.EntryVar[0], width = 30, highlightbackground = hg)
        set_entry_1.grid(row = 1, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        set_entry_1.bind('<Return>', lambda e: self.EntryVar_confirm(0))
        
        set_filename = tk.Button(frame, text = "Filename", width = 10, command = lambda: self.setfilename(),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        set_filename.grid(row = 2, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        set_entry_2 = tk.Entry(master = frame, textvariable = self.EntryVar[1], width = 30, highlightbackground = hg)
        set_entry_2.grid(row = 2, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        set_entry_2.bind('<Return>', lambda e: self.EntryVar_confirm(1))
        
        set_number_format = tk.Button(frame, text = "format", width = 10, command = lambda: self.setformat(),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        set_number_format.grid(row = 3, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        set_entry_3 = tk.Entry(master = frame, textvariable = self.EntryVar[2], width = 30, highlightbackground = hg)
        set_entry_3.grid(row = 3, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        set_entry_3.bind('<Return>', lambda e: self.EntryVar_confirm(2))

        set_frames = tk.Button(frame, text = "frames", width = 10, command = lambda: self.setframes(),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        set_frames.grid(row = 4, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        set_entry_4 = tk.Entry(master = frame, textvariable = self.EntryVar[3], width = 30, highlightbackground = hg)
        set_entry_4.grid(row = 4, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        set_entry_4.bind('<Return>', lambda e: self.EntryVar_confirm(3))

        set_start = tk.Button(frame, text = "start", width = 10, command = lambda: self.setstart(),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        set_start.grid(row = 5, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        set_entry_5 = tk.Entry(master = frame, textvariable = self.EntryVar[4], width = 30, highlightbackground = hg)
        set_entry_5.grid(row = 5, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        set_entry_5.bind('<Return>', lambda e: self.EntryVar_confirm(4))
        
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.confirm(e, f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.confirm(e, f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 6, column = 0, sticky = tk.NE, padx = 5, pady = 5)
        
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.bind('<Right>', lambda e = None: load_button.focus())
        cancel_button.grid(row = 6, column = 1, sticky = tk.NW, padx = 5, pady = 5)

        load_button = tk.Button(frame, text = "Load", width = 10, command = lambda: self.load_config(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_button.bind('<Return>', lambda e = None: self.load_config())
        load_button.bind('<Left>', lambda e = None: cancel_button.focus())
        load_button.grid(row = 6, column = 2, sticky = tk.NW, padx = 5, pady = 5)
        
        self.bind('<Escape>', lambda e = None: self.destroy())
        
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/2 - 125, self.RHeight/2 - 10))
        self.focus_set()
        self.grab_set()
        ok_button.focus()
        self.ok_button = ok_button

    def check(self, n):
        print("check")
        self.checkmark[n] = not self.checkmark[n]
        self.anim_entry[n].set(self.checkmark[n])
        self.n[n + 5] = self.checkmark[n]
        print(self.n[n + 5])

    def load_config(self):
        try:
            with open("Folders/config.txt", "r") as f:
                n = eval(f.read())
                print(n)
                self.n = n
            if self.n[0][-1] != '/':
                self.n[0] += '/'
            self.directory    = self.n[0]
            self.filename     = self.n[1]
            self.numbers      = self.n[2]
            self.EntryVar[0].set(self.n[0])
            self.EntryVar[1].set(self.n[1])
            self.EntryVar[2].set(self.n[2])
            self.EntryVar[3].set(self.n[3])
            self.EntryVar[4].set(self.n[4])
            self.anim_entry[0].set(self.n[5])
            self.anim_entry[1].set(self.n[6])
            self.anim_entry[2].set(self.n[7])
        except:
            print("load_config not successful!")

    def EntryVar_confirm(self, n):
        if n == 0:
            d = self.EntryVar[n].get()
            if d[-1] != '/':
                d += '/'
            self.EntryVar[n].set(d)
        self.ok_button.focus()

    def change_Var(self, n):
        if n == 0:
            d = self.EntryVar[n].get()
            self.n[n] = d
        elif n == 1:
            f = self.EntryVar[n].get()
            if str(f):
                self.n[n] = f
        elif n == 2:
            N = self.EntryVar[n].get()
            if N == "x" * len(N):
                self.n[n] = N
        elif n == 3:
            F = self.EntryVar[n].get()
            try:
                F = int(F)
            except:
                return
            self.n[n] = F
        elif n == 4:
            s = self.EntryVar[n].get()
            try:
                S = int(s)
            except:
                return
            if S < self.n[3] and S > -1:
                self.n[n] = S

    def readVars(self):
        if self.n[0][-1] != '/':
            self.n[0] += '/'
        self.n[0] = self.directory
        self.n[1] = self.filename
        self.n[2] = self.numbers
        self.n[3] = self.frames
        self.EntryVar[0].set(self.n[0])
        self.EntryVar[1].set(self.n[1])
        self.EntryVar[2].set(self.n[2])
        self.EntryVar[3].set(self.n[3])
        self.EntryVar[4].set(self.n[4])
        self.anim_entry[0].set(self.n[5])
        self.anim_entry[1].set(self.n[6])
        self.anim_entry[2].set(self.n[7])

    def setdirectory(self):
        d = askdirectory(title = "Choose Files Directory",
                         initialdir = self.n[0])
        if len(d) > 0:
            if d[-1] != '/':
                d += '/'
            self.n[0] = d
            self.EntryVar[0].set(d)

    def setfilename(self):
        file_name = "frame"
        self.n[1] = file_name
        self.EntryVar[1].set(file_name)

    def setformat(self):
        format_shape = "xxxx"
        self.n[2] = format_shape
        self.EntryVar[2].set(format_shape)

    def setframes(self):
        frames = 25
        self.n[3] = frames
        self.EntryVar[3].set(frames)

    def setstart(self):
        start = 0
        self.n[4] = start
        self.EntryVar[4].set(start)
        
    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def confirm(self, e, f):
        eval('self.root.' + f + '(self.n)')
        self.destroy()

class ConfigureDirs(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", n = None, cmd = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        self.msg = tk.Message(self, text = default, width = 170, bg = bg)
        self.msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        button_1 = tk.Button(master = self, text = "Load Directory", width = 20, command = lambda: self.putpath(),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        button_1.pack()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")

        self.cmd_dir2 = cmd

        self.EntryVar = []
        
        self.EntryVar.insert(0, tk.StringVar())
        self.EntryVar.insert(1, tk.StringVar())
        self.EntryVar.insert(2, tk.StringVar())
        self.EntryVar.insert(3, tk.StringVar())
        self.EntryVar.insert(4, tk.StringVar())
        
        self.EntryVar[0].trace("w", lambda a, b, c, r = 0: self.change_Var(r))
        self.EntryVar[1].trace("w", lambda a, b, c, r = 1: self.change_Var(r))
        self.EntryVar[2].trace("w", lambda a, b, c, r = 2: self.change_Var(r))
        self.EntryVar[3].trace("w", lambda a, b, c, r = 3: self.change_Var(r))
        self.EntryVar[4].trace("w", lambda a, b, c, r = 4: self.change_Var(r))

        self.dirlist = []

        self.dirlist.insert(0, n[0])
        self.dirlist.insert(1, n[1])
        self.dirlist.insert(2, n[2])
        self.dirlist.insert(3, n[3])
        self.dirlist.insert(4, n[4])

        self.n = [0, 1, 2, 3, 4]

        self.readVars()
        
        load_1 = tk.Button(frame, text = "1", width = 10, command = lambda: self.setpath(0),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_1.grid(row = 0, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        load_entry_1 = tk.Entry(master = frame, textvariable = self.EntryVar[0], width = 30, highlightbackground = hg)
        load_entry_1.grid(row = 0, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        
        load_2 = tk.Button(frame, text = "2", width = 10, command = lambda: self.setpath(1),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_2.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        load_entry_2 = tk.Entry(master = frame, textvariable = self.EntryVar[1], width = 30, highlightbackground = hg)
        load_entry_2.grid(row = 1, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        
        load_3 = tk.Button(frame, text = "3", width = 10, command = lambda: self.setpath(2),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_3.grid(row = 2, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        load_entry_3 = tk.Entry(master = frame, textvariable = self.EntryVar[2], width = 30, highlightbackground = hg)
        load_entry_3.grid(row = 2, column = 1, sticky = tk.NE, padx = 5, pady = 5)

        load_4 = tk.Button(frame, text = "4", width = 10, command = lambda: self.setpath(3),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_4.grid(row = 3, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        load_entry_4 = tk.Entry(master = frame, textvariable = self.EntryVar[3], width = 30, highlightbackground = hg)
        load_entry_4.grid(row = 3, column = 1, sticky = tk.NE, padx = 5, pady = 5)

        load_5 = tk.Button(frame, text = "5", width = 10, command = lambda: self.setpath(4),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_5.grid(row = 4, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        load_entry_5 = tk.Entry(master = frame, textvariable = self.EntryVar[4], width = 30, highlightbackground = hg)
        load_entry_5.grid(row = 4, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.confirm(e, f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.confirm(e, f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 5, column = 0, sticky = tk.NE, padx = 5, pady = 5)
        
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.bind('<Right>', lambda e = None: load_button.focus())
        cancel_button.grid(row = 5, column = 1, sticky = tk.NW, padx = 5, pady = 5)

        load_button = tk.Button(frame, text = "Load", width = 10, command = lambda: self.load_config(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_button.bind('<Return>', lambda e = None: self.load_config())
        load_button.bind('<Left>', lambda e = None: cancel_button.focus())
        load_button.grid(row = 5, column = 2, sticky = tk.NW, padx = 5, pady = 5)
        
        self.bind('<Escape>', lambda e = None: self.destroy())
        
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/2 - 125, self.RHeight/2 - 10))
        self.focus_set()
        self.grab_set()
        ok_button.focus()
        self.ok_button = ok_button

    def putpath(self):
        p = askdirectory(title = "Choose Files Directory",
                         initialdir = self.cmd_dir2)
        self.cmd_dir2 = p
        self.msg.configure(text = p)

    def load_config(self):
        try:
            with open("Folders/dirconfig.txt", "r") as f:
                n = eval(f.read())
                print(n)
                self.n = n
            self.dirlist[0] = self.n[0]
            self.dirlist[1] = self.n[1]
            self.dirlist[2] = self.n[2]
            self.dirlist[3] = self.n[3]
            self.dirlist[4] = self.n[4]
            self.EntryVar[0].set(self.n[0])
            self.EntryVar[1].set(self.n[1])
            self.EntryVar[2].set(self.n[2])
            self.EntryVar[3].set(self.n[3])
            self.EntryVar[4].set(self.n[4])
        except:
            print("load_config not successful!")

    def change_Var(self, n):
        d = self.EntryVar[n].get()
        if os.path.isdir(d):
            self.n[n] = d

    def readVars(self):
        self.n[0] = self.dirlist[0]
        self.n[1] = self.dirlist[1]
        self.n[2] = self.dirlist[2]
        self.n[3] = self.dirlist[3]
        self.n[4] = self.dirlist[4]
        self.EntryVar[0].set(self.n[0])
        self.EntryVar[1].set(self.n[1])
        self.EntryVar[2].set(self.n[2])
        self.EntryVar[3].set(self.n[3])
        self.EntryVar[4].set(self.n[4])

    def setpath(self, n):
        d = askdirectory(title = "Choose Files Directory",
                         initialdir = self.n[n])
        if len(d) > 0:
            self.n[n] = d
            self.EntryVar[n].set(d)

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def confirm(self, e, f):
        eval('self.root.' + f + '(self.n)')
        self.destroy()

class ConfigureBox(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", n = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")

        self.EntryVar = []
        
        self.EntryVar.insert(0, tk.StringVar())
        self.EntryVar.insert(1, tk.StringVar())
        self.EntryVar.insert(2, tk.StringVar())
        
        self.EntryVar[0].trace("w", lambda a, b, c, r = 0: self.change_Var(r))
        self.EntryVar[1].trace("w", lambda a, b, c, r = 1: self.change_Var(r))
        self.EntryVar[2].trace("w", lambda a, b, c, r = 2: self.change_Var(r))

        self.output_folder      = n[0]
        self.plaster_folder     = n[1]
        self.cmd_folder_avatar  = n[2]

        self.n = [0, 1, 2]

        self.readVars()
        
        load_output = tk.Button(frame, text = "Output", width = 10, command = lambda: self.setpath(0),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_output.grid(row = 0, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        load_entry_1 = tk.Entry(master = frame, textvariable = self.EntryVar[0], width = 30, highlightbackground = hg)
        load_entry_1.grid(row = 0, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        
        load_plaster = tk.Button(frame, text = "Plaster", width = 10, command = lambda: self.setpath(1),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_plaster.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        load_entry_2 = tk.Entry(master = frame, textvariable = self.EntryVar[1], width = 30, highlightbackground = hg)
        load_entry_2.grid(row = 1, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        
        load_avatar = tk.Button(frame, text = "Avatar", width = 10, command = lambda: self.setpath(2),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_avatar.grid(row = 2, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        load_entry_3 = tk.Entry(master = frame, textvariable = self.EntryVar[2], width = 30, highlightbackground = hg)
        load_entry_3.grid(row = 2, column = 1, sticky = tk.NE, padx = 5, pady = 5)
        
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.confirm(e, f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.confirm(e, f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 3, column = 0, sticky = tk.NE, padx = 5, pady = 5)
        
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.bind('<Right>', lambda e = None: load_button.focus())
        cancel_button.grid(row = 3, column = 1, sticky = tk.NW, padx = 5, pady = 5)

        load_button = tk.Button(frame, text = "Load", width = 10, command = lambda: self.load_config(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        load_button.bind('<Return>', lambda e = None: self.load_config())
        load_button.bind('<Left>', lambda e = None: cancel_button.focus())
        load_button.grid(row = 3, column = 2, sticky = tk.NW, padx = 5, pady = 5)
        
        self.bind('<Escape>', lambda e = None: self.destroy())
        
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/2 - 125, self.RHeight/2 - 10))
        self.focus_set()
        self.grab_set()
        ok_button.focus()
        self.ok_button = ok_button

    def load_config(self):
        try:
            with open("Folders/config.txt", "r") as f:
                n = eval(f.read())
                print(n)
                self.n = n
            self.output_folder     = self.n[0]
            self.plaster_folder    = self.n[1]
            self.cmd_folder_avatar = self.n[2]
            self.EntryVar[0].set(self.n[0])
            self.EntryVar[1].set(self.n[1])
            self.EntryVar[2].set(self.n[2])
        except:
            print("load_config not successful!")

    def change_Var(self, n):
        d = self.EntryVar[n].get()
        if os.path.isdir(d):
            self.n[n] = d

    def readVars(self):
        self.n[0] = self.output_folder
        self.n[1] = self.plaster_folder
        self.n[2] = self.cmd_folder_avatar
        self.EntryVar[0].set(self.n[0])
        self.EntryVar[1].set(self.n[1])
        self.EntryVar[2].set(self.n[2])

    def setpath(self, n):
        d = askdirectory(title = "Choose Files Directory")
        if len(d) > 0:
            self.n[n] = d
            self.EntryVar[n].set(d)

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def confirm(self, e, f):
        eval('self.root.' + f + '(self.n)')
        self.destroy()

class ProgressBar(tk.Toplevel, threading.Thread):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", bc = None, total = 100, Start = 0,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None, downhill = False):
        tk.Toplevel.__init__(self)
        threading.Thread.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        self.width = 200
        self.msg = tk.Message(self, text = default, width = self.width, bg = bg, fg = fg)
        self.msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", width = 200, bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg, width = self.width, height = 100)
        frame.pack()
        text = tk.Label(frame, bg = bg, fg = fg)
        text.pack(side = tk.LEFT)
        self.progressbar = tk.Frame(self, width = 0, height = 10, bg = bc)
        self.progressbar.pack()
        self.msg1 = tk.Message(self, text = "", width = self.width, bg = bg, fg = fg)
        self.msg1.pack(side = "top", fill = "x")
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        if downhill:
            self.geometry(("%dx%d+%d+%d") % (width + 120, height + 120, self.width - 150, RHeight - height - 200))
        else:
            self.geometry(("%dx%d+%d+%d") % (width + 120, height + 120, self.width, 50))
        self.focus_set()
        self.grab_set()
        self.total = total
        self.done = Start
        self.advanced = 0.0
        self.step = self.width / float(total)
        self.exit = False
        self.exitQ = Queue.Queue()
        self.start()

    def run(self):
        while True:
            self.exit = self.exitQ.get()
            if self.exit == True:
                print('exit is on %s' % str(self))
                return

    def quit(self):
        self.exitQ.put(True)
        self.destroy()

    def set_msg(self, message):
        self.msg['text'] = message

    def set_msg1(self, message):
        self.msg1['text'] = message
        self.msg1.update()

    def advance(self, message = ""):
        self.done += 1
        self.advanced += self.step
        self.msg['text'] = message + str(self.done) + "/" + str(self.total)
        self.msg1['text'] = ""
        self.progressbar['width'] = int(self.advanced)
        self.progressbar.update()
        
class PostMenu(tk.Menu):
    def __init__(self, Self, root, **kwargs):
        tk.Menu.__init__(self, **kwargs)
        self.add('separator')
        self.add_command(label = 'tag info')
        self.supress = None
        self.root = root
        self.Self = Self

    def postit(self, x, y):
        self.post(x, y)
        self.supress = 1
        self.root.after(1001, self.Self.remove_supress)

class ListBox(tk.Listbox):
    def __init__(self, parent, width = None, height = None):
        tk.Listbox.__init__(self, parent, height = height, width = width)
        self.master = parent
        self.width = width
        self.height = height
        self.pic_list = ['pilt1']
        self.pic_index = {'pilt1' : 0}
        self.N = 1
        self.Paste = []
        self.count_items()

    def construct_paste(self):
        self.Paste = self.curselection()

    def deselect(self):
        self.selection_clear(0, len(self.pic_list))

    def select_multiple(self, begin, last):
        self.selection_set(begin, last)

    def select(self, x):
        self.selection_clear(0, len(self.pic_list))
        self.selection_set(x)
        self.see(x)

    def update_list(self, n):
        self.pic_list = n
        self.N = len(self.pic_list)
        self.count_items()

    def count_items(self):
        self.delete(0, self.N)
        self.pic_index = {}
        for x, i in enumerate(self.pic_list):
            self.insert(x, i)
            self.pic_index[i] = x

class About_This_Voxel(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", info = "Info",
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.top = self.winfo_toplevel()
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 270, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.pack(side = "top", fill = "x")
        self.bind('<Escape>', lambda e = None: self.destroy())
        frame_text = tk.Frame(frame, bg = bg)
        frame_text.grid(row = 1, column = 0, sticky = tk.NW, padx = 5, pady = 1)
        T = info.split("\n")
        self.label = [None] * len(T)
        for x, i in enumerate(T):
            self.label[x] = tk.Label(frame_text, width = 100, height = 1, bg = bg, fg = fg)
            self.label[x].configure(text = i, justify = tk.LEFT, anchor = tk.NW)
            self.label[x].pack(fill = tk.X)
            if "\t" in i:
                (A, B) = i.split("\t")
                if A == "image" or A == "repro" or A == "texName" or A == "ground":
                    folder = ""
                    if validators.url(B):
                        folders = B.split('/')
                        folder = "http://" + folders[2]
                    elif os.path.isfile(B):
                        p = os.path.realpath(B)
                        folder, n = os.path.split(p)
                    if folder:
                        self.label[x].bind('<Button-1>', lambda e, f = folder: open_folder(f))
                        self.label[x].bind('<Enter>', lambda e: self.cursor_over())
                        self.label[x].bind('<Leave>', lambda e: self.cursor_off())

        update_button = tk.Button(frame, text = "Update Info", width = 12, command = lambda f = self.callback: self.callback1(f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        update_button.grid(row = 2, column = 0, sticky = tk.NW, padx = 5, pady = 1)

        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (220, height + 220, 0, 0))
        self.focus_set()

    def cursor_over(self):
        self.top.configure(cursor = "hand1")

    def cursor_off(self):
        self.top.configure(cursor = "")

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, f):
        info = eval('self.root.' + f + '()')
        T = info.split("\n")
        for x, i in enumerate(T):
            self.label[x].unbind('<Button-1>')
        for x, i in enumerate(T):
            self.label[x].configure(text = i)
            if "\t" in i:
                (A, B) = i.split("\t")
                if A == "image" or A == "repro" or A == "texName":
                    if os.path.isfile(B):
                        p = os.path.realpath(B)
                        folder, n = os.path.split(p)
                        self.label[x].bind('<Button-1>', lambda e, f = folder: open_folder(f))
        self.update()

class HelpBox(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not",
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 270, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")
        self.bind('<Escape>', lambda e = None: self.destroy())
        frame_text = tk.Frame(frame, bg = bg)
        frame_text.grid(row = 1, column = 0, columnspan = 3, sticky = tk.NW, padx = 5, pady = 1)
        clausetext = tk.Label(frame_text, width = 40, height = 46, bg = bg, fg = fg)
        clausetext.configure(text = """
        Shortcuts:
        On canvas:
            Esc - drop selection
            LCtrl-i - select invert
            Delete - delete selected
            LCtrl-Delete - delete current
            Insert - insert deleted
            Ctrl-c - copy selection
            Ctrl-v - paste selection
            Enter - place keyframe
            Arrows - left, right, up, down
            Scroll - front, back
            f - refresh falloff
            u - update object center
            l - toggle lights in SDL
            p - play/stop animation
            Page up - previous object
            Page down - next object
            i - show voxel image
            k - select same highlight
        On colorpalette:
            p, n, v, b, u, i
            mousemove and arrows
            to choose colors
            mouseclicks
            to place keyframes
            i - creates color undo
            u - loads color undo
        On timeline:
            s - place keyframe
            p - fill/play animation
            scroll to frame
            Enter - goto animation
            control-c - copy keyframe
            control-v - paste keyframe
        Tip:
            Click and drag in canvas
            to select with rectangle
            When spawned voxel
            has some voxels deleted
            partially, then click
            "voxel spawned" after
            navigating to this parent
            voxel with "select super".
            Then click "spawn 0".
            This reinserts voxels.            
        """, justify = tk.LEFT)
        clausetext.pack(side = tk.LEFT)
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width + 120, height + 50, self.RWidth/2 - 125, self.RHeight/5))
        self.focus_set()

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

class AboutBox(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not",
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.image = tk.PhotoImage(file = "Folders/imgstall/Dice.gif")
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 270, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")

        self.imageframe = tk.Label(frame, image = self.image)
        self.imageframe.grid(row = 0, column = 0, rowspan = 2, sticky = tk.N)
        
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.callback1(e, f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.callback1(e, f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 1, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        frame_text = tk.Frame(frame, bg = bg)
        frame_text.grid(row = 2, column = 0, columnspan = 3, sticky = tk.NW, padx = 5, pady = 5)
        clausetext = tk.Label(frame_text, width = 30, height = 27, bg = bg, fg = fg)
        clausetext.configure(text = """
        allankiipli@yahoo.com \n
        --------------------- \n
        Use this software at will. \n
        It is distributed as is. \n
        Any rights to used librarys \n
        are distributed under according \n
        license, if included. \n
        From my part i am ready \n
        to change my terms, if these \n
        licenses say so. \n
        If one plans to sell this \n
        software, he needs to change \n
        at least \n
        two thirds of this code.
        """, justify = tk.LEFT)
        clausetext.pack(side = tk.LEFT)
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width + 120, height + 120, self.RWidth/2 - 125, self.RHeight/5))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, e, f):
        eval('self.root.' + f + '(e)')
        self.destroy()

class MessageBox(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not",
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.callback1(e, f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.callback1(e, f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 0, column = 0, sticky = tk.NE, padx = 5, pady = 5)
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 0, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/2 - 125, self.RHeight/2 - 10))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, e, f):
        eval('self.root.' + f + '(e)')
        #self.destroy()

class Check_Mark(tk.Toplevel):
    def __init__(self, parent, root, ok, T, check_mark, default,
                 RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.pack(side = "top", fill = "x")
        self.Check_lock = check_mark
        self.EntryVar_lock = tk.BooleanVar()
        self.EntryVar_lock.set(self.Check_lock)        
        self.Entry_lock = tk.Checkbutton(master = frame, command = lambda f = self.callback: self.change_Lock(f), text = "",
            variable = self.EntryVar_lock, onvalue = True, offvalue = False, width = 3,
            height = 1, background = bg, highlightbackground = hg, activebackground = ag)
        self.Entry_lock.pack(side = "top", fill = "x")
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def change_Lock(self, f):
        self.Check_lock = not self.Check_lock
        self.EntryVar_lock.set(self.Check_lock)
        eval('self.root.' + f + '(self.Check_lock)')

    def set_Lock(self, value):
        self.Check_lock = value
        self.EntryVar_lock.set(self.Check_lock)
        self.update()

class Image_Panel(tk.Toplevel):
    def __init__(self, parent, root, ok, T, imageFile, default, sceneDir = "",
                 RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.sceneDir = sceneDir
        top = self.winfo_toplevel()
        self.menubar = tk.Menu(top)
        top['menu'] = self.menubar
        self.menu1 = tk.Menu(self.menubar, bg = bg)
        self.menu1.add_command(label = "Save Image", command = self.saveImage)
        self.menubar.add_cascade(label = "List Commands", menu = self.menu1)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.pack(side = "top", fill = "x")
        self.imageFile = imageFile
        
        Height = RHeight - 100
        Width = RWidth - 100

        if imageFile in self.root.Screen.LoadedImages:
            img1 = self.root.Screen.LoadedImages[imageFile]
        if validators.url(imageFile):
            f = cStringIO.StringIO(urllib.urlopen(imageFile).read())
            try:
                img1 = Image.open(f)
            except(Exception) as detail:
                print(detail)
                return
        else:
             img1 = Image.open(imageFile)
        print(img1.size)
        self.img = img1
        if img1.size[0] > Width or img1.size[1] > Height: 
            if Width / float(img1.size[0]) > Height / float(img1.size[1]):
                mult = Height / float(img1.size[1])
            else:
                mult = RWidth / float(img1.size[0])
            w = int(img1.size[0] * mult)
            h = int(img1.size[1] * mult)
            img1 = img1.resize((w, h), Image.ANTIALIAS)
        else:
            w = img1.size[0]
            h = img1.size[1]            
        if img1.mode != 'RGBA':
            img1 = img1.convert("RGBA")
        if platform == 'darwin':
            img = Image.new("RGBA", (w, h), (54, 108, 173, 255))
            img1 = Image.alpha_composite(img, img1)
            
        self.image = ImageTk.PhotoImage(img1)

        self.canvas = tk.Canvas(frame, width = w, height = h, bg = bg)
        self.canvas.pack(side = "top", fill = "x")
        self.canvas.create_image(0, 0, image = self.image, anchor = tk.NW, tags = "ImageDisplay")
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.bind('<i>', lambda e = None: self.destroy())
        self.canvas.update()
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.focus_set()

    def saveImage(self):
        imagesDir = "Images"
        path = os.path.join(self.sceneDir, imagesDir)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print("cannot create directory")
        currentDir = path
        if not os.path.exists(path):
            currentDir = os.getcwd()
        currentName = self.imageFile.split('/')[-1]
        outPutFile = asksaveasfilename(initialfile = currentName, initialdir = currentDir, defaultextension = ".png")
        self.img.save(outPutFile)

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

class Horizontal_Scale(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", L = "scale", cleanup_function = None,
                 I = 5, font = None, default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.entry_font = font
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        self.frame = tk.Frame(self, bg = bg)
        self.frame.pack(side = "top", fill = "x")

        #self.protocol("WM_DELETE_WINDOW", lambda : self.cleanup(cleanup_function))

        self.Scale = I
        self.Scale_factor = tk.IntVar()
        self.Scale_factor.set(self.Scale)
        self.Scale_factor.trace('w', lambda e, m, c, v = self.Scale_factor, f = self.callback: self.limit_entry(e, m, c, v, f))
        self.scale1 = tk.Scale(master = self.frame, orient = tk.HORIZONTAL, from_= 0, to=10, resolution = 1, var = self.Scale_factor, label = L,
                               command = lambda e: self.update_scale_factor(e), bg = bg, highlightbackground = hg, fg = fg, activebackground = ag)
        self.scale1.grid(row = 1, column = 1, padx = 10)
        self.scale1.bind('<Enter>', lambda e, c = self.scale1, m = "Scale factor.": self.takefocus1(e, c, m))
        
        self.scale1.bind('<Left>', lambda e, c = self.Scale: self.adjustScale(e, c, -1))
        self.scale1.bind('<Right>', lambda e, c = self.Scale: self.adjustScale(e, c, 1))

        self.scale1.bind('<g>', lambda e: self.goto_frame())

        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()

    def goto_frame(self):
        width = self.scale1.winfo_width() - 2 * 19
        mouse_x = self.scale1.winfo_pointerx()
        left = self.scale1.winfo_rootx()
        pointer = mouse_x - left - 5
        print(pointer, mouse_x, width)
        frame = int(float(pointer) / float(width) * 10) - 1
        if frame < 0:
            frame = 0
        elif frame > 10:
            frame = 10
        print(frame)
        self.Scale = frame
        self.Scale_factor.set(self.Scale)

    def cleanup(self, f):
        if f is not None:
            eval('self.root.' + f + '()')

    def adjustScale(self, e, c, d):
        c += d
        self.Scale_factor.set(self.Scale)

    def update_scale_factor(self, e):
        self.Scale = self.Scale_factor.get()

    def limit_entry(self, e, m, c, variable, f):
        try:
            n = variable.get()
        except:
            return
        try:
            i = int(n)
            if i > 10:
                variable.set(10)
            elif i < 0:
                variable.set(0)
        except(Exception) as detail:
            print("cannot set not numbers", detail)
        self.callback1(f, False)

    def takefocus1(self, event, c, msg, variable = None, f = None):
        c.focus_set()
        if msg == "Scroll I":
            try:
                n = variable.get()
            except:
                return
            try:
                i = int(n)
                self.EntryVar_I.set("%d" % n)
            except(Exception) as detail:
                print("cannot set not numbers", detail)
        if f:
            self.callback1(f, False)

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, f, destroy = True):
        I = self.Scale_factor.get()
        eval('self.root.' + f + '(' + str(I) + ')')
        if destroy:
            self.destroy()


class Single_Integer_scroll(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not",
                 I = 0, font = None, default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.entry_font = font
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.pack(side = "top", fill = "x")
        label = tk.Label(frame, text = 'rigidity', width = 10, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label.grid(row = 0, column = 0, sticky = tk.W)
        self.EntryVar_I = tk.IntVar()
        self.EntryVar_I.set(I)
        self.EntryVar_I.trace('w', lambda e, m, c, v = self.EntryVar_I, f = self.callback: self.limit_entry(e, m, c, v, f))
        self.Entry_I = tk.Entry(frame, textvariable = self.EntryVar_I, width = 5, font = self.entry_font)
        self.Entry_I.grid(row = 0, column = 1, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_I.bind('<Enter>', lambda e, c = self.Entry_I, m = "Scroll I": self.takefocus1(e, c, m))
        self.Entry_I.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_I.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_I, f = self.callback: self.scroll_Entry(e, v))
        self.Entry_I.bind('<Return>', lambda e = None, f = self.callback: self.callback1(f))

        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()

    def scroll_Entry(self, event, variable):
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
        try:
            n = variable.get()
            n += amount
            if n > 100:
                n = 100
            elif n < 0:
                n = 0
            variable.set("%d" % n)
        except(Exception) as detail:
            print("cannot set not numbers", detail)

    def limit_entry(self, e, m, c, variable, f):
        try:
            n = variable.get()
        except:
            return
        try:
            i = int(n)
            if i > 100:
                variable.set(100)
            elif i < 0:
                variable.set(0)
        except(Exception) as detail:
            print("cannot set not numbers", detail)
        self.callback1(f, False)

    def takefocus1(self, event, c, msg, variable = None, f = None):
        c.focus_set()
        if msg == "Scroll I":
            try:
                n = variable.get()
            except:
                return
            try:
                i = int(n)
                self.EntryVar_I.set("%d" % n)
            except(Exception) as detail:
                print("cannot set not numbers", detail)
        if f:
            self.callback1(f, False)

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, f, destroy = True):
        I = self.EntryVar_I.get()
        eval('self.root.' + f + '(' + str(I) + ')')
        if destroy:
            self.destroy()

        
class Position_Scale_size(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not",
                 sx = 1.0, sy = 1.0, sz = 1.0, px = 0, py = 0, font = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.entry_font = font
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.columnconfigure(2, minsize = True)
        frame.columnconfigure(3, minsize = True)
        frame.columnconfigure(4, minsize = True)
        frame.columnconfigure(5, minsize = True)
        frame.pack(side = "top", fill = "x")
        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 4, padx = 0, pady = 0, sticky = tk.N)
        label_1 = tk.Label(frame1, text = 'sx', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_1.grid(row = 0, column = 0, sticky = tk.W)
        self.EntryVar_sx = tk.DoubleVar()
        self.EntryVar_sx.set(sx)
        self.EntryVar_sx.trace('w', lambda e, m, c, v = self.EntryVar_sx: self.limit_scale_entry(e, m, c, v))
        self.Entry_sx = tk.Entry(frame1, textvariable = self.EntryVar_sx, width = 5, font = self.entry_font)
        self.Entry_sx.grid(row = 0, column = 1, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_sx.bind('<Enter>', lambda e, c = self.Entry_sx, m = "Scroll scale x": self.takefocus1(e, c, m))
        self.Entry_sx.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_sx.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_sx, f = self.callback: self.scroll_scale_Entry(e, v, f))
        label_2 = tk.Label(frame1, text = 'sy', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_2.grid(row = 0, column = 2, sticky = tk.W)
        self.EntryVar_sy = tk.DoubleVar()
        self.EntryVar_sy.set(sy)
        self.EntryVar_sy.trace('w', lambda e, m, c, v = self.EntryVar_sy: self.limit_scale_entry(e, m, c, v))
        self.Entry_sy = tk.Entry(frame1, textvariable = self.EntryVar_sy, width = 5, font = self.entry_font)
        self.Entry_sy.grid(row = 0, column = 3, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_sy.bind('<Enter>', lambda e, c = self.Entry_sy, m = "Scroll scale y": self.takefocus1(e, c, m))
        self.Entry_sy.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_sy.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_sy, f = self.callback: self.scroll_scale_Entry(e, v, f))
        label_3 = tk.Label(frame1, text = 'sz', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_3.grid(row = 0, column = 4, sticky = tk.W)
        self.EntryVar_sz = tk.DoubleVar()
        self.EntryVar_sz.set(sz)
        self.EntryVar_sz.trace('w', lambda e, m, c, v = self.EntryVar_sz: self.limit_scale_entry(e, m, c, v))
        self.Entry_sz = tk.Entry(frame1, textvariable = self.EntryVar_sz, width = 5, font = self.entry_font)
        self.Entry_sz.grid(row = 0, column = 5, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_sz.bind('<Enter>', lambda e, c = self.Entry_sz, m = "Scroll scale z": self.takefocus1(e, c, m))
        self.Entry_sz.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_sz.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_sz, f = self.callback: self.scroll_scale_Entry(e, v, f))

        label_4 = tk.Label(frame1, text = 'px', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_4.grid(row = 1, column = 0, sticky = tk.W)
        self.EntryVar_px = tk.IntVar()
        self.EntryVar_px.set(px)
        self.EntryVar_px.trace('w', lambda e, m, c, v = self.EntryVar_px: self.limit_pos_entry(e, m, c, v))
        self.Entry_px = tk.Entry(frame1, textvariable = self.EntryVar_px, width = 5, font = self.entry_font)
        self.Entry_px.grid(row = 1, column = 1, padx = 0, pady = 1, sticky = tk.W)
        self.Entry_px.bind('<Enter>', lambda e, c = self.Entry_px, m = "Scroll position x": self.takefocus1(e, c, m))
        self.Entry_px.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_px.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_px, f = self.callback: self.scroll_pos_Entry(e, v, f))
        label_5 = tk.Label(frame1, text = 'py', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_5.grid(row = 1, column = 2, sticky = tk.W)
        self.EntryVar_py = tk.IntVar()
        self.EntryVar_py.set(py)
        self.EntryVar_py.trace('w', lambda e, m, c, v = self.EntryVar_py: self.limit_pos_entry(e, m, c, v))
        self.Entry_py = tk.Entry(frame1, textvariable = self.EntryVar_py, width = 5, font = self.entry_font)
        self.Entry_py.grid(row = 1, column = 3, padx = 0, pady = 1, sticky = tk.W)
        self.Entry_py.bind('<Enter>', lambda e, c = self.Entry_py, m = "Scroll position y": self.takefocus1(e, c, m))
        self.Entry_py.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_py.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_py, f = self.callback: self.scroll_pos_Entry(e, v, f))
        label_6 = tk.Label(frame1, text = 'lck', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_6.grid(row = 1, column = 4, sticky = tk.W)
        self.Scale_lock = True
        self.EntryVar_lock = tk.BooleanVar()
        self.EntryVar_lock.set(self.Scale_lock)

        self.Entry_lock = tk.Checkbutton(master = frame1, command = self.change_Lock, text = "",
            variable = self.EntryVar_lock, onvalue = True, offvalue = False, width = 3,
            height = 1, background = bg, highlightbackground = hg, activebackground = ag)
        self.Entry_lock.grid(row = 1, column = 5, padx = 0, pady = 1, sticky = tk.W)

        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.callback1(f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.callback1(f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)
        self.Entry_px.bind('<Return>', lambda e, c = ok_button, m = "ok focus", f = self.callback: self.takefocus1(e, c, m, None, f))
        self.Entry_py.bind('<Return>', lambda e, c = ok_button, m = "ok focus", f = self.callback: self.takefocus1(e, c, m, None, f))
        self.Entry_sx.bind('<Return>', lambda e, c = ok_button, m = "ok scale", v = self.EntryVar_sx, f = self.callback: self.takefocus1(e, c, m, v, f))
        self.Entry_sy.bind('<Return>', lambda e, c = ok_button, m = "ok scale", v = self.EntryVar_sy, f = self.callback: self.takefocus1(e, c, m, v, f))
        self.Entry_sz.bind('<Return>', lambda e, c = ok_button, m = "ok scale", v = self.EntryVar_sz, f = self.callback: self.takefocus1(e, c, m, v, f))
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 1, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def change_Lock(self):
        self.Scale_lock = not self.Scale_lock
        self.EntryVar_lock.set(self.Scale_lock)

    def limit_scale_entry(self, e, m, c, variable):
        try:
            n = variable.get()
        except:
            return
        try:
            i = float(n)
            if i > 10:
                variable.set(10.0)
            elif i < 0:
                variable.set(0.0)
        except(Exception) as detail:
            print("cannot set not numbers", detail)

    def limit_pos_entry(self, e, m, c, variable):
        try:
            n = variable.get()
        except:
            return
        try:
            i = int(n)
            if i > 100:
                variable.set(100)
            elif i < -100:
                variable.set(-100)
        except(Exception) as detail:
            print("cannot set not numbers", detail)

    def takefocus1(self, event, c, msg, variable = None, f = None):
        c.focus_set()
        if msg == "ok scale":
            try:
                n = variable.get()
            except:
                return
            try:
                i = float(n)
                if self.Scale_lock:
                    self.EntryVar_sx.set("%.3f" % n)
                    self.EntryVar_sy.set("%.3f" % n)
                    self.EntryVar_sz.set("%.3f" % n)
            except(Exception) as detail:
                print("cannot set not numbers", detail)
        if f:
            self.callback1(f, False)

    def scroll_scale_Entry(self, event, variable, f):
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
        try:
            n = variable.get()
            n += amount / 100.0
            if self.Scale_lock:
                self.EntryVar_sx.set("%.3f" % n)
                self.EntryVar_sy.set("%.3f" % n)
                self.EntryVar_sz.set("%.3f" % n)
            else:
                variable.set("%.3f" % n)
            self.callback1(f, False)
        except(Exception) as detail:
            print("cannot set not numbers", detail)

    def scroll_pos_Entry(self, event, variable, f):
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
        try:
            n = variable.get()
            n += amount
            variable.set(int(n))
            self.callback1(f, False)
        except(Exception) as detail:
            print("cannot set not numbers", detail)
            
    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, f, destroy = True):
        px = self.EntryVar_px.get()
        py = self.EntryVar_py.get()
        sx = self.EntryVar_sx.get()
        sy = self.EntryVar_sy.get()
        sz = self.EntryVar_sz.get()
        eval('self.root.' + f + '(' + str(px) + ',' + str(py) + ',' + str(sx) + ',' + str(sy) + ',' + str(sz) + ')')
        if destroy:
            self.destroy()

class Canvas_size(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", canvas_w = None, canvas_h = None, font = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.entry_font = font
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.columnconfigure(2, minsize = True)
        frame.columnconfigure(3, minsize = True)
        frame.pack(side = "top", fill = "x")
        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 4, padx = 0, pady = 0, sticky = tk.N)
        label_1 = tk.Label(frame1, text = 'w', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_1.grid(row = 0, column = 0, sticky = tk.W)
        self.EntryVar_w = tk.IntVar()
        self.EntryVar_w.set(canvas_w)
        self.EntryVar_w.trace('w', lambda e, m, c, v = self.EntryVar_w: self.limit_entry(e, m, c, v))
        self.Entry_w = tk.Entry(frame1, textvariable = self.EntryVar_w, width = 5, font = self.entry_font)
        self.Entry_w.grid(row = 0, column = 1, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_w.bind('<Enter>', lambda e, c = self.Entry_w, m = "Scroll canvas width": self.takefocus1(e, c, m))
        self.Entry_w.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_w.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_w: self.scroll_Entry(e, v))
        label_2 = tk.Label(frame1, text = 'h', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_2.grid(row = 0, column = 2, sticky = tk.W)
        self.EntryVar_h = tk.IntVar()
        self.EntryVar_h.set(canvas_h)
        self.EntryVar_h.trace('w', lambda e, m, c, v = self.EntryVar_h: self.limit_entry(e, m, c, v))
        self.Entry_h = tk.Entry(frame1, textvariable = self.EntryVar_h, width = 5, font = self.entry_font)
        self.Entry_h.grid(row = 0, column = 3, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_h.bind('<Enter>', lambda e, c = self.Entry_h, m = "Scroll canvas height": self.takefocus1(e, c, m))
        self.Entry_h.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_h.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_h: self.scroll_Entry(e, v))
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.callback1(e, f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.callback1(e, f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)
        self.Entry_w.bind('<Return>', lambda e, c = ok_button, m = "ok focus": self.takefocus1(e, c, m))
        self.Entry_h.bind('<Return>', lambda e, c = ok_button, m = "ok focus": self.takefocus1(e, c, m))
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 1, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def limit_entry(self, e, m, c, variable):
        try:
            n = variable.get()
        except:
            return
        try:
            i = int(n)
            if i > 1000:
                variable.set(1000)
            elif i < 1:
                variable.set(1)
        except(Exception) as detail:
            print("cannot set not numbers", detail)
            variable.set(1)

    def takefocus1(self, event, c, msg):
        c.focus_set()

    def scroll_Entry(self, event, variable):
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
        try:
            n = variable.get()
            n += amount
            variable.set(int(n))
        except(Exception) as detail:
            print("cannot set not numbers", detail)
            variable.set(1)
            
    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, e, f):
        w = self.EntryVar_w.get()
        h = self.EntryVar_h.get()
        eval('self.root.' + f + '(e,' + str(w) + ',' + str(h) + ')')
        self.destroy()

class CrossFadeBox(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", c = None, f = None, e = None, d = None, p = None,
                 font = None, default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.Callback = c
        self.fileName = f
        self.episode = e
        self.dim = d
        self.path = p
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.entry_font = font
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        self.fileNameList = []
        self.validateFileNames()
        if len(self.fileNameList) < 2:
            self.fileNameList = ["", ""]
        filename_0 = self.fileNameList[0]
        filename_1 = self.fileNameList[1]
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.columnconfigure(2, minsize = True)
        frame.columnconfigure(3, minsize = True)
        frame.pack(side = "top", fill = "x")
        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 4, padx = 0, pady = 0, sticky = tk.N)
        label_1 = tk.Label(frame1, text = '0', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_1.grid(row = 0, column = 0, sticky = tk.W)
        self.EntryVar_0 = tk.StringVar()
        self.EntryVar_0.set(filename_0)
        self.EntryVar_0.trace('w', lambda e, m, c, v = self.EntryVar_0: self.limit_entry(e, m, c, v))
        self.Entry_0 = tk.Entry(frame1, textvariable = self.EntryVar_0, width = 15, font = self.entry_font)
        self.Entry_0.grid(row = 0, column = 1, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_0.bind('<Enter>', lambda e, c = self.Entry_0, m = "Scroll 0": self.takefocus1(e, c, m))
        self.Entry_0.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_0.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_0: self.scroll_Entry(e, v))
        label_2 = tk.Label(frame1, text = '1', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_2.grid(row = 0, column = 2, sticky = tk.W)
        self.EntryVar_1 = tk.StringVar()
        self.EntryVar_1.set(filename_1)
        self.EntryVar_1.trace('w', lambda e, m, c, v = self.EntryVar_1: self.limit_entry(e, m, c, v))
        self.Entry_1 = tk.Entry(frame1, textvariable = self.EntryVar_1, width = 15, font = self.entry_font)
        self.Entry_1.grid(row = 0, column = 3, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_1.bind('<Enter>', lambda e, c = self.Entry_1, m = "Scroll 1": self.takefocus1(e, c, m))
        self.Entry_1.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_1.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_1: self.scroll_Entry(e, v))
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None: self.callback1(e),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None: self.callback1(e))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)
        self.Entry_0.bind('<Return>', lambda e, c = ok_button, m = "ok focus": self.takefocus1(e, c, m))
        self.Entry_1.bind('<Return>', lambda e, c = ok_button, m = "ok focus": self.takefocus1(e, c, m))
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 1, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def validateFileNames(self):
        fileNameList = os.listdir(self.path)
        L = len(self.fileName)
        for i in fileNameList:
            I = i.split('_')
            S = I[-1].split('.')
            print(I)
            if i[:L] == self.fileName and S[0] == str(self.dim):
                self.fileNameList.append(i)
        self.fileNameList.sort()

    def limit_entry(self, e, m, c, variable):
        try:
            n = variable.get()
        except:
            return

    def takefocus1(self, event, c, msg):
        c.focus_set()

    def scroll_Entry(self, event, variable):
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
        try:
            n = variable.get()
            N = self.fileNameList.index(n)
            N += amount
            if N >= len(self.fileNameList):
                N = 0
            if N < 0:
                N = len(self.fileNameList) - 1
            variable.set(self.fileNameList[N])
        except(Exception) as detail:
            print("cannot set", detail)
            
    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, e):
        filename_0 = self.EntryVar_0.get()
        filename_1 = self.EntryVar_1.get()
        self.callback(self.Callback, filename_0, filename_1)
        self.destroy()

class Rotation_size(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", rotation = None, font = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.entry_font = font
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")
        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 2, padx = 0, pady = 0, sticky = tk.N)
        label_1 = tk.Label(frame1, text = 'r', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_1.grid(row = 0, column = 0, sticky = tk.W)
        self.EntryVar_r = tk.IntVar()
        self.EntryVar_r.set(rotation)
        self.EntryVar_r.trace('w', lambda e, m, c, v = self.EntryVar_r: self.limit_entry(e, m, c, v))
        self.Entry_r = tk.Entry(frame1, textvariable = self.EntryVar_r, width = 5, font = self.entry_font)
        self.Entry_r.grid(row = 0, column = 1, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_r.bind('<Enter>', lambda e, c = self.Entry_r, m = "Scroll canvas width": self.takefocus1(e, c, m))
        self.Entry_r.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_r.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_r: self.scroll_Entry(e, v))
        
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.callback1(f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.callback1(f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        self.Entry_r.bind('<Return>', lambda e, c = ok_button, m = "ok focus": self.takefocus1(e, c, m))
        
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 1, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def limit_entry(self, e, m, c, variable):
        try:
            n = variable.get()
        except:
            return
        try:
            i = int(n)
            if i > 360:
                variable.set(0)
            elif i < 0:
                variable.set(360)
        except(Exception) as detail:
            print("cannot set not numbers", detail)
            variable.set(0)

    def takefocus1(self, event, c, msg):
        c.focus_set()

    def scroll_Entry(self, event, variable):
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
        try:
            n = variable.get()
            n += amount
            variable.set(int(n))
        except(Exception) as detail:
            print("cannot set not numbers", detail)
            variable.set(0)
            
    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, f):
        r = self.EntryVar_r.get()
        eval('self.root.' + f + '(' + str(r) + ')')
        self.destroy()

class Spin_size(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", rotation = None, font = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.entry_font = font
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")
        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 2, padx = 0, pady = 0, sticky = tk.N)
        label_1 = tk.Label(frame1, text = 's', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_1.grid(row = 0, column = 0, sticky = tk.W)
        self.EntryVar_r = tk.IntVar()
        self.EntryVar_r.set(rotation)
        self.EntryVar_r.trace('w', lambda e, m, c, v = self.EntryVar_r: self.limit_entry(e, m, c, v))
        self.Entry_r = tk.Entry(frame1, textvariable = self.EntryVar_r, width = 5, font = self.entry_font)
        self.Entry_r.grid(row = 0, column = 1, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_r.bind('<Enter>', lambda e, c = self.Entry_r, m = "Scroll canvas width": self.takefocus1(e, c, m))
        self.Entry_r.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_r.bind('<<scrollwheel>>', lambda e, v = self.EntryVar_r: self.scroll_Entry(e, v))
        
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.callback1(f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.callback1(f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        self.Entry_r.bind('<Return>', lambda e, c = ok_button, m = "ok focus": self.takefocus1(e, c, m))
        
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 1, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def limit_entry(self, e, m, c, variable):
        try:
            n = variable.get()
        except:
            return
        try:
            i = int(n)
            if i > 360:
                variable.set(0)
            elif i < -360:
                variable.set(0)
        except(Exception) as detail:
            print("cannot set not numbers", detail)
            variable.set(0)

    def takefocus1(self, event, c, msg):
        c.focus_set()

    def scroll_Entry(self, event, variable):
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
        try:
            n = variable.get()
            n += amount
            variable.set(int(n))
        except(Exception) as detail:
            print("cannot set not numbers", detail)
            variable.set(0)
            
    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, f):
        r = self.EntryVar_r.get()
        eval('self.root.' + f + '(' + str(r) + ')')
        self.destroy()

class Scene_name(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", filename = None, font = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.entry_font = font
        self.title(T)

        self.scenes = self.load_scenes()
        self.paths = self.load_paths()
        (path, name) = os.path.split(filename)
        if path == "":
            path = self.paths[0]
            name = self.scenes[0]
        if name in self.scenes:
            N = self.scenes.index(name)
        else:
            N = 0
            self.scenes.insert(N, name)
        self.scene_id = N
        self.scene = self.scenes[self.scene_id]

        if path in self.paths:
            N = self.paths.index(path)
        else:
            N = 0
            self.paths.insert(N, path)
        self.path_id = N
        self.path = self.paths[self.path_id]
        
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        self.path_pin = False
        self.name_pin = False
        self.path_Pin = tk.BooleanVar()
        self.name_Pin = tk.BooleanVar()
        self.path_Pin.set(self.path_pin)
        self.name_Pin.set(self.name_pin)
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")
        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 2, padx = 0, pady = 0, sticky = tk.N)
        label_0 = tk.Label(frame1, text = 'path', width = 5, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_0.grid(row = 0, column = 0, sticky = tk.W)
        label_1 = tk.Label(frame1, text = 'name', width = 5, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_1.grid(row = 1, column = 0, sticky = tk.W)
        self.C_0 = tk.Checkbutton(master = frame1, command = lambda: self.check_path_pin(), text = "pin exsist",
            variable = self.path_Pin, onvalue = True, offvalue = False, width = 10,
            height = 1, background = bg, highlightbackground = hg, activebackground = ag)
        self.C_0.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = tk.N)
        self.C_1 = tk.Checkbutton(master = frame1, command = lambda: self.check_name_pin(), text = "pin exsist",
            variable = self.name_Pin, onvalue = True, offvalue = False, width = 10,
            height = 1, background = bg, highlightbackground = hg, activebackground = ag)
        self.C_1.grid(row = 1, column = 1, padx = 0, pady = 0, sticky = tk.N)
        self.EntryVar_f1 = tk.StringVar()
        self.EntryVar_f1.set(path)
        self.EntryVar_f1.trace('w', lambda e, m, c, v = self.EntryVar_f1: self.limit_entry1(e, m, c, v))
        self.EntryVar_f = tk.StringVar()
        self.EntryVar_f.set(name)
        self.EntryVar_f.trace('w', lambda e, m, c, v = self.EntryVar_f: self.limit_entry(e, m, c, v))
        self.excluded_dir_names_list = ["Pic", "key_frame", "Scene", "Back", "Voxels",
                                        "Raster", "object", "Source", "OBJ", "imgstall",
                                        "Images", "resources"]

        self.Entry_f1 = tk.Entry(frame1, textvariable = self.EntryVar_f1, width = 30, font = self.entry_font)
        self.Entry_f1.grid(row = 0, column = 2, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_f1.bind('<Enter>', lambda e, c = self.Entry_f1, m = "Enter path": self.takefocus1(e, c, m))

        self.Entry_f1.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_f1.bind('<<scrollwheel>>', lambda e: self.scroll_Path(e))
        self.Entry_f1.bind('<Up>', lambda e: self.scroll_Path(e))
        self.Entry_f1.bind('<Down>', lambda e: self.scroll_Path(e))
        
        self.Entry_f = tk.Entry(frame1, textvariable = self.EntryVar_f, width = 30, font = self.entry_font)
        self.Entry_f.grid(row = 1, column = 2, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_f.bind('<Enter>', lambda e, c = self.Entry_f, m = "Enter name": self.takefocus1(e, c, m))

        self.Entry_f.event_add('<<scrollwheel>>', '<MouseWheel>', '<Button-4>', '<Button-5>')
        self.Entry_f.bind('<<scrollwheel>>', lambda e: self.scroll_Scene(e))
        self.Entry_f.bind('<Up>', lambda e: self.scroll_Scene(e))
        self.Entry_f.bind('<Down>', lambda e: self.scroll_Scene(e))
        
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.callback1(f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.callback1(f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        self.Entry_f.bind('<Return>', lambda e, c = ok_button, m = "ok focus": self.takefocus1(e, c, m))
        
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 1, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def check_path_pin(self):
        self.path_pin = not self.path_pin
        self.path_Pin.set(self.path_pin)
        if self.path_pin:
            print("path pin 1")
            paths = []
            for i in self.paths:
                if os.path.exists(i):
                    paths.append(i)
            self.paths = paths
            print("path pin 2", self.paths)
        else:
            self.paths = self.load_paths()
        path = self.EntryVar_f1.get()
        if path in self.paths:
            N = self.paths.index(path)
        else:
            N = 0
            self.paths.insert(N, path)
        self.path_id = N
        self.path = self.paths[self.path_id]

    def check_name_pin(self):
        self.name_pin = not self.name_pin
        self.name_Pin.set(self.name_pin)
        if self.name_pin:
            path = self.EntryVar_f1.get()
            print("name pin 1", path)
            if os.path.exists(path):
                self.scenes = os.listdir(path)
                self.scenes.sort()
                print("name pin 2")
        else:
            self.scenes = self.load_scenes()
        name = self.EntryVar_f.get()
        if name in self.scenes:
            N = self.scenes.index(name)
        else:
            N = len(self.scenes) - 1
            l = len(name)
            I = []
            for i in self.scenes:
                I.append(i[0:l])
            if name in I:
                N = I.index(name)
            self.scenes.insert(N, name)
        self.scene_id = N
        self.scene = self.scenes[self.scene_id]

    def load_scenes(self):
        try:
            file = open("Folders/scenes.txt", "r")
            scenes = eval(file.read())
            file.close()
        except:
            print("no scenes.txt")
            scenes = []
        return scenes

    def load_paths(self):
        try:
            file = open("Folders/paths.txt", "r")
            paths = eval(file.read())
            file.close()
        except:
            print("no paths.txt")
            paths = []
        return paths

    def write_scenes(self, filename):
        if filename not in self.scenes:
            self.scenes.insert(0, filename)
        self.scenes = list(set(self.scenes))
        self.scenes.sort()
        i = self.scenes.index(filename)
        scenes1 = self.scenes[:i]
        scenes2 = self.scenes[i:]
        self.scenes = scenes2 + scenes1
        try:
            file = open("Folders/scenes.txt", "w")
            file.write(str(self.scenes))
            file.close()
        except:
            print("no scenes.txt written")

    def write_paths(self, filename):
        if filename not in self.paths:
            self.paths.insert(0, filename)
        self.paths = list(set(self.paths))
        self.paths.sort()
        i = self.paths.index(filename)
        paths1 = self.paths[:i]
        paths2 = self.paths[i:]
        self.paths = paths2 + paths1
        try:
            file = open("Folders/paths.txt", "w")
            file.write(str(self.paths))
            file.close()
        except:
            print("no paths.txt written")

    def scroll_Scene(self, event):
        amount = 0
        if event.keycode == 111:
            print("linux key up")
            amount = -1
        elif event.keycode == 116:
            print("linux key down")
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

        N = self.scene_id
        N += amount

        if N >= len(self.scenes):
            N = 0
        if N < 0:
            N = len(self.scenes) - 1
        self.scene_id = N
        self.scene = self.scenes[int(N)]
        self.EntryVar_f.set(self.scene)

    def scroll_Path(self, event):
        if self.name_pin:
            self.check_name_pin()
        amount = 0
        if event.keycode == 111:
            print("linux key up")
            amount = -1
        elif event.keycode == 116:
            print("linux key down")
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

        N = self.path_id
        N += amount

        if N >= len(self.paths):
            N = 0
        if N < 0:
            N = len(self.paths) - 1
        self.path_id = N
        self.path = self.paths[int(N)]
        self.EntryVar_f1.set(self.path)

    def limit_entry(self, e, m, c, variable):
        try:
            n = variable.get()
            print(n)
        except:
            return
        try:
            n = n.replace(" ", "-")
            R = re.match(r'([a-zA-Z]*)([\-]?)([a-zA-Z]*)([\-]?)(\d*)', n)
            N = "".join(R.groups())
            if N in self.excluded_dir_names_list:
                N = "Custom"
            variable.set(N)
        except(Exception) as detail:
            print("cannot set filename", detail)
            variable.set("Custom")

    def limit_entry1(self, e, m, c, variable):
        try:
            n = variable.get()
            print(n)
        except:
            return
        try:
            N = n.replace("\\", "/")
        except(Exception) as detail:
            print("cannot set path", detail)
            N = ""
        variable.set(N)
        self.path = N

    def takefocus1(self, event, c, msg):
        c.focus_set()

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, f):
        path = self.EntryVar_f1.get()
        scene = self.EntryVar_f.get()
        print("1", path, scene)
        self.write_scenes(scene)
        self.write_paths(path)
        scene_path = os.path.join(path, scene)
        scene_path = scene_path.replace("\\", "/")
        evalstring = 'self.root.' + f + '("' + scene_path + '")'
        print(evalstring)
        eval(evalstring)
        self.destroy()

class Url_Name(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", return_func = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.return_func = return_func
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")
        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 2, padx = 0, pady = 0, sticky = tk.N)
        label_1 = tk.Label(frame1, text = 'url', width = 5, relief = tk.SUNKEN, bd = 1, bg = bg, fg = fg)
        label_1.grid(row = 0, column = 0, sticky = tk.W)
        self.EntryVar_o = tk.StringVar()
        self.EntryVar_o.set("http://")
        self.Entry_o = tk.Entry(frame1, textvariable = self.EntryVar_o, width = 30)
        self.Entry_o.grid(row = 0, column = 1, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_o.bind('<Enter>', lambda e, c = self.Entry_o, m = "Enter name": self.takefocus1(e, c, m))
        
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.callback1(f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.callback1(f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        self.Entry_o.bind('<Return>', lambda e, c = ok_button, m = "ok focus": self.takefocus1(e, c, m))
        
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 1, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def takefocus1(self, event, c, msg):
        c.focus_set()

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, f):
        name = self.EntryVar_o.get()
        self.callback(name, self.return_func)
        self.destroy()

class Object_name(tk.Toplevel):
    def __init__(self, parent = None, root = None, ok = None, T = "OK or not", objectname = None, font = None,
                 default = "OK", RWidth = None, RHeight = None, bg = None, ag = None, hg = None, fg = None):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.root = root
        self.callback = ok
        self.RWidth = RWidth
        self.RHeight = RHeight
        self.entry_font = font
        self.title(T)
        self.configure(takefocus = True, bg = bg)
        self.transient(self.parent)
        msg = tk.Message(self, text = default, width = 170, bg = bg)
        msg.pack(side = "top", fill = "x")
        separator = Separator(master = self, grid = False, side = "top", fill = "x", bg = bg)
        separator.Place()
        frame = tk.Frame(self, bg = bg)
        frame.columnconfigure(0, minsize = True)
        frame.columnconfigure(1, minsize = True)
        frame.pack(side = "top", fill = "x")
        frame1 = tk.Frame(frame, bg = bg)
        frame1.grid(row = 0, column = 0, columnspan = 2, padx = 0, pady = 0, sticky = tk.N)
        label_1 = tk.Label(frame1, text = 'n', width = 3, relief = tk.SUNKEN, bd = 1, font = self.entry_font, bg = bg, fg = fg)
        label_1.grid(row = 0, column = 0, sticky = tk.W)
        self.EntryVar_o = tk.StringVar()
        self.EntryVar_o.set(objectname)
        self.EntryVar_o.trace('w', lambda e, m, c, v = self.EntryVar_o: self.limit_entry(e, m, c, v))
        self.excluded_dir_names_list = ["Pic", "key_frame", "Scene", "Back", "Voxels",
                                        "Raster", "object", "Source", "OBJ", "imgstall",
                                        "Images", "resources"]
        self.Entry_o = tk.Entry(frame1, textvariable = self.EntryVar_o, width = 30, font = self.entry_font)
        self.Entry_o.grid(row = 0, column = 1, padx = 0, pady = 1, sticky = tk.N)
        self.Entry_o.bind('<Enter>', lambda e, c = self.Entry_o, m = "Enter name": self.takefocus1(e, c, m))
        
        ok_button = tk.Button(frame, text = "OK", width = 10, command = lambda e = None, f = self.callback: self.callback1(f),
                              bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        ok_button.bind('<Return>', lambda e = None, f = self.callback: self.callback1(f))
        ok_button.bind('<Right>', lambda e = None: cancel_button.focus())
        ok_button.grid(row = 1, column = 0, sticky = tk.NE, padx = 5, pady = 5)

        self.Entry_o.bind('<Return>', lambda e, c = ok_button, m = "ok focus": self.takefocus1(e, c, m))
        
        cancel_button = tk.Button(frame, text = "Cancel", width = 10, command = lambda: self.destroy(),
                                  bg = bg, activebackground = ag, highlightbackground = hg, fg = fg)
        cancel_button.bind('<Return>', lambda e = None: self.destroy())
        cancel_button.bind('<Left>', lambda e = None: ok_button.focus())
        cancel_button.grid(row = 1, column = 1, sticky = tk.NW, padx = 5, pady = 5)
        self.bind('<Escape>', lambda e = None: self.destroy())
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        self.geometry(("%dx%d+%d+%d") % (width, height, self.RWidth/3 - 125, self.RHeight/3 - 10))
        self.focus_set()
        ok_button.focus()
        self.ok_button = ok_button

    def limit_entry(self, e, m, c, variable):
        try:
            n = variable.get()
            print(n)
        except:
            return
        try:
            n = n.replace(" ", "-")
            R = re.match(r'([a-zA-Z]*)([\-]?)([a-zA-Z]*)([\-]?)(\d*)', n)
            objectname = "".join(R.groups())
            if objectname in self.excluded_dir_names_list:
                objectname = "object-x"
            variable.set(objectname)
        except(Exception) as detail:
            print("cannot set filename", detail)
            variable.set("object-x")

    def takefocus1(self, event, c, msg):
        self.limit_entry(0, 0, 0, self.EntryVar_o)
        c.focus_set()

    def lift_it(self):
        if platform == 'darwin':
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        if platform == 'cygwin':
            pass
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def callback1(self, f):
        name = self.EntryVar_o.get()
        print("1", name)
        evalstring = 'self.root.' + f + '("' + name + '")'
        print(evalstring)
        eval(evalstring)
        self.destroy()
