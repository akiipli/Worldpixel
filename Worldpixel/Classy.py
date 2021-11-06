#!python
#
# Worldpixel module
# authors: A. Kiipli
#
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image, ImageTk, ImageChops
from PIL import ImageDraw, ImageFont, ImageFilter
from numpy import *
import threading
import os, sys, inspect
import pygame, pygame.mixer, pygame.image, pygame.surfarray
from pygame.locals import *
import struct
import random
import math
import scan_object
import re

import time
import sys

import urllib
import validators

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

lastusedDir = "."

arrow = ( "11                      ",
          "101                     ",
          "1001                    ",
          "10001                   ",
          "100001                  ",
          "1000001                 ",
          "10000001                ",
          "100000001               ",
          "1000000001              ",
          "10000000001             ",
          "100000011111            ",
          "10001001                ",
          "10011001                ",
          "101 11001               ",
          "11   1001               ",
          "1     1001              ",
          "      1001              ",
          "       1001             ",
          "       1001             ",
          "        11              ",
          "                        ",
          "                        ",
          "                        ",
          "                        ")

from transformer import Transformer
import obj_loader

try:
    import psutil
    psutil_enable = True
except:
    psutil_enable = False

Blur_master = 1.5

mem_Limit = 80.0

object_masks = []
object_maskimages = []
object_masks.append(None)
object_maskimages.append(None)

label_w = 30
label_h = 30

rotation_amount = pi / 180.0

image_folder = "Folders/imgstall/"
rsc_folder = "Folders/resources/"
fontPath = rsc_folder + "Fonts/"
pygame.font.init()
formant_diamond = pygame.font.Font(fontPath + "Formant.ttf", 8)
fonts = []
fonts.append(formant_diamond)
fontcolor = (255, 255, 0, 255)
backgroundcolor = (0, 0, 0, 255)
gl_backgroundcolor = (1.0, 1.0, 1.0, 1.0)
ground_image = "grass-ground.jpg"
background_image = "BlueSea.png"
if sys.platform == "darwin":
    groundcolor = (100, 100, 127, 255)
else:
    groundcolor = (100, 100, 127, 200)
gl_groundcolor = (0.4, 0.4, 0.5, 0.75)
gl_selectioncolor = (1.0, 1.0, 1.0, 1.0)
gl_black = (0.0, 0.0, 0.0, 1.0)
shadowcolor = (127, 127, 127, 127)
gl_shadowcolor = (0.5, 0.5, 0.5, 0.5)
objectcolor = (255, 255, 127, 255)
gl_objectcolor = (1.0, 1.0, 0.5, 1.0)

def set_object_color(color):
    global objectcolor, gl_objectcolor
    objectcolor = color
    gl_objectcolor = (color[0] / float(255), color[1] / float(255),
                      color[2] / float(255), color[3] / float(255))

def set_shadow_color(color):
    global shadowcolor, gl_shadowcolor
    shadowcolor = color
    gl_shadowcolor = (color[0] / float(255), color[1] / float(255),
                      color[2] / float(255), color[3] / float(255))
alphaline = (255, 255, 255, 255)
alphalinewidth = 3
alpha_clear = (0, 0, 0, 0)

def normalize(vector):
    d = sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    return (vector[0] / d, vector[1] / d, vector[2] / d)

lightdir = normalize((-1, -1, -1))

linecolor = [tuple] * 12
for i in range(12):
    A = i * 10
    linecolor[i] = (A, A, 0, 255)
linewidth = 1
h_color = (255, 255, 255, 255)
i_color = (255, 255, 0, 255)
f_color = (0, 0, 0, 0)

backup_linecolor = None

hi_linecolor = [tuple] * 12
for i in range(12):
    A = i * 10 + 100
    hi_linecolor[i] = (A, A, 0, 255)

pi2 = pi * 2.0
sqrt_3 = sqrt(3.0)

pyversion = sys.version_info[0]
platform = sys.platform

if platform == "darwin":
    shadowcolor = (127, 127, 127, 255)

canvas_w = 460
canvas_h = 460

clearcolor = (0, 0, 0, 0)

scale = 1.5
img_len = 159
screen_depth = float(320)
voxel_limit = 612 * 80
dim = 4
levelLimit = 0.0078125

datatype = int32
for_depth_divisions = 162

if pyversion < 3:
    import cStringIO
    from tkFileDialog import askopenfilename
else:
    from io import StringIO
    from tkinter.filedialog import askopenfilename

def validate_filename(filename, dialog = True):
    if filename is None:
        return None
    if validators.url(filename):
        if internetOn:
            return filename
        else:
            return None
    filename = filename.replace("\\","/")
    if filename == "empty":
        return "empty"
    if not os.path.exists(filename):
        if os.path.isabs(filename):
            return None
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
            return None
    else:
        return filename

def load_object_repro(filename, Frames = 1, p = (0, 0, 1.0, 1.0, 1.0), t = (False, True), progress = None, useLoaded = True):
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
        return None
    if not os.path.exists(filename):
        return None

    if filename in screen.objFileNames and useLoaded:
        OBJ_repro = screen.objFileNames[filename]
    else:
        faces = obj_loader.load(filename)
        print("polys", len(faces))
        Faces = []
        Verts = []
        Norms = []
        if Frames > 1:
            Faces, Verts, Norms = obj_loader.load_Faces(filename, progress, False)
        OBJ_repro = obj_loader.obj_transform(faces, Faces, Verts, Norms)
        screen.obj_transforms.append(OBJ_repro)
        screen.objFileNames[filename] = OBJ_repro

    if screen.SDL_Mode and OBJ_repro:
        if screen.VBO:
            if not OBJ_repro.VBO:
                OBJ_repro.set_up_vertex_array()
        elif not OBJ_repro.objdisplayList:
            OBJ_repro.set_up_display_list()

        OBJ_repro.tune_Position_And_Scale(p)
        OBJ_repro.tune_Wire_Render(t)

    return OBJ_repro

def load_object_texture(texName, useLoaded = True):
    print(texName)
    if texName != "empty":
        try:
            l = len(texName)
        except:
            l = len(str(texName))
        if l > 0:
            if not validators.url(texName):
                texName = os.path.normpath(texName)
                print(texName)
                try:
                    texName = os.path.relpath(texName).replace("\\","/")
                except:
                    print("using absolute path")
                if not os.path.exists(texName):
                    return (None, None)
            elif not internetOn:
                return (None, None)
        else:
            return (None, None)

    texture = None
    if texName:
        if screen.SDL_Mode:
            if texName in screen.texNamesList and useLoaded:
                texture = screen.texNamesList[texName]
            else:
                texture = screen.TexFromPNG(texName)
        else:
            texName = None
            texture = None

    return (texture, texName)

class background_spawner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def spawn_invisible(self, voxel):
        voxel.spawn_invisible_sub_voxels()

class line_3d():
    def __init__(self, A, B):
        self.voxels = [object] * 2
        self.voxels[0] = A
        self.voxels[1] = B
        self.center_z()

    def center_z(self):
        self.z_center = (self.voxels[0].z_rotated + self.voxels[1].z_rotated) / 2.0

    def __getitem__(self, i):
        return self.voxels[i]

class cube_3d(Transformer):
    def __init__(self, superior, radius, name, index):
        self.v = v = [object] * 9
        v[0] = Coordinates_3d(( radius, -radius,  radius))
        v[1] = Coordinates_3d(( radius,  radius,  radius))
        v[2] = Coordinates_3d((-radius,  radius,  radius))
        v[3] = Coordinates_3d((-radius, -radius,  radius))
        v[4] = Coordinates_3d(( radius, -radius, -radius))
        v[5] = Coordinates_3d(( radius,  radius, -radius))
        v[6] = Coordinates_3d((-radius,  radius, -radius))
        v[7] = Coordinates_3d((-radius, -radius, -radius))
        v[8] = Coordinates_3d(( 0,  0,  0))
        Transformer.__init__(self, name = name)
        self.voxels = voxels = self.print_voxels()
        self.l = l = [object] * 12
        l[0] = line_3d(voxels[0], voxels[1])
        l[1] = line_3d(voxels[1], voxels[2])
        l[2] = line_3d(voxels[2], voxels[3])
        l[3] = line_3d(voxels[3], voxels[0])
        l[4] = line_3d(voxels[4], voxels[5])
        l[5] = line_3d(voxels[5], voxels[6])
        l[6] = line_3d(voxels[6], voxels[7])
        l[7] = line_3d(voxels[7], voxels[4])
        l[8] = line_3d(voxels[1], voxels[5])
        l[9] = line_3d(voxels[2], voxels[6])
        l[10] = line_3d(voxels[3], voxels[7])
        l[11] = line_3d(voxels[0], voxels[4])
        self.p = p = [tuple] * 6
        p[0] = (0, 1, 2, 3)
        p[1] = (7, 6, 5, 4)
        p[2] = (1, 5, 6, 2)
        p[3] = (0, 3, 7, 4)
        p[4] = (3, 2, 6, 7)
        p[5] = (0, 4, 5, 1)
        self.groundedge = ((0, 3), (3, 7), (7, 4), (4, 0))
        self.uv = grounduv = [tuple] * 8
        grounduv[0] = (1.0, 0.0)
        grounduv[3] = (0.0, 0.0)
        grounduv[7] = (0.0, 1.0)
        grounduv[4] = (1.0, 1.0)
        self.vcenter = self.voxels[-1]
        self.vectors = [tuple] * 8
        self.parent = superior
        self.index = index
        object_masks.append(None)
        object_maskimages.append(None)
        self.linecolor = linecolor

    def highlight_line(self):
        self.linecolor = hi_linecolor

    def normal_line(self):
        self.linecolor = linecolor

    def give_center_parent(self):
        return self.vcenter.get_transformed()

    def get_diagonals(self):
        for x, v in enumerate(self.voxels[:8]):
            x_rotated =  (v.x_rotated - self.vcenter.x_rotated) / sqrt_3
            y_rotated =  (v.y_rotated - self.vcenter.y_rotated) / sqrt_3
            z_rotated =  (v.z_rotated - self.vcenter.z_rotated) / sqrt_3
            if self.parent.GL_depth_cued:
                self.vectors[x] = (x_rotated, y_rotated, z_rotated)
            else:
                self.vectors[x] = (x_rotated, -y_rotated, -z_rotated)

    def print_voxels(self):
        voxels = []
        for v in self.v:
            voxel = voxel3d_o(v.getitem(), (0, 0, 0), 1.0, 0.5, None)
            voxels.append(voxel)
        return voxels

    def z_sort(self):
        for l in self.l:
            l.center_z()
        min_list = []
        lines = self.l
        values = []
        values = [(x.z_center, x) for x in lines]
        values.sort(key = lambda tup: tup[0])
        min_list = [val for (key, val) in values]
        return min_list

    def return_offset_vectors(self):
        C = self.voxels[7].get_transformed()
        X = self.voxels[4].get_transformed()
        Y = self.voxels[6].get_transformed()
        Z = self.voxels[3].get_transformed()
        vec_X = (array(X) - array(C)) / 2
        vec_Y = (array(Y) - array(C)) / 2
        vec_Z = (array(Z) - array(C)) / 2
        return (vec_X, vec_Y, vec_Z)

    def blit_shadow(self, depth):
        for p in self.p:
            P = []
            for i in p:
                coords = self.voxels[i].get_transformed()
                P.append(coords)
            planevector = self.parent.give_up_vector()
            Transformed = scan_object.projectpoints(P, lightdir, planevector)
            Projected = []
            for N, v in enumerate(Transformed):
                x_rotated = v[0]
                y_rotated = v[1]
                z_rotated = v[2]
                if depth == 0:
                    factor = scale
                else:
                    factor = scale - ((z_rotated + self.vcenter.z_pos) / depth)
                if(factor == 0):
                    factor = scale
                x = (x_rotated + self.vcenter.x_pos) / factor
                y = (y_rotated + self.vcenter.y_pos) / factor
                #
                w = screen.width
                h = screen.height
                if w > h:
                    w = h
                else:
                    h = w
                x = x * w / 2 + w / 2
                y = -y * h / 2 + h / 2
                Projected.append((x, y))

            if Projected:
                if screen.SDL_Mode:
                    if screen.texture != screen.Empty_texture:
                        glCallList(screen.Empty_texture)
                        screen.texture = screen.Empty_texture
                    glDisable(GL_DEPTH_TEST)
                    lights = glGetBooleanv(GL_LIGHTING)
                    if lights:
                        glDisable(GL_LIGHTING)
                    glNormal3fv((0.0, 1.0, 0.0))
                    glColor4fv(gl_shadowcolor)
                    glBegin(GL_QUADS)
                    for x, v in enumerate(Projected):
                        glVertex2f(float(v[0]), float(v[1]))
                    glEnd()
                    glEnable(GL_DEPTH_TEST)
                    if lights:
                        glEnable(GL_LIGHTING)
                else:
                    pygame.draw.polygon(screen.surface, shadowcolor, Projected, 0)

    def findlongest(self, coords):
        length2d = []
        for e in self.groundedge:
            (x0, y0, z0) = coords[e[0]]
            (x1, y1, z1) = coords[e[1]]
            l = sqrt((x1 - x0)**2 + (y1 - y0)**2)
            length2d.append(l)
        return length2d

    def draw_ground(self, depth, ground):
        if screen.SDL_Mode:
            glDisable(GL_DEPTH_TEST)
            if ground is None:
                glCallList(screen.Ground_texture)
            else:
                glCallList(ground)

            coords = {}
            for v in self.p[3]:
                coords[v] = self.voxels[v].blit_line(depth)
            groundedges = self.groundedge * 2

            length2d = self.findlongest(coords)
            if length2d[0] > length2d[2]:
                longestedge = groundedges[0]
                oppositeedge = groundedges[2]
                difference = 1 - (length2d[2] / length2d[0])
            else:
                longestedge = groundedges[2]
                oppositeedge = groundedges[0]
                difference = 1 - (length2d[0] / length2d[2])

            if length2d[1] > length2d[3]:
                longestedge_1 = groundedges[1]
                oppositeedge_1 = groundedges[3]
                difference_1 = 1 - (length2d[3] / length2d[1])
            else:
                longestedge_1 = groundedges[3]
                oppositeedge_1 = groundedges[1]
                difference_1 = 1 - (length2d[1] / length2d[3])

            uv = self.uv[:]

            idx0 = oppositeedge[0]
            idx1 = oppositeedge[1]
            v0 = uv[idx1][0] - uv[idx0][0]
            v1 = uv[idx1][1] - uv[idx0][1]
            vectoruv = (v0, v1)
            offset = (uv[idx1][0] - (vectoruv[0] * difference), uv[idx1][1] - (vectoruv[1] * difference))
            uv[idx1] = offset

            idx0_1 = oppositeedge_1[1]
            idx1_1 = oppositeedge_1[0]
            v0 = uv[idx1_1][0] - uv[idx0_1][0]
            v1 = uv[idx1_1][1] - uv[idx0_1][1]
            vectoruv = (v0, v1)
            offset = (uv[idx1_1][0] - (vectoruv[0] * difference_1), uv[idx1_1][1] - (vectoruv[1] * difference_1))
            uv[idx1_1] = offset


##            vector_1 = (coords[3][0] - coords[7][0], coords[3][1] - coords[7][1])
##            vector_2 = (coords[4][0] - coords[7][0], coords[4][1] - coords[7][1])
##            diagonal = (vector_2[0] + vector_1[0], vector_2[1] + vector_1[1])
##            length_diagonal = sqrt(diagonal[0]**2 + diagonal[1]**2)
##            diagonal3d = (coords[0][0] - coords[7][0], coords[0][1] - coords[7][1])
##            length_diagonal3d = sqrt(diagonal3d[0]**2 + diagonal3d[1]**2)
##            ratio_amount = length_diagonal / length_diagonal3d
##
##            vector_uv = (1.0, -1.0)
##            uv[0] = (vector_uv[0] / ratio_amount, vector_uv[1] / ratio_amount + 1.0)

            glBegin(GL_QUADS)
            glColor4fv(gl_groundcolor)
            glNormal3fv((0.0, 1.0, 0.0))
            for v in self.p[3]:
                glTexCoord2f(uv[v][0], uv[v][1])
                glVertex2f(float(coords[v][0]), float(coords[v][1]))
            glEnd()
            glEnable(GL_DEPTH_TEST)
            glCallList(screen.Empty_texture)
            screen.texture = screen.Empty_texture
        else:
            pointlist = []
            for v in self.p[3]:
                (x0, y0, z0) = self.voxels[v].blit_line(depth)
                p = (x0, y0)
                pointlist.append(p)
            pygame.draw.polygon(screen.surface, groundcolor, pointlist, 0)
        if self.index:
            screen.alpha.fill(alpha_clear)
            pointlist = []
            for v in self.p[3]:
                (x0, y0, z0) = self.voxels[v].blit_line(depth)
                p = (x0, y0)
                pointlist.append(p)
            pygame.draw.polygon(screen.alpha, alphaline, pointlist, 0)

            alpha = pygame.surfarray.pixels_alpha(screen.alpha)
            alpha = alpha.transpose()
            A = Image.fromarray(alpha)
            alpha3 = alpha.view(uint8)
            alpha3[:] = divide(alpha3, 128)
            object_masks[-self.index] = alpha3

            alpha1 = multiply(alpha, 255)
            alpha2 = alpha1.astype(uint8)
            img1 = Image.fromarray(alpha2)
            object_maskimages[-self.index] = img1
            size = screen.alpha.get_size()
            screen.pixelmap_picking.paste(-self.index, (0, 0), (size[1], size[0]), self.index - 1, self.index)

    def blit_line(self, depth):
        L = self.z_sort()
        if screen.SDL_Mode:
            if screen.texture != screen.Empty_texture:
                glCallList(screen.Empty_texture)
                screen.texture = screen.Empty_texture
            lights = glGetBooleanv(GL_LIGHTING)
            if lights:
                glDisable(GL_LIGHTING)
            glBegin(GL_LINES)
            for x, l in enumerate(L):
                glColor3fv((float(self.linecolor[x][0]/255.0),
                            float(self.linecolor[x][1]/255.0),
                            float(self.linecolor[x][2]/255.0)))
                (x0, y0, z0) = l[0].blit_line(depth)
                (x1, y1, z1) = l[1].blit_line(depth)
                glVertex3f(float(x0), float(y0), -float(z0))
                glVertex3f(float(x1), float(y1), -float(z1))
            glEnd()
            if lights:
                glEnable(GL_LIGHTING)
        else:
            for x, l in enumerate(L):
                (x0, y0, z0) = l[0].blit_line(depth)
                (x1, y1, z1) = l[1].blit_line(depth)
                pygame.draw.line(screen.surface, self.linecolor[x], (x0, y0), (x1, y1), linewidth)

        if self.index:
            screen.alpha.fill(alpha_clear)
            for x, l in enumerate(L):
                (x0, y0, z0) = l[0].blit_line(depth)
                (x1, y1, z1) = l[1].blit_line(depth)
                pygame.draw.line(screen.alpha, alphaline, (x0, y0), (x1, y1), alphalinewidth)

            alpha = pygame.surfarray.pixels_alpha(screen.alpha)
            alpha = alpha.transpose()
            A = Image.fromarray(alpha)
            alpha3 = alpha.view(uint8)
            alpha3[:] = divide(alpha3, 128)
            object_masks[-self.index] = alpha3

            alpha1 = multiply(alpha, 255)
            alpha2 = alpha1.astype(uint8)
            img1 = Image.fromarray(alpha2)
            object_maskimages[-self.index] = img1
            size = screen.alpha.get_size()
            screen.pixelmap_picking.paste(-self.index, (0, 0), (size[1], size[0]), self.index - 1, self.index)

class picking():
    def __init__(self, w, h, t):
        self.w = h
        self.h = w
        self.pic = zeros((self.w, self.h), dtype = t)
        #self.pic = self.pic.astype(t)
        self.img = Image.fromarray(self.pic)
        self.t = t

    def init_pic(self):
        self.img.paste(0, (0, 0, self.w, self.h))

    def get_array(self):
        l = self.img.getdata()
        l = array(l).reshape(self.w, self.h)
        l = transpose(l)
        return l

    def paste(self, s, coord, size, index, i):
        if index < -1:
            #paste cube3d
            mask = object_masks[s]
            maskimage = object_maskimages[s]
        else:
            mask = masks[s]
            maskimage = maskimages[s]
        x0 = int(coord[0])
        y0 = int(coord[1])
        try:
            blank = zeros(size, dtype = self.t)
            blank.fill(index + 1)
            mask = multiply(mask, blank)
            img1 = Image.fromarray(mask)
            self.img.paste(img1, (x0, y0), maskimage)
        except:
            return

        """
        if i > 63:
            print
            print(mask)
            s = mask.shape
            for x in range(s[0])[::10]:
                C = ""
                for y in range(s[1])[::10]:
                    p = mask[y, x] - 1
                    C += str(p) + " "
                print(C)
            l = self.get_array()
            s = l.shape
            for x in range(s[0])[::20]:
                C = ""
                for y in range(s[1])[::20]:
                    p = l[y, x] - 1
                    C += str(p) + " "
                print(C)
        #mask = mask.astype(self.t)
        """

class Coordinates_3d():
    def __init__(self, position = (0.0, 0.0, 0.0)):
        self.x = float(position[0])
        self.y = float(position[1])
        self.z = float(position[2])

    def __getitem__(self, index):
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        if index == 2:
            return self.z

    def getitem(self):
        return (self.x, self.y, self.z)

class rect_3d():
    def __init__(self, rect = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)):
        self.max = Coordinates_3d()
        self.min = Coordinates_3d()
        self.center = Coordinates_3d()
        self.max.x = rect[0]
        self.max.y = rect[1]
        self.max.z = rect[2]
        self.min.x = rect[3]
        self.min.y = rect[4]
        self.min.z = rect[5]
        self.state = False

    def give_center(self):
        self.center.x = (self.min.x + self.max.x) / 2
        self.center.y = (self.min.y + self.max.y) / 2
        self.center.z = (self.min.z + self.max.z) / 2
        return self.center

    def return_tuple(self):
        return (self.max.x, self.max.y, self.max.z, self.min.x, self.min.y, self.min.z)

T = Transformer()
#T.__init__()
T.name = "world"
T.LOCAL = True

class object3d(threading.Thread, Transformer):

    def __init__(self, voxels = [], a = 0, v = (0, 1, 0),
                 position = (0, 0, 0), name = "", parent = None,
                 pic_index = None, images = None, image = None,
                 OBJ_repro = None, repro = None, texName = None):
        threading.Thread.__init__(self)
        Transformer.__init__(self, name = name, index = pic_index)
        self.voxels = voxels
        self.propagate = False
        self.images = images
        self.image = image
        self.OBJ_repro = OBJ_repro
        self.Frames = 0
        self.repro = repro
        self.texture = None
        self.texName = texName
        self.angle = a
        self.previousangle = a
        self.backupangle = 0.0
        self.previouslocal = (0, 1, 0)
        self.up_vector = (0, 1, 0)
        self.vector = v
        self.local = v
        self.direction = rotation_amount
        self.create_picmap = True
        self.position = (0, 0, 0)
        self.conform_position = array(list(position), dtype = float32)
        self.local_position = array([0, 0, 0], dtype = float32)
        self.local_conform = array([0, 0, 0], dtype = float32)
        self.center = array([0, 0, 0], dtype = float32)
        self.center = self.give_center()
        self.oldcenter = None
        self.collected = []
        self.highlighted = 0
        self.highlight_color = array([255, 255, 0], int)
        self.get_highlight(0)
        self.rect = rect_3d()
        self.animated_Cube = arange(dim**3).reshape(dim, dim, dim)
        self.animated_Cube_filled = 0
        self.voxelLimit = voxel_limit
        self.levelLimit = levelLimit
        self.name = name
        self.neighbours = [[]]
        self.draw_Cube = True
        self.draft_Mode = False
        self.draw_Ground = True
        self.Depth = 5.0
        self.GL_depth_cued = False
        self.vec_x = (1, 0, 0)
        self.vec_y = (0, 1, 0)
        self.vec_z = (0, 0, 1)
        self.parent = T

        #self.Voxels = {}
        self.visibility_array = {}
        self.color_array = {}
        self.vector_array = {}
        self.size_array = {}
        self.index_array = {}
        self.coords_array = {}
        self.baked_array = {}
        self.rotated_array = {}
        self.Size_Array = {}
        self.Color_Array = {}
        self.Vector_Array = {}

        self.cube = cube_3d(self, 1, "cube", self.index)
        self.cube3d = cube_3d(self.cube, 0.8, "cube_3d", None)
        self.put_child_nodes([self.cube, self.cube3d])
        self.collect_voxels()

        self.falloff = 0

        self.move_to_conform(self.conform_position)

        self.smoothColors_original = None
        self.smoothSizes_original = None
        self.smoothColors_smoothed = None
        self.smoothSizes_smoothed = None
        self.dimension = 1
        self.Mask = [False]
        self.add_mask = array([True])
        self.sub_mask = array([False])

        self.groundImage = image_folder + ground_image
        self.ground = None

        self.start()

    def get_size_array(self, dim):
        if dim in self.size_array:
            return self.size_array[dim]
        else:
            return None

    def get_color_array(self, dim):
        if dim in self.color_array:
            return self.color_array[dim]
        else:
            return None

    def __getitem__(self, i):
        if i >= 0 and i < len(self.voxels):
            return self.voxels[i]
        else:
            return self.voxels[0]

    def get_direction(self):
        return self.direction

    def get_position(self):
        return self.position

    def get_local_position(self):
        return self.local_position

    def get_local_conform(self):
        return self.local_conform

    def get_voxels(self):
        return self.voxels

    def get_center(self):
##        if self.LOCAL:
##            center = self.cube.give_center_parent()
##        else:
##            center = self.center
        return self.center

    def get_conform_position(self):
        return self.conform_position

    def get_highlighted(self):
        return self.highlighted

    def get_highlight_color(self):
        return self.highlight_color

    def get_collected(self):
        return self.collected

    def get_rect(self):
        return self.rect

    def get_animated_Cube(self):
        return self.animated_Cube

    def get_voxelLimit(self):
        return self.voxelLimit

    def get_levelLimit(self):
        return self.levelLimit

    def get_name(self):
        return self.name

    def get_neighbours(self):
        return self.neighbours

    def get_cube(self):
        return self.cube

    def get_cube3d(self):
        return self.cube3d

    def get_draw_Cube(self):
        return self.draw_Cube

    def get_parent(self):
        return self.parent

    def get_falloff(self):
        return self.falloff

    def get_image(self):
        return self.image

    def get_OBJ_repro(self):
        return self.OBJ_repro

    def get_Frames(self):
        return self.Frames

    def get_repro(self):
        return self.repro

    def get_texName(self):
        return self.texName

    def get_texture(self):
        return self.texture

    def get_groundImage(self):
        return self.groundImage

    def get_local_vector(self):
        return self.local

    def get_ground(self):
        return self.groundImage

    def get_draw_Ground(self):
        return self.draw_Ground

    def print_array(self):
        dim = self.get_dimension()
        print(fliplr(self.visibility_array[dim].transpose(2, 1, 0)))
        print(fliplr(self.color_array[dim].reshape(dim, dim, dim, 3).transpose(2, 1, 0, 3)))
        print(fliplr(self.size_array[dim].reshape(dim, dim, dim, 1).transpose(2, 1, 0, 3)))

    def get_dimension(self):
        if self.highlighted >= len(self.voxels):
            self.get_highlight(0)
        level = self.voxels[self.highlighted].level
        dim = int(1 / float(level))
        return dim

    def get_minor_dimension(self):
        level = self.get_minor_level()
        dim = int(1 / float(level))
        return dim

    def get_minor_level(self):
        voxels = self.return_voxel_hierarchy()
        return voxels[-1].level

    def renumber_invisible(self):
        voxels = self.return_voxel_hierarchy()
        Voxels = set(self.voxels)
        currency = len(self.voxels)
        for i in voxels:
            if i not in Voxels:
                i.currency = currency
                currency += 1

    def get_dimensions(self):
        levels = []
        dimensions = []
        voxels = self.return_voxel_hierarchy()
        for i in voxels:
            level = i.level
            if level not in levels:
                dim = int(1 / float(level))
                levels.append(level)
                dimensions.append(dim)
        return dimensions

    def get_object_data(self, minor = True):
        A = self.local_conform
        B = self.conform_position
        C = self.local_position
        D = self.angle
        E = self.local
        F = self.LOCAL
        if minor:
            G = self.get_minor_dimension()
        else:
            G = self.get_dimension()
        H = self.direction
        I = self.groundImage
        J = self.draw_Ground
        return (A, B, C, D, E, F, G, H, I, J)

    def select_by_VoxelDim(self, Dim, Voxel):
        level = 1.0 / float(Dim)
        voxels = set(self.get_levelVoxels(level))
        for i in voxels:
            if i.Currency == Voxel:
                self.get_highlight(i.currency)
                return True
        return False

    def set_highlighted(self, level):
        for x, i in enumerate(self.voxels):
            if i.level == level and not i.spawned:
                self.get_highlight(x)
                break

    def set_draw_ground(self, ground_Mode):
        self.draw_Ground = ground_Mode

    def reset_Oscillate(self):
        voxels = set(self.voxels)
        for i in voxels:
            i.Oscillate = abs(i.Oscillate)

    def return_Pos_And_Scale(self):
        if self.OBJ_repro:
            return self.OBJ_repro.return_Pos_And_Scale()
        else:
            return (0, 0, 1.0, 1.0, 1.0)

    def return_Wire_Render(self):
        if self.OBJ_repro:
            return self.OBJ_repro.return_Wire_Render()
        else:
            return (0, 1)

    def select_Level(self, dim):
        Dim = self.get_dimension()
        level = 1.0 / float(dim)
        candidate = None
        if Dim != dim:
            for i in set(self.voxels):
                if i.get_visibility() and i.level == level:
                    candidate = i.currency
                    break
        else:
            return True
        if candidate is not None:
            #self.get_highlight(candidate)
            return True
        else:
            return False

    def select_visible_level(self):
        self.collected = []
        highlighted = self.highlighted
        notFound = True
        while notFound:
            voxel = self.voxels[highlighted]
            parent = voxel.parent
            if parent is None:
                return
            level = parent.level
            found = False
            for i in set(self.voxels):
                if i.level == level:
                    if i.spawned == False:
                        found = True
                        highlighted = i.currency
                        break
            if not found:
                notFound = False
        if highlighted != self.highlighted:
            self.get_highlight(highlighted)

    def return_levelVoxels_Indexes(self, voxel = None):
        if voxel is None:
            voxel = self.highlighted
        level = self.voxels[voxel].level
        voxels = []
        if self.collected:
            collected = self.collected
        else:
            collected = self.voxels
        for i in set(collected):
            if i.level == level:
                voxels.append(i.currency)
        return voxels

    def return_levelVoxels(self, voxel = None):
        if voxel is None:
            voxel = self.highlighted
        level = self.voxels[voxel].level
        voxels = []
        if self.collected:
            collected = self.collected
        else:
            collected = self.voxels
        for i in set(collected):
            if i.level == level:
                voxels.append(i)
        return voxels

    def set_object_data(self, data):
        self.local_conform      = data[0]
        self.conform_position   = data[1]
        self.local_position     = data[2]
        self.angle              = data[3]
        self.local              = data[4]
        try:
            self.direction          = data[5]
        except:
            pass
        try:
            self.groundImage        = data[6]
        except:
            pass
        try:
            self.draw_Ground         = data[7]
        except:
            pass

    def spawn_to_voxels(self, data, init = True):
        zippedList = {}
        for superiors in data:
            for voxels in superiors[1]:
                key = voxels[0]
                try:
                    value = voxels[1]
                    zippedList[key] = bool(value)
                except:
                    pass

        current_voxel = self.get_biggest_pixel()
        biggest_pixel = self.voxels[current_voxel]
        voxels = biggest_pixel.voxels
        if zippedList and (0.0, 0.0, 0.0) in zippedList:
            if zippedList[(0.0, 0.0, 0.0)]:
                biggest_pixel.spawn_sub_voxels(init = init)

        if type(voxels) is not list:
            voxels = []

        conform = self.conform_position + self.local_conform

        def apply_data(superior, voxels):
            for i in voxels:
                pos = i.get_unchanged(conform)
                if zippedList and pos in zippedList:
                    if zippedList[pos]:
                        i.spawn_sub_voxels(init = init)
                if i.voxels:
                    apply_data(i, i.voxels)

        apply_data(biggest_pixel, voxels)

        self.validate_voxels()

    def apply_to_voxels(self, images, spins, spin_amounts, frame, spawned, data,
                        color, size,
                        random_rot, RotCombine, ImageCombo, visible = False,
                        progress = False, advance = False):

        Images = []
        for i in images:
            img = validate_filename(i)
            Images.append(img)
        images = Images

        imageList = {}
        spinList = {}
        spinAmount = {}
        frameList = {}
        spawnedList = {}
        colorList = {}
        sizeList = {}
        zippedList = {}

        for superiors in data:
            for voxels in superiors[1]:
                key = voxels[0]
                value = voxels[1]
                imageList[key] = images[value]

                value = voxels[2]
                spinList[key] = spins[value]

                value = voxels[3]
                spinAmount[key] = spin_amounts[value]

                value = voxels[4]
                frameList[key] = frame[value]

                if spawned:
                    value = voxels[5]
                    spawnedList[key] = spawned[value]

                if color:
                    value = voxels[6]
                    colorList[key] = color[value]

                if size:
                    value = voxels[7]
                    sizeList[key] = size[value]

                try:
                    value = voxels[8]
                    zippedList[key] = bool(value)
                except:
                    pass

        current_voxel = self.get_biggest_pixel()
        biggest_pixel = self.voxels[current_voxel]
        voxels = biggest_pixel.voxels
        if spawnedList and spawned[0]:
            biggest_pixel.spawn_sub_voxels()
            voxels = biggest_pixel.voxels
        if zippedList and (0.0, 0.0, 0.0) in zippedList:
            biggest_pixel.zipped = zippedList[(0.0, 0.0, 0.0)]

        if type(voxels) is not list:
            voxels = []

        conform = self.conform_position + self.local_conform

        voxelList = [biggest_pixel,]
        biggest_pixel.image = images[0]
        biggest_pixel.spin = spins[0]
        biggest_pixel.spin_amount = spin_amounts[0]
        biggest_pixel.frame = frame[0]

        if colorList:
            biggest_pixel.color[:] = color[0][:]
        if sizeList:
            biggest_pixel.size[:] = size[0]

        Voxels = set(self.voxels)

        def apply_data(superior, voxels):
            for i in voxels:
                if visible:
                    if i not in Voxels:
                        continue
                pos = i.get_unchanged(conform)
                if pos in imageList:
                    i.image = imageList[pos]
                    i.spin = spinList[pos]
                    i.spin_amount = spinAmount[pos]
                    i.frame = frameList[pos]
                    if colorList and pos in colorList:
                        i.color[:] = colorList[pos][:]
                    if sizeList and pos in sizeList:
                        i.size[:] = sizeList[pos]
                    voxelList.append(i)
                if spawnedList and pos in spawnedList:
                    if spawnedList[pos]:
                        i.spawn_sub_voxels()
                if zippedList and pos in zippedList:
                    i.zipped = zippedList[pos]
                if i.voxels:
                    apply_data(i, i.voxels)

        apply_data(biggest_pixel, voxels)

        self.validate_voxels()

        for i in images:
            if progress:
                try:
                    if advance:
                        progress.advance("images\n")
                    progress.set_msg1(str(i))
                except(Exception) as detail:
                    print(detail)
                    return
            if i is not None:
                init_images(i, random_rot, RotCombine, ImageCombo)
                for j in voxelList:
                    if j.image == i:
                        j.set_images()

    def apply_to_voxels_repro(self, repros, textures, Frames, Pos_And_Scale, Wire_Frame, data,
                              useLoaded = True,
                              progress = False,
                              advance = False):
        print("apply_to_voxels_repro")

        Repros = []
        for i in repros:
            r = validate_filename(i)
            Repros.append(r)
        repros = Repros

        Textures = []
        for i in textures:
            t = validate_filename(i)
            Textures.append(t)
        textures = Textures

        Oscillate = [0, 1, -1]

        reproList = {}
        textureList = {}
        FramesList = {}
        OscList = {}

        textuFrames = {}
        reproFrames = {}

        for superiors in data:
            for voxels in superiors[1]:
                key = voxels[0]
                value = voxels[1]
                reproList[key] = repros[value]

                value = voxels[2]
                textureList[key] = textures[value]

                value = voxels[3]
                FramesList[key] = Frames[value]

                try:
                    value = voxels[4]
                    OscList[key] = Oscillate[value]
                except:
                    pass

        current_voxel = self.get_biggest_pixel()
        biggest_pixel = self.voxels[current_voxel]
        voxels = biggest_pixel.voxels
        if type(voxels) is not list:
            voxels = []

        conform = self.conform_position + self.local_conform

        voxelList = [biggest_pixel,]
        biggest_pixel.repro = repros[0]
        biggest_pixel.texName = textures[0]
        biggest_pixel.Frames = Frames[0]

        try:
            biggest_pixel.Oscillate = OscList[(0.0, 0.0, 0.0)]
        except(Exception) as detail:
            print("Oscillate", detail)
            pass

        textuFrames[textures[0]] = textures[0]
        reproFrames[repros[0]] = Frames[0]

        def apply_rep(superior, voxels):
            for i in voxels:
                pos = i.get_unchanged(conform)
                if pos in reproList:
                    i.repro = reproList[pos]
                    i.texName = textureList[pos]
                    i.Frames = FramesList[pos]
                    textuFrames[i.texName] = None
                    reproFrames[i.repro] = i.Frames
                    voxelList.append(i)
                if pos in OscList:
                    i.Oscillate = OscList[pos]
                if i.voxels:
                    apply_rep(i, i.voxels)

        apply_rep(biggest_pixel, voxels)

        for i in textures:
            if progress:
                try:
                    if advance:
                        progress.advance("textures\n")
                    progress.set_msg1(str(i))
                except(Exception) as detail:
                    print(detail)
                    return
            if i is not None:
                if i in textuFrames:
                    if screen.SDL_Mode:
                        (texture, texName) = load_object_texture(i, useLoaded)
                    else:
                        texture = None
                    for j in voxelList:
                        if j.texName == i:
                            if texture:
                                j.set_texture(texture, i)

        PS = iter(Pos_And_Scale)
        if Wire_Frame:
            WO = iter(Wire_Frame)

        print(Frames)
        for i in repros:
            p = next(PS)
            if Wire_Frame:
                t = next(WO)
            else:
                t = (False, True)
            print("1 Pos_And_Scale", i, p)
            if progress:
                try:
                    if advance:
                        progress.advance("repros\n")
                    progress.set_msg1(str(i))
                except(Exception) as detail:
                    print(detail)
                    return
            if i is not None:
                if i in reproFrames:
                    f = reproFrames[i]
                    if screen.SDL_Mode:
                        OBJ_repro = load_object_repro(i, f, p, t, progress, useLoaded)
                    else:
                        OBJ_repro = None
                    for j in voxelList:
                        if j.repro == i:
                            j.set_repro(i, OBJ_repro)

    def print_invisible_voxels(self):
        voxels = self.return_voxel_hierarchy()
        deleted = []
        for i in voxels:
            if i.voxels and not i.spawned:
                deleted.append(i.currency)
        print("deleted", deleted)

    def return_voxel_hierarchy(self):
        current_voxel = self.get_biggest_pixel()
        biggest_pixel = self.voxels[current_voxel]
        voxels = biggest_pixel.voxels
        if type(voxels) is not list:
            voxels = []

        voxelList = [biggest_pixel,]
        IndexList = [biggest_pixel.currency,]

        def apply_vox(superior, voxels):
            for i in voxels:
                voxelList.append(i)
                IndexList.append(i.currency)
                if i.voxels:
                    apply_vox(i, i.voxels)

        apply_vox(biggest_pixel, voxels)
        #print(IndexList)
        return voxelList

    def find_smallest_voxel(self):
        voxels = set(self.voxels)
        level = 1.0
        for i in voxels:
            if i.level < level:
                level = i.level
        return level

    def delete_invisible_arrays(self):
        level = self.find_smallest_voxel()
        Dim = int(1.0 / level)
        for dim in self.visibility_array.keys():
            S = sum(self.visibility_array[dim])
            if dim > Dim and not S:
                print("delete invisible array", dim, S)
                del self.visibility_array[dim]
                del self.color_array[dim]
                del self.vector_array[dim]
                del self.size_array[dim]
                del self.index_array[dim]
                del self.coords_array[dim]
                del self.baked_array[dim]
                del self.rotated_array[dim]
                del self.Size_Array[dim]
                del self.Color_Array[dim]
                del self.Vector_Array[dim]

    def delete_voxels_below(self):
        level = 1.0
        voxels = self.return_voxel_hierarchy()
        Voxels = set(self.voxels)
        for i in reversed(voxels):
            if i.level < level and i not in Voxels:
                i.parent.zipped = False
                i.parent.voxels = None
                del(i)

    def cleanup(self):
        self.OBJ_repro = None
        self.repro = None
        self.texture = None
        self.texName = None
        self.Frames = 0
        voxels = self.return_voxel_hierarchy()
        for i in voxels:
            i.image = None
            i.images = None
            i.repro = None
            i.OBJ_repro = None
            i.texName = None
            i.texture = None
            i.Frames = 0

    def set_spin_random(self, random_amount, voxels):
        if not voxels:
            if self.collected:
                voxels = self.collected
            else:
                voxels = set(self.voxels)
        for i in voxels:
            spin = rad2deg(i.spin)
            spin = random.randint(int(spin - random_amount), int(spin + random_amount))
            i.spin = deg2rad(spin)

    def set_spin(self, spin, voxels = None):
        if not voxels:
            if self.collected:
                voxels = self.collected
            else:
                voxels = set(self.voxels)
        for i in voxels:
            i.spin = spin

    def set_spin_amount(self, spin_amount, voxels = None):
        if not voxels:
            if self.collected:
                voxels = self.collected
            else:
                voxels = set(self.voxels)
        for i in voxels:
            i.spin_amount = spin_amount

    def set_spin_amount_random(self, voxels = None):
        if not voxels:
            if self.collected:
                voxels = self.collected
            else:
                voxels = set(self.voxels)
        d = [-1.0, 1.0]
        for i in voxels:
            m = random.randint(0, 1)
            i.spin_amount *= d[m]

    def selectSameLevel(self):
        level = self.voxels[self.highlighted].level
        self.collected = []
        for i in set(self.voxels):
            if i.level == level:
                self.collected.append(i)
        self.clear_illumination()
        self.highlight_collection()

    def selectSameTexture(self):
        Tex = self.voxels[self.highlighted].texture
        self.collected = []
        for i in set(self.voxels):
            if i.texture == Tex:
                self.collected.append(i)
        self.clear_illumination()
        self.highlight_collection()

    def selectSameOBJ(self):
        OBJ = self.voxels[self.highlighted].OBJ_repro
        self.collected = []
        for i in set(self.voxels):
            if i.OBJ_repro == OBJ:
                self.collected.append(i)
        self.clear_illumination()
        self.highlight_collection()

    def selectHighlighted(self):
        self.collected = [self.voxels[self.highlighted],]
        self.clear_illumination()
        self.highlight_collection()

    def selectSameImage(self):
        Img = self.voxels[self.highlighted].images
        self.collected = []
        for i in set(self.voxels):
            if i.images == Img:
                self.collected.append(i)
        self.clear_illumination()
        self.highlight_collection()

    def make_unique(self):
        self.voxels = list(set(self.voxels))
        self.validate_voxels()
        if self.highlighted >= len(set(self.voxels)):
            self.highlighted = len(set(self.voxels)) - 1

    def toggle_propagate(self):
        self.propagate = not self.propagate

    def toggle_draft_Mode(self):
        self.draft_Mode = not self.draft_Mode

    def toggle_draw_Cube(self):
        self.draw_Cube = not self.draw_Cube

    def toggle_GL_depth_cued(self):
        self.GL_depth_cued = not self.GL_depth_cued

    def select_array(self, t, v, level, c, collection = False):
        s = self.animated_Cube.shape
        print(t, v, level)
        S = s[0]**3
        l = 1.0 / s[0]
        print(l)
        L = len(self.voxels)
        if collection:
            voxels = self.collected
        else:
            if v < len(self.voxels):
                voxels = [self.voxels[v],]
            else:
                voxels = [self.voxels[-1],]
        if level == l:
            a = []
            for i in voxels:
                v = i.currency
                if v < S:
                    h = unravel_index(v, s)

                    X = range(h[0], h[0] + 1)
                    Y = range(h[1], h[1] + 1)
                    Z = range(h[2], h[2] + 1)

                    if t[0]:
                        X = range(0, s[0])
                        if c == 1:
                            X = range(h[0], s[0])
                        elif c == 2:
                            X = range(0, h[0] + 1)
                    if t[1]:
                        Y = range(0, s[0])
                        if c == 1:
                            Y = range(h[1], s[0])
                        elif c == 2:
                            Y = range(0, h[1] + 1)
                    if t[2]:
                        Z = range(0, s[0])
                        if c == 1:
                            Z = range(h[2], s[0])
                        elif c == 2:
                            Z = range(0, h[2] + 1)

                    slic = self.animated_Cube[X[0]:X[-1] + 1, Y[0]:Y[-1] + 1, Z[0]:Z[-1] + 1]
                    Slic = slic.flatten()
                    for i in Slic:
                        if i < L:
                            voxel = self.voxels[i]
                            if voxel.level == level:
                                a.append(voxel)
            a = set(a)
            d = set(self.voxels)
            for i in self.collected:
                i.clear_illumination()
            b = d - a
            self.collected = list(d - b)
            for i in self.collected:
                i.set_illumination()

    def select_child_voxels(self, append = False):
        voxel = self.voxels[self.highlighted]
        if voxel.spawned:
            voxels = [voxel,]
        elif self.collected:
            voxels = self.collected
        else:
            voxels = [voxel,]
        if not append:
            self.clear_collected()
        for i in voxels:
            if i.voxels:
                self.collected += i.voxels
        self.collected[:] = set(self.collected)
        self.highlight_collection()

    def set_voxel_color(self, voxel = None, color = (0, 0, 0), mix = 255, falloff = 0):
        print("mix", mix)
        if self.neighbours != [[]]:
            if self.collected:
                self.clear_collected()
            if falloff == 0:
                voxels = self.neighbours[0]
                for i in voxels:
                    (m, n) = self.func_0_1(255, mix)
                    c = array(color).astype(float) * m + array(i.illu_color).astype(float) * n
                    i.set_color(c.astype(int))
            else:
                self.affect_neighbours(color = color, falloff = falloff)
        else:
            voxels = []
            if self.collected:
                voxels = self.collected
                print("set_voxel_color")
                for i in voxels:
                    (m, n) = self.func_0_1(255, mix)
                    c = array(color).astype(float) * m + array(i.illu_color).astype(float) * n
                    i.set_color(c.astype(int))
                self.clear_collected()
            else:
                voxels = [self.voxels[voxel],]
                self.remove_highlight()
                for i in voxels:
                    (m, n) = self.func_0_1(255, mix)
                    c = array(color).astype(float) * m + array(i.color).astype(float) * n
                    i.set_color(c.astype(int))

    def affect_neighbours(self, scale = False, voxel = None, color = None, falloff = 1):
        step = 1.0 / float(falloff)
        if voxel == None:
            voxel = self.highlighted
        v = self.voxels[voxel]
        a = v.coords
        radius = v.level * falloff * float(2) + v.level * 2.0
        print("affect_neighbours")
        for i in self.neighbours:
            for j in i:
                b = j.coords
                c = b - a
                l = sqrt(c.dot(c)) + j.level
                (m, n) = self.func_0_1(radius, l)
                if scale != False:
                    j.size[:] = (j.level * n) + ((j.level * scale / 4.0) * ((l + radius) / radius) * m)
                elif color:
                    j.mix_color(color, m, n)

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

    def select_neighbours_by_cube(self, layers, voxel):
        self.falloff = layers
        if layers == 0:
            if self.collected:
                self.neighbours = [set(self.collected)]
                self.clear_collected()
            else:
                self.neighbours = [[]]
            return
        if voxel == None:
            voxels = self.collected
        else:
            voxels = [self.voxels[voxel],]

        s = self.animated_Cube.shape
        l = 1.0 / s[0]
        X = []
        Y = []
        Z = []
        for i in voxels:
            c = i.currency
            try:
                h = unravel_index(c, s)
            except:
                continue
            X += range(h[0] - layers, h[0] + layers + 1)
            Y += range(h[1] - layers, h[1] + layers + 1)
            Z += range(h[2] - layers, h[2] + layers + 1)

        X = set(X)
        Y = set(Y)
        Z = set(Z)

        flag_X = False
        flag_Y = False
        flag_Z = False

        a = []
        for x in range(s[0]):
            if x in X:
                flag_x = True
            else:
                flag_x = False
            for y in range(s[1]):
                if y in Y:
                    flag_y = True
                else:
                    flag_y = False
                for z in range(s[2]):
                    if z in Z:
                        flag_z = True
                    else:
                        flag_z = False
                    if flag_x and flag_y and flag_z:
                        i = self.animated_Cube[x, y, z]
                        v = self.voxels[i]
                        if v.level == l:
                            a.append(v)
        self.neighbours = [set(a)]

        if self.collected != []:
            self.clear_collected()

    def smooth_Colors(self, dimension, m, M):
        R = ma.masked_array(self.color_array[dimension][:, 0], mask = m)
        G = ma.masked_array(self.color_array[dimension][:, 1], mask = m)
        B = ma.masked_array(self.color_array[dimension][:, 2], mask = m)
        r = R.mean()
        g = G.mean()
        b = B.mean()
        self.color_array[dimension][M, 0] = int(r)
        self.color_array[dimension][M, 1] = int(g)
        self.color_array[dimension][M, 2] = int(b)

    def smooth_Sizes(self, dimension, m, M):
        S = ma.masked_array(self.size_array[dimension], mask = m)
        s = S.mean()
        self.size_array[dimension][M] = s

    def setup_Smooth_Arrays_fade(self, smoothColors, smoothSizes):
        level = self.voxels[self.highlighted].level
        dimension = int(1.0 / level)
        self.dimension = dimension
        if dimension in self.visibility_array:
            m = logical_not(self.visibility_array[dimension].flatten())
            M = logical_not(m)

            self.Mask = M

        if smoothColors and dimension in self.color_array:
            if self.collected:
                self.clear_illumination()
            self.smoothColors_original = self.color_array[dimension][self.Mask]
            self.smooth_Colors(dimension, m, M)
            self.smoothColors_smoothed = self.color_array[dimension][self.Mask]
        else:
            self.smoothColors_original = None
            self.smoothColors_smoothed = None
        if smoothSizes and dimension in self.size_array:
            self.smoothSizes_original = self.size_array[dimension][self.Mask]
            self.smooth_Sizes(dimension, m, M)
            self.smoothSizes_smoothed = self.size_array[dimension][self.Mask]
        else:
            self.smoothSizes_original = None
            self.smoothSizes_smoothed = None

    def setup_Smooth_Arrays(self, smoothColors, smoothSizes):
        level = self.voxels[self.highlighted].level
        dimension = int(1.0 / level)
        self.dimension = dimension
        if smoothColors and dimension in self.color_array:
            if self.collected:
                self.clear_illumination()
            self.smoothColors_original = self.color_array[dimension].copy()
            self.smooth_colors()
            self.smoothColors_smoothed = self.color_array[dimension].copy()
        else:
            self.smoothColors_original = None
            self.smoothColors_smoothed = None
        if smoothSizes and dimension in self.size_array:
            self.smoothSizes_original = self.size_array[dimension].copy()
            self.smooth_sizes()
            self.smoothSizes_smoothed = self.size_array[dimension].copy()
        else:
            self.smoothSizes_original = None
            self.smoothSizes_smoothed = None

    def cleanup_Smoothing(self):
        if self.smoothColors_original is not None:
            self.smoothColors_original = None
        if self.smoothColors_smoothed is not None:
            self.smoothColors_smoothed = None
        if self.smoothSizes_original is not None:
            self.smoothSizes_original = None
        if self.smoothSizes_smoothed is not None:
            self.smoothSizes_smoothed = None

    def perform_smoothing_fade(self, dial_amount, smoothColors, smoothSizes):
        if smoothColors and self.smoothColors_original is not None and self.smoothColors_smoothed is not None:

            originalWeight = 10 - dial_amount
            smoothedWeight = 10 - originalWeight
            smoothed_Color_Array = (self.smoothColors_original * originalWeight + self.smoothColors_smoothed * smoothedWeight) / (originalWeight + smoothedWeight)
            self.color_array[self.dimension][self.Mask] = smoothed_Color_Array[:]
        if smoothSizes and self.smoothSizes_original is not None and self.smoothSizes_smoothed is not None:
            originalWeight = 10 - dial_amount
            smoothedWeight = 10 - originalWeight
            smoothed_Size_Array = (self.smoothSizes_original * originalWeight + self.smoothSizes_smoothed * smoothedWeight) / (originalWeight + smoothedWeight)
            self.size_array[self.dimension][self.Mask] = smoothed_Size_Array[:]

    def perform_smoothing(self, dial_amount, smoothColors, smoothSizes):
        if smoothColors and self.smoothColors_original is not None and self.smoothColors_smoothed is not None:

            originalWeight = 10 - dial_amount
            smoothedWeight = 10 - originalWeight
            smoothed_Color_Array = (self.smoothColors_original * originalWeight + self.smoothColors_smoothed * smoothedWeight) / (originalWeight + smoothedWeight)
            self.color_array[self.dimension][:] = smoothed_Color_Array[:]
        if smoothSizes and self.smoothSizes_original is not None and self.smoothSizes_smoothed is not None:
            originalWeight = 10 - dial_amount
            smoothedWeight = 10 - originalWeight
            smoothed_Size_Array = (self.smoothSizes_original * originalWeight + self.smoothSizes_smoothed * smoothedWeight) / (originalWeight + smoothedWeight)
            self.size_array[self.dimension][:] = smoothed_Size_Array[:]

    def smooth_sizes_colors(self, mode = 4.0):
        level = self.voxels[self.highlighted].level
        if self.collected:
            voxels = set(self.collected)
            self.clear_collected()
        else:
            voxels = set(self.get_levelVoxels(level))
        self.remove_highlight()
        for i in voxels:
            S = 0.0
            C = array([0, 0, 0])
            v = []
            for c in i.neighbours():
                p = self.select_through_xyz(c, i.level, True)
                if p != None:
                    voxel = self.voxels[p]
                    S += voxel.size
                    C += voxel.color
                    v.append(voxel)
            if v:
                S /= len(v)
                C /= len(v)
                for j in v:
                    Mode = mode * ((j.size / level) + 1)
                    j.size[:] = (j.size * (Mode - 1) + S) / Mode
                    j.color[:] = (j.color * (Mode - 1) + C) / Mode

    def smooth_sizes(self, mode = 4.0):
        level = self.voxels[self.highlighted].level
        if self.collected:
            voxels = set(self.collected)
            self.clear_collected()
        else:
            voxels = set(self.get_levelVoxels(level))
        self.remove_highlight()
        for i in voxels:
            S = 0.0
            v = []
            for c in i.neighbours():
                p = self.select_through_xyz(c, i.level, True)
                if p != None:
                    voxel = self.voxels[p]
                    S += voxel.size
                    v.append(voxel)
            if v:
                S /= len(v)
                for j in v:
                    Mode = mode * ((j.size / level) + 1)
                    j.size[:] = (j.size * (Mode - 1) + S) / Mode

    def smooth_colors(self, mode = 4.0):
        level = self.voxels[self.highlighted].level
        if self.collected:
            voxels = set(self.collected)
            self.clear_collected()
        else:
            voxels = set(self.get_levelVoxels(level))
        self.remove_highlight()
        for i in voxels:
            C = array([0, 0, 0])
            v = []
            for c in i.neighbours():
                p = self.select_through_xyz(c, i.level, True)
                if p != None:
                    voxel = self.voxels[p]
                    C += voxel.color
                    v.append(voxel)
            if v:
                C /= len(v)
                for j in v:
                    j.color[:] = (j.color * (mode - 1) + C) / mode

    def select_expand(self):
        if not self.collected:
            collected = [self.voxels[self.highlighted],]
        else:
            collected = self.collected
        n = list(collected)
        for v in collected:
            for c in v.neighbours():
                p = self.select_through_xyz(c, v.level, True)
                if p != None:
                    n.append(self.voxels[p])
        self.collected = list(set(n))
        self.highlight_collection()
        self.validate_highlight()

    def find_neighbours(self, falloff, voxel):
        self.falloff = falloff
        if falloff == 0:
            self.neighbours = [[]]
            return
        if voxel == None:
            voxels = self.collected
        else:
            voxels = [self.voxels[voxel],]

        self.neighbours = [[]]
        for i in range(falloff):
            neighs = []
            for v in voxels:
                n = []
                for c in v.neighbours():
                    p = self.select_through_xyz(c, v.level, True)
                    if p != None:
                        if self.voxels[p] not in n:
                            n.append(self.voxels[p])
                for N in n:
                    if N not in neighs:
                        neighs.append(N)

            voxels = set(neighs) - set(self.neighbours[-1])
            self.neighbours.append(voxels)

        if self.collected != []:
            self.clear_collected()

    def update_voxels_scale(self, scale, v = None):
        c = []
        if v != None and v < len(self.voxels):
            voxel = self.voxels[v]
            if self.collected:
                c = self.collected
            elif voxel.spawned:
                c = [voxel,] + voxel.voxels
            else:
                c = [voxel,]
        for i in c:
            i.size[:] = i.level * scale

    def paste_by_coordinates(self, collected):
        c = []
        for i in set(self.voxels):
            t = i.coords - array(self.conform_position) - array(self.local_conform)
            if tuple(t) in collected:
                c.append(i)
        self.collected = c
        self.highlight_collection()
        self.validate_highlight()
        return len(c)

    def give_by_coordinates(self):
        collected = []
        for i in self.collected:
            t = i.coords - array(self.conform_position) - array(self.local_conform)
            collected.append(tuple(t))
        return collected

    def get_levelVoxels(self, level):
        voxels = []
        for i in self.voxels:
            if i.level == level:
                voxels.append(i)
        return voxels

    def give_active_bounds(self):
        dim = self.get_dimension()
        (X, Y, Z) = self.visibility_array[dim].shape
        X_bounds = []
        Y_bounds = []
        Z_bounds = []
        for x in range(X):
            for y in range(Y):
                for z in range(Z):
                    i = self.visibility_array[dim][x, y, z]
                    if i == 1:
                        X_bounds.append(x)
                        Y_bounds.append(y)
                        Z_bounds.append(z)
        if not X_bounds:
            X_dim = 0
            Y_dim = 0
            Z_dim = 0
            X_bounds = [0, 0]
            Y_bounds = [0, 0]
            Z_bounds = [0, 0]
        else:
            X_bounds.sort()
            Y_bounds.sort()
            Z_bounds.sort()
            X_dim = X_bounds[-1] - X_bounds[0] + 1
            Y_dim = Y_bounds[-1] - Y_bounds[0] + 1
            Z_dim = Z_bounds[-1] - Z_bounds[0] + 1
            X_bounds = [X_bounds[0], X_bounds[-1]]
            Y_bounds = [Y_bounds[0], Y_bounds[-1]]
            Z_bounds = [Z_bounds[0], Z_bounds[-1]]
        print(X_bounds, Y_bounds, Z_bounds, X_dim, Y_dim, Z_dim)
        return X_bounds, Y_bounds, Z_bounds, X_dim, Y_dim, Z_dim

    def validate_animated_Cube(self):
        (X, Y, Z) = self.animated_Cube.shape
        level = 1.0 / float(X)
        A = self.animated_Cube.flatten()
        voxels = self.get_levelVoxels(level)
        voxels = iter(voxels)
        for i in A:
            v = next(voxels)
            if v.currency != i:
                return False
        return True

    def dump_arrays(self, minorlevel = True):
        if not minorlevel:
            voxels = self.return_voxel_hierarchy()
            level = voxels[-1].level
            for i in voxels[::-1]:
                if i.get_visibility():
                    level = i.level
            dim = int(1.0 / level)
            v = {}
            c = {}
            s = {}
            V = {}
            for k in self.visibility_array.keys():
                if k <= dim:
                    v[k] = self.visibility_array[k]
                    c[k] = self.color_array[k]
                    s[k] = self.size_array[k]
                    V[k] = self.vector_array[k]
            return v, c, s, V
        else:
            return self.visibility_array, self.color_array, self.size_array, self.vector_array

    def setup_visibility_array(self, dimension):
        if dimension not in self.visibility_array:
            self.visibility_array[dimension] = zeros((dimension, dimension, dimension), dtype=uint8)

    def setup_color_array(self, dimension):
        if dimension not in self.color_array:
            self.color_array[dimension] = zeros((dimension * dimension * dimension, 3), dtype=int)

    def setup_vector_array(self, dimension):
        if dimension not in self.vector_array:
            self.vector_array[dimension] = zeros((dimension * dimension * dimension, 3), dtype=float)

    def setup_size_array(self, dimension):
        if dimension not in self.size_array:
            self.size_array[dimension] = zeros((dimension * dimension * dimension, 1), dtype=float)
            self.size_array[dimension].fill(1.0 / float(dimension))

    def setup_index_array(self, dimension):
        if dimension not in self.index_array:
            index_array = arange((dimension * dimension * dimension), dtype=int32)
            self.index_array[dimension] = index_array.reshape((dimension, dimension, dimension))
            print("setup_index_array", self.index_array[dimension].shape)

    def setup_coords_array(self, dimension):
        if dimension not in self.coords_array:
            level = 1 / float(dimension)
            self.coords_array[dimension] = zeros((dimension * dimension * dimension, 3), dtype=float)
            for index in range(dimension * dimension * dimension):
                i = unravel_index(index, (dimension, dimension, dimension))
                x = ((i[0] * 2) - dimension + 1) * level
                y = ((i[1] * 2) - dimension + 1) * level
                z = ((i[2] * 2) - dimension + 1) * level
                self.coords_array[dimension][index] = (x, y, z)
            self.coords_array[dimension] += self.conform_position + self.local_conform

    def setup_baked_array(self, dimension):
        if dimension not in self.baked_array:
            self.baked_array[dimension] = zeros((dimension * dimension * dimension, 3), dtype=float)

    def setup_rotated_array(self, dimension):
        if dimension not in self.rotated_array:
            self.rotated_array[dimension] = zeros((dimension * dimension * dimension, 3), dtype=float)

    def setup_Size_Color_And_Vectors(self, dimension):
        self.Size_Array[dimension] = zeros((dimension, dimension, dimension), dtype = object)
        self.Color_Array[dimension] = zeros((dimension, dimension, dimension), dtype = object)
        self.Vector_Array[dimension] = zeros((dimension, dimension, dimension), dtype = object)

    def create_arrays(self, dimension):
        #
        # when new voxels are spawned and level is finer of levels that exsist.
        # Spawning is a process of publishing voxels with their children.
        # To check exsisting levels, it can use visibility_array.keys()
        # If exists, spawning just accesses existing arrays to set visibility,
        # color, size, get index and setup position.
        #
        self.setup_visibility_array(dimension)
        self.setup_color_array(dimension)
        self.setup_vector_array(dimension)
        self.setup_size_array(dimension)
        self.setup_index_array(dimension)
        self.setup_coords_array(dimension)
        self.setup_baked_array(dimension)
        self.setup_rotated_array(dimension)
        self.setup_Size_Color_And_Vectors(dimension)

    def setup_array(self, dimension, arrange = False, force = False):
        if force or self.animated_Cube_filled != dimension:
            print('FORCE')
            self.animated_Cube = zeros((dimension, dimension, dimension), dtype=int32)
            self.animated_Cube.fill(-1)
            self.animated_Cube_filled = dimension
            level = 1.0 / float(dimension)
            for i in set(self.voxels):
                if i.level == level:
                    x = int(((i.coords[0] - self.conform_position[0] - self.local_conform[0]) / level) + dimension) // 2
                    y = int(((i.coords[1] - self.conform_position[1] - self.local_conform[1]) / level) + dimension) // 2
                    z = int(((i.coords[2] - self.conform_position[2] - self.local_conform[2]) / level) + dimension) // 2
                    try:
                        self.animated_Cube[x, y, z] = i.currency
                    except:
                        pass
        if arrange:
            self.arrange_animated_Cube()
            self.validate_voxels()
        return self.highlighted

    def give_voxel_indexes(self):
        indexes = []
        for i in set(self.voxels):
            indexes.append(i.currency)
        return indexes

    def arrange_animated_Cube(self):
        if self.highlighted < len(self.voxels):
            h = self.voxels[self.highlighted]
        else:
            h = self.voxels[-1]
        (X, Y, Z) = self.animated_Cube.shape
        level = 1.0 / float(X)
        voxels = []
        for x in range(X):
            for y in range(Y):
                for z in range(Z):
                    i = self.animated_Cube[x, y, z]
                    voxels.append(self.voxels[i])
        self.animated_Cube = arange(X * Y * Z).reshape(X, Y, Z)
        v0 = set(voxels)
        v1 = set(self.voxels)
        v = v1 - v0
        self.voxels = voxels + list(v)
        c = self.select_through_xyz(h.coords, level)
        self.get_highlight(c)

    def shift_colors_reset(self):
        self.sub_mask = array([False])

    def shift_colors(self, R, G, B):
        dimension = self.get_dimension()
        if dimension in self.color_array:
            if len(self.sub_mask) != len(self.color_array[dimension]):
                self.sub_mask = False
                self.add_mask = True
            color_array = self.color_array[dimension].copy()
            color_array[self.add_mask] += 10
            color_array[self.sub_mask] -= 10
            color_array = clip(color_array, 0, 255)
            sub_mask = greater(color_array, 245)
            self.sub_mask = logical_or(sub_mask, self.sub_mask)
            add_mask = less(color_array, 10)
            self.add_mask = logical_not(self.sub_mask)
            self.add_mask = logical_or(add_mask, self.add_mask)
            self.sub_mask = logical_not(self.add_mask)
            if R and G and B:
                self.color_array[dimension][:] = color_array[:]
            else:
                if R:
                    self.color_array[dimension][:, 0] = color_array[:, 0]
                if G:
                    self.color_array[dimension][:, 1] = color_array[:, 1]
                if B:
                    self.color_array[dimension][:, 2] = color_array[:, 2]

    def reset_all_voxels(self):
        for i in set(self.voxels):
            i.size[:] = i.level * float(2)

    def reset_matrix(self):
        (x, y, z) = self.animated_Cube.shape
        for X in range(x):
            for Y in range(y):
                for Z in range(z):
                    v = self.animated_Cube[X, Y, Z]
                    self.voxels[v].size[:] = self.voxels[v].level * float(2)

    def manifest_color(self, R, G, B):
        dimension = self.get_dimension()
        if dimension in self.color_array:
            color_array = zeros((dimension, dimension, dimension, 3), dtype = int)
            step_x = 255.0 / float(dimension)
            step_y = 255.0 / float(dimension)
            step_z = 255.0 / float(dimension)
            X = 0.0
            for x in range(dimension):
                Y = 0.0
                for y in range(dimension):
                    Z = 0.0
                    for z in range(dimension):
                        color_array[x, y, z][:] = (int(X), int(Y), int(Z))
                        Z += step_z
                    Y += step_y
                X += step_x
            color_array = color_array.reshape(dimension * dimension * dimension, 3)
            if R and G and B:
                self.color_array[dimension][:] = color_array[:]
            else:
                if R:
                    self.color_array[dimension][:, 0] = color_array[:, 0]
                if G:
                    self.color_array[dimension][:, 1] = color_array[:, 1]
                if B:
                    self.color_array[dimension][:, 2] = color_array[:, 2]

    def manifest_grays(self, R, G, B):
        dimension = self.get_dimension()
        if dimension in self.color_array:
            step = 255.0 / float(dimension **3)
            color_array = arange(0, 255, step)
            if R:
                self.color_array[dimension][:, 0] = color_array[:]
            if G:
                self.color_array[dimension][:, 1] = color_array[:]
            if B:
                self.color_array[dimension][:, 2] = color_array[:]

    def get_portion_of_cube(self, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim):
        if not self.collected:
            return None
        else:
            collected = self.return_levelVoxels_Indexes()
        a = zeros((Xdim, Ydim, Zdim), dtype = list)
        for X in range(Xdim):
            for Y in range(Ydim):
                for Z in range(Zdim):
                    Xb = X + Xbound[0]
                    Yb = Y + Ybound[0]
                    Zb = Z + Zbound[0]
                    v = self.animated_Cube[Xb, Yb, Zb]
                    if v in collected:
                        a[X, Y, Z] = 1
        return a

    def select_same_Currency(self, c, level):
        voxels = set(self.get_levelVoxels(level))
        for i in voxels:
            if i.Currency == c:
                return i.currency
        return None

    def select_through_xyz(self, c, level, notfound = False):
        (x, y, z) = c
        (X, Y, Z) = self.animated_Cube.shape
        x1 = int((((x - self.conform_position[0] - self.local_conform[0]) / level) + X) / 2)
        y1 = int((((y - self.conform_position[1] - self.local_conform[1]) / level) + Y) / 2)
        z1 = int((((z - self.conform_position[2] - self.local_conform[2]) / level) + Z) / 2)
        if (x1 < X and x1 >= 0 and
            y1 < Y and y1 >= 0 and
            z1 < Z and z1 >= 0):
            v = self.animated_Cube[x1, y1, z1]
            if v < len(self.voxels):
                if self.voxels[v].level == level:
                    return v
        if notfound:
            return None
        else:
            return self.highlighted

    def load_vector_frame(self, data, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim):
        try:
            animated_Cube = data.reshape(Xdim, Ydim, Zdim, 1)
        except:
            print("error 2")
            return
        dimension = self.get_dimension()
        vectors = animated_Cube[:,:,:,0]

        V = self.Vector_Array[dimension]
        try:
            V[Xbound[0]: Xbound[-1] + 1, Ybound[0]: Ybound[-1] + 1, Zbound[0]: Zbound[-1] + 1] = vectors
        except:
            print("error 3")
            return

        l = len(self.vector_array[dimension])
        x = 0
        for v in V.flatten():
            if v is not None:
                self.vector_array[dimension][x] = v
            x += 1
            if x >= l:
                break

    def load_frame_size(self, data, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim):
        try:
            animated_Cube = data.reshape(Xdim, Ydim, Zdim, 2)
        except:
            print("error 1")
            return
        dimension = self.get_dimension()
        sizes = animated_Cube[:,:,:,0]

        S = self.Size_Array[dimension]
        try:
            S[Xbound[0]: Xbound[-1] + 1, Ybound[0]: Ybound[-1] + 1, Zbound[0]: Zbound[-1] + 1] = sizes
        except:
            print("error 1")
            return

        l = len(self.size_array[dimension])
        x = 0
        for s in S.flatten():
            if s is not None:
                self.size_array[dimension][x] = s
            x += 1
            if x >= l:
                break

    def load_frame(self, data, Xbound, Ybound, Zbound, Xdim, Ydim, Zdim):
        try:
            animated_Cube = data.reshape(Xdim, Ydim, Zdim, 2)
        except:
            print("error 1")
            return
        dimension = self.get_dimension()
        sizes = animated_Cube[:,:,:,0]
        colors = animated_Cube[:,:,:,1]

        S = self.Size_Array[dimension]
        C = self.Color_Array[dimension]
        try:
            S[Xbound[0]: Xbound[-1] + 1, Ybound[0]: Ybound[-1] + 1, Zbound[0]: Zbound[-1] + 1] = sizes
            C[Xbound[0]: Xbound[-1] + 1, Ybound[0]: Ybound[-1] + 1, Zbound[0]: Zbound[-1] + 1] = colors
        except:
            print("error 1")
            return

        l = len(self.size_array[dimension])
        x = 0
        for s, c in zip(S.flatten(), C.flatten()):
            if s is not None:
                self.size_array[dimension][x] = s
            if c is not None:
                self.color_array[dimension][x] = c
            x += 1
            if x >= l:
                break

    def write_frame(self, shape, color, illu_color = False):
        #print('WRITE OBJECT FRAME', shape, color)
        (Xbound, Ybound, Zbound, Xdim, Ydim, Zdim) = self.give_active_bounds()
        (x, y, z) = self.animated_Cube.shape
        a = []
        for X in range(Xbound[0], Xbound[-1] + 1):
            for Y in range(Ybound[0], Ybound[-1] + 1):
                for Z in range(Zbound[0], Zbound[-1] + 1):
                    v = self.animated_Cube[X, Y, Z]
                    #print(v)
                    if shape:
                        s = self.voxels[v].size[0]
                    else:
                        s = None
                    if color:
                        if illu_color:
                            c = list(self.voxels[v].illu_color)
                        else:
                            c = list(self.voxels[v].color)
                    else:
                        c = None
                    a.append([s, c])
        return a

    def get_biggest_pixel(self):
        P = self.voxels[0]
        collect = []
        P.find_parent_recursive(collect)
        if collect[0].level > P.level:
            P = collect[0]
        return P.currency

    def reset_camera_pan(self):
        if self.position != (0.0, 0.0, 0.0):
            center = (-self.position[0], -self.position[1], -self.position[2])
            self.move_around(center)
            self.oldcenter = None

    def store_angle(self):
        self.backupangle = self.angle

    def restore_angle(self):
        self.angle = self.backupangle

    def undo_zoom_screen(self, level = None, depth_factor = None):
        if depth_factor != None:
            z = (depth_factor * (1 - level))
            center = (self.center[0], self.center[1], -z)
        else:
            center = (self.center[0], self.center[1], 0)
        self.move_around(center = center)
        if self.oldcenter is not None:
            self.center = self.oldcenter
        self.oldcenter = None

    def reset_pan(self):
        center = (0.0, 0.0, 0.0)
        self.position = (0.0, 0.0, 0.0)
        self.move_around(center = center)
        self.oldcenter = None

    def move_to_the_screen(self, current, depth_factor = None, restore = False):
        self.position = (0.0, 0.0, 0.0)
        self.oldpos = self.position
        if restore:
            self.position = (-self.oldpos[0], -self.oldpos[1], -self.oldpos[2])
        if depth_factor != None:
            print(depth_factor)
            z = (depth_factor * (1 - current.level)) - current.xyz_rotated[2]
            center = (-current.xyz_rotated[0], -current.xyz_rotated[1], z)
        else:
            center = (-current.xyz_rotated[0], -current.xyz_rotated[1], 0)
        if self.oldcenter is None:
            self.oldcenter = self.center
        self.center = current.xyz_rotated
        self.move_around(center = center)

    def invert_collected(self):
        self.collected = list(set(self.voxels) - set(self.collected))
        self.highlight_collection()
        self.validate_highlight()

    def clear_collected(self):
        self.collected = []
        self.validate_highlight()

    def return_voxels_in_3d_rect(self, rect):
        collection = []
        for i in set(self.voxels):
            if (i.coords[0] < rect.max.x and i.coords[0] > rect.min.x
                and i.coords[1] < rect.max.y and i.coords[1] > rect.min.y
                and i.coords[2] < rect.max.z and i.coords[2] > rect.min.z):
                collection.append(i)
        return collection

    def voxel_at_coordinates(self, voxels):
        center = self.rect.give_center()
        print("voxel_at_coordinates", (center.x, center.y, center.z))
        for i in voxels:
            if (i.coords[0] == center.x
                and i.coords[1] == center.y
                and i.coords[2] == center.z):
                return i
        return self.voxels[0]

    def return_prominent_3d_voxel(self):
        print("return_prominent_3d_voxel")
        voxels = self.return_voxels_in_3d_rect(self.rect)
        self.rect.state = False
        if len(voxels) < 1:
            return self.voxels[0]
        else:
            return self.voxel_at_coordinates(voxels)

    def return_3d_rect(self, voxels):
        i = voxels[0]
        r = rect_3d((i.coords[0], i.coords[1], i.coords[2], i.coords[0], i.coords[1], i.coords[2]))
        for i in voxels:
            if i.coords[0] - i.level < r.min.x:
                r.min.x = i.coords[0] - i.level
            if i.coords[1] - i.level < r.min.y:
                r.min.y = i.coords[1] - i.level
            if i.coords[2] - i.level < r.min.z:
                r.min.z = i.coords[2] - i.level
            if i.coords[0] + i.level > r.max.x:
                r.max.x = i.coords[0] + i.level
            if i.coords[1] + i.level > r.max.y:
                r.max.y = i.coords[1] + i.level
            if i.coords[2] + i.level > r.max.z:
                r.max.z = i.coords[2] + i.level
        r.state = True
        return r

    def get_current(self):
        voxel = self.voxels[self.highlighted]
        return voxel.coords - array(self.local_conform)

    def put_current(self, current):
        for i in set(self.voxels):
            t = i.coords - array(self.local_conform)
            if tuple(t) == tuple(current):
                return i

    def get_collection(self):
        c = []
        if not self.collected:
            collected = [self.voxels[self.highlighted],]
        else:
            collected = self.collected
        for i in collected:
            t = i.coords - array(self.local_conform)
            c.append(tuple(t))
        return c

    def set_collection(self, collection):
        c = []
        for i in set(self.voxels):
            t = i.coords - array(self.local_conform)
            if tuple(t) in collection:
                c.append(i)
        return c

    def refine_highlighted_level(self, level, collection, Zipped = False):
        self.clear_collected()
        level = level / 2.0
        for i in collection:
            if i.level > level:
                i.spawn_recursive(level, Zipped, False)
        self.validate_voxels()
        self.get_highlight(0)

    def refine_highlighted(self, to_level = False, Zipped = False):
        v = self.voxels[self.highlighted]
        level = v.level
        if to_level:
            level = level / 2.0
        if not self.collected:
            c = [self.voxels[self.highlighted],]
            n = 0
        else:
            c = self.collected
            v = self.return_prominent_3d_voxel()
            n = v.currency
        for i in c:
            if i.level > level:
                i.spawn_recursive(level, Zipped, False)
        self.clear_collected()
        self.validate_voxels()
        self.get_highlight(n)
        return n

    def raise_levels(self):
        level = self.voxels[self.highlighted].level
        self.collected = []
        for i in set(self.voxels):
            if i.level == level:
                i.collect_all_child_voxels(self.collected)
        self.remove_highlighted()
        return 0

    def append_collection(self, voxels):
        candidates = []
        for i in voxels:
            #if i < len(self.voxels):
            candidates.append(self.voxels[i])
        collected = list(self.collected) + candidates
        self.collected = list(set(collected))

    def create_3d_array(self, level):
        H = {}
        for i in set(self.voxels):
            if i.level == level:
                t = i.coords
                H[t] = i.currency
        return H

    def return_slice_with(self, o, level):
        A = self.create_3d_array(level)
        B = o.create_3d_array(level)
        C = []
        for x, i in B.items():
            if x in A:
                C.append(A[x])
        print("C", C)
        return C

    def subtract_collection(self, voxels):
        candidates = []
        for i in voxels:
            #if i < len(self.voxels):
            candidates.append(self.voxels[i])
        collected = set(self.collected) - set(candidates)
        self.collected[:] = collected

    def create_collection(self, v):
        self.collected = []
        for i in v:
            #if i < len(self.voxels):
            self.collected.append(self.voxels[i])

    def highlight_collection(self):
        for i in self.collected:
            i.set_illumination()

    def highlight_all(self):
        self.collected = list(set(self.voxels))
        self.highlight_collection()

    def highlight_tree(self, v):
        if v >= 0 and v < len(self.voxels):
            if self.voxels[v].spawned:
                p = self.voxels[v]
            else:
                p = self.voxels[v].parent
            if p:
                p.collect_all_child_voxels(self.collected)
                self.collected[:] = set(self.collected)
                for i in self.collected:
                    i.set_illumination()
        if self.rect.state == False:
            if len(self.voxels) > 1 and self.collected:
                self.rect = self.return_3d_rect(self.collected)
            print("return_3d_rect", self.rect.return_tuple())

    def remove_highlighted_level(self, collected):
        if not collected:
            return self.highlighted
        level = self.voxels[self.highlighted].level
        dim = 1.0 / float(level)
        n = sum(self.visibility_array[dim])
        if self.collected:
            v = list(self.collected)[-1].parent
        else:
            v = self.voxels[self.highlighted].parent
        self.clear_collected()
        self.remove_highlight()
        if len(collected) == len(set(self.voxels)):
            voxel = self.get_biggest_pixel()
            v = self.voxels[voxel]
            collected = set(collected) - set([v])
            for i in list(collected)[::-1]:
                i.spawned = False
                if i.voxels:
                    i.zipped = True
            for dim in self.visibility_array.keys():
                if dim > 1:
                    self.visibility_array[dim].fill(0)
            v.turn_visible()
            v.spawned = False
            v.zipped = True
            self.voxels = [v,]
        elif len(collected) == n and n > 1:
            parents = self.give_parents(collected)
            for i in parents:
                i.turn_visible()
                i.spawned = False
                i.zipped = True
            #self.visibility_array[dim].fill(0)
            self.voxels = list(set(self.voxels) - set(collected))
        else:
            for i in list(collected)[::-1]:
                i.collect_voxels(False)
        self.validate_voxels()
        self.validate_visibility()
        try:
            self.get_highlight(v.currency)
            return v.currency
        except:
            return 0

    def give_parents(self, collected):
        parents = []
        for i in collected:
            parents.append(i.parent)
        return list(set(parents))

    def remove_highlighted(self, voxel = None):
        if self.collected:
            v = list(self.collected)[-1].parent
            level = self.voxels[self.highlighted].level
            dim = 1.0 / float(level)
            n = sum(self.visibility_array[dim])
        else:
            v = self.voxels[self.highlighted].parent
        if self.collected:
            c = self.collected
            self.clear_collected()
            self.remove_highlight()
            if len(self.collected) == len(set(self.voxels)):
                voxel = self.get_biggest_pixel()
                v = self.voxels[voxel]
                c = set(c) - set([v])
                for i in list(c)[::-1]:
                    i.spawned = False
                    if i.voxels:
                        i.zipped = True
                for dim in self.visibility_array.keys():
                    if dim > 1:
                        self.visibility_array[dim].fill(0)
                v.turn_visible()
                v.spawned = False
                v.zipped = True
                self.voxels = [v,]
            elif len(c) == n and n > 1:
                parents = self.give_parents(c)
                for i in parents:
                    i.turn_visible()
                    i.spawned = False
                    i.zipped = True
                #self.visibility_array[dim].fill(0)
                self.voxels = list(set(self.voxels) - set(c))
            else:
                for i in list(c)[::-1]:
                    i.collect_voxels(False)
            self.clear_collected()
        elif (voxel != None) and self.voxels[voxel].spawned:
            c = self.voxels[self.highlighted].voxels
            if not c:
                return v.currency
            self.remove_highlight()
            for i in c[::-1]:
                i.collect_voxels(False)
        self.validate_voxels()
        self.validate_visibility()
        try:
            self.get_highlight(v.currency)
            return v.currency
        except:
            return 0

    def collapse_all(self):
        self.clear_collected()
        self.remove_highlight()
        voxel = self.get_biggest_pixel()
        v = self.voxels[voxel]
        c = set(self.voxels) - set([v])
        for i in list(c)[::-1]:
            i.spawned = False
            if i.voxels:
                i.zipped = True
        for dim in self.visibility_array.keys():
            if dim > 1:
                self.visibility_array[dim].fill(0)
        v.turn_visible()
        v.spawned = False
        v.zipped = True
        self.voxels = [v,]
        self.clear_collected()
        self.validate_voxels()
        self.validate_visibility()
        self.get_highlight(0)

    def validate_visibility(self):
        voxels = self.return_voxel_hierarchy()
        Voxels = set(self.voxels)
        for i in voxels:
            if i not in Voxels:
                i.turn_invisible()

    def clear_highlight(self):
        for i in set(self.voxels):
            i.clear_highlight()

    def clear_illumination(self):
        for i in set(self.voxels):
            i.clear_illumination()

    def validate_highlight(self):
        voxels = set(self.voxels) - set(self.collected)
        for i in voxels:
            i.clear_illumination()

    def get_highlight(self, v):
        if v >= 0 and v < len(self.voxels):
            if self.highlighted < len(self.voxels):
                self.voxels[self.highlighted].highlighted = False
            self.validate_highlight()
            self.voxels[v].set_illumination()
            self.voxels[v].highlighted = True
            self.highlighted = v

    def remove_highlight(self):
        if self.highlighted < len(self.voxels):
            self.voxels[self.highlighted].clear_highlight()
            if self.voxels[self.highlighted] not in self.collected:
                self.voxels[self.highlighted].clear_illumination()

    def change_spawned(self, v = None):
        if not v:
            voxels = self.collected
        else:
            voxels = [self.voxels[self.highlighted],]
        if not voxels:
            if self.voxels[self.highlighted].spawned:
                for i in self.voxels[self.highlighted].voxels:
                    i.spawned = False
                    i.turn_visible()
        for i in voxels:
            if i.spawned == True:
                i.spawned = False
                i.turn_visible()
            else:
                i.spawned = True
                i.turn_invisible()

    def localize_nodes(self, vector = None):
        print("localize cubes")
        if vector is None:
            vector = self.local
        for node in self.child_nodes:
            node.localize(vector)

    def restore_vector(self):
        self.vec_x = (1, 0, 0)
        self.vec_y = (0, 1, 0)
        self.vec_z = (0, 0, 1)
        print("restored")

    def set_vector(self, vector):
        if self.LOCAL:
            self.local = vector
            self.give_local_vector(vector, self.parent.local, self.parent.angle)
        else:
            self.parent.local = vector
            self.parent.vector = vector

    def set_angle(self, angle):
        if self.LOCAL:
            self.angle = angle
        else:
            self.parent.angle = angle

    def set_name(self, name):
        self.name = name

    def give_up_vector(self):
        if self.LOCAL:
            return self.vec_y
        else:
            if (self.previousangle != self.parent.angle or
                self.previouslocal != self.parent.local):
                self.previousangle = self.parent.angle
                self.previouslocal = self.parent.local
                self.up_vector = self.rotate_center((0, 1, 0), self.parent.local, self.parent.angle)
            return self.up_vector

    def give_local_vector(self, vector, space, angle):
        print("give_local_vector")
        if vector is None:
            vector = self.local
        if space is None:
            space = self.parent.local
        self.vector = self.rotate_center(vector, space, angle)
        self.vec_x = self.rotate_center((1, 0, 0), space, angle)
        self.vec_y = self.rotate_center((0, 1, 0), space, angle)
        self.vec_z = self.rotate_center((0, 0, 1), space, angle)
        print(self.vector)

    def rotate_center(self, center, vector, angle):
        x = center[0]
        y = center[1]
        z = center[2]

        y_x_angle = math.atan2(vector[1], vector[0])

        x_1 = math.cos(-y_x_angle) * x - math.sin(-y_x_angle) * y
        y_1 = math.sin(-y_x_angle) * x + math.cos(-y_x_angle) * y

        l_x_y = math.sqrt(vector[0] * vector[0] + vector[1] * vector[1])
        x_z_angle = math.atan2(-vector[2], l_x_y)

        x_2 = math.cos(-x_z_angle) * x_1 + math.sin(-x_z_angle) * z
        z_2 = -math.sin(-x_z_angle) * x_1 + math.cos(-x_z_angle) * z

        y_3 = math.cos(angle) * y_1 - math.sin(angle) * z_2
        z_3 = math.sin(angle) * y_1 + math.cos(angle) * z_2

        x_4 = math.cos(x_z_angle) * x_2 + math.sin(x_z_angle) * z_3
        z_4 = -math.sin(x_z_angle) * x_2 + math.cos(x_z_angle) * z_3

        x_5 = math.cos(y_x_angle) * x_4 - math.sin(y_x_angle) * y_3
        y_5 = math.sin(y_x_angle) * x_4 + math.cos(y_x_angle) * y_3

        x = x_5
        y = y_5
        z = z_4
        return (x, y, z)

    def give_center(self, vector = None, angle = None):
        center = array(self.conform_position) + array(self.local_conform)
        if vector == None:
            vector = self.local
            print("give_center", vector)
        if angle == None:
            angle = self.angle
        center = self.rotate_center(center, vector, angle)
        return array(center, dtype = float32)

    def give_center_parent(self, n = None, angle = 0):
        print("IN PARENT")
        return self.cube.give_center_parent()
##        if n == None:
##            n = self.highlighted
##        if n < len(self.voxels):
##            center = [0]
##            self.voxels[n].find_parent_recursive_parent(center)
##        else:
##            center[0] = None
##        return center[0]

    def give_center_actual(self):
        x = 0
        y = 0
        z = 0
        for i in set(self.voxels):
            x += i.xyz_rotated[0]
            y += i.xyz_rotated[1]
            z += i.xyz_rotated[2]
        if len(self.voxels) > 0:
            return array([x/len(self.voxels), y/len(self.voxels), z/len(self.voxels)], dtype = float32)
        else:
            return (0, 0, 0)

    def select_closest(self):
        voxels = self.z_sort()
        v = voxels[-1].currency
        self.get_highlight(v)
        return v

    def set_picmap(self, s):
        self.create_picmap = s

    def map_to_screen(self, s):
        w = screen.width
        h = screen.height
        if w > h:
            k = h
        else:
            k = w
        s = s * k / 2
        return s

    def render_shadows(self):
        self.cube.blit_shadow(self.Depth)

    def set_voxel_images(self, Status = True):
        if self.collected != []:
            voxels = self.collected
        else:
            voxels = [self.voxels[self.highlighted],]
        for i in voxels:
            i.set_images(Status)

    def set_voxel_repro(self, repro, OBJ_repro, texture, texName):
        if self.collected != []:
            voxels = self.collected
        else:
            voxels = [self.voxels[self.highlighted],]
        for i in voxels:
            i.set_repro(repro, OBJ_repro, texture, texName)

    def set_voxel_texture(self, texture, texName, voxel = None):
        if voxel == None:
            voxel = self.highlighted
        if self.collected != []:
            voxels = self.collected
        else:
            voxels = [self.voxels[voxel],]
        for i in voxels:
            i.set_texture(texture, texName)

    def set_images(self):
        self.image = image_name
        self.images = images

    def set_repro(self, repro, OBJ_repro, texture, texName):
        self.repro = repro
        self.OBJ_repro = OBJ_repro
        if self.OBJ_repro:
            self.Frames = self.OBJ_repro.Frames
        else:
            self.Frames = 0
        if texture:
            self.texName = texName
            self.texture = texture

    def set_texture(self, texture, texName):
        self.texName = texName
        self.texture = texture

    def set_frame(self, f = None):
        if self.OBJ_repro and self.OBJ_repro.Frames > 1:
            voxels = self.return_levelVoxels()
            for i in voxels:
                if f is None:
                    frame = random.randint(0, self.OBJ_repro.Frames - 1)
                else:
                    frame = f
                i.set_frame(frame)

    def set_voxel_oscillate(self):
        if self.collected != []:
            voxels = self.collected
        else:
            voxels = [self.voxels[self.highlighted],]
        for i in voxels:
            i.set_oscillate()

    def set_voxel_frames(self, f = None):
        if self.collected != []:
            voxels = self.collected
        else:
            voxels = [self.voxels[self.highlighted],]
        for i in voxels:
            if i.OBJ_repro and i.OBJ_repro.Frames > 1:
                if f is None:
                    frame = random.randint(0, i.OBJ_repro.Frames - 1)
                else:
                    frame = f
                i.set_frame(frame)

    def clean_Ground(self):
        self.ground = None
        self.groundImage = ""
        self.draw_Ground = False

    def set_Ground(self, imagename):
        self.groundImage = imagename
        if imagename in screen.texNamesList:
            self.ground = screen.texNamesList[imagename]

    def set_Ground_Texture(self, ground):
        self.ground = ground

    def draw_selection_rect(self):
        if screen.SDL_Mode and self.draw_Cube:
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_LINE_STIPPLE)
            glCallList(screen.Empty_texture)
            center = self.voxels[self.highlighted].blit_point(self.Depth)
            size = center[2] * 1.42
            if size < 10:
                radius = 10
                refine = 4
            else:
                radius = size
                refine = 30
            step = pi2 / float(refine)
            c = pi / 4.0
            glNormal3fv((0.0, 1.0, 0.0))
            glColor4fv(gl_selectioncolor)
            glLineStipple(1, 0x3333)
            glBegin(GL_LINE_LOOP)
            for i in range(refine):
                glVertex2f(cos(c) * radius + center[0],
                           sin(c) * radius + center[1])
                c += step
            glEnd()
            glLineStipple(1, 0xCCCC)
            glColor4fv(gl_black)
            glBegin(GL_LINE_LOOP)
            for i in range(refine):
                glVertex2f(cos(c) * radius + center[0],
                           sin(c) * radius + center[1])
                c += step
            glEnd()
            glDisable(GL_LINE_STIPPLE)
            glEnable(GL_DEPTH_TEST)
            screen.texture = screen.Empty_texture
        elif self.draw_Cube:
            center = self.voxels[self.highlighted].blit_point(self.Depth)
            size = center[2] * 1.42
            if size < 10:
                pygame.draw.rect(screen.surface, (255, 255, 255), (int(center[0] - 10), int(center[1] - 10), 20, 20), 1)
            else:
                radius = size
                pygame.draw.circle(screen.surface, (255, 255, 255), (int(center[0]), int(center[1])), int(radius), 1)

    def render(self, groundAll, VectorAnimation):
        if groundAll or self.create_picmap:
            if self.draw_Ground:
                if self.propagate:
                    self.cube.draw_ground(self.Depth, None)
                else:
                    self.cube.draw_ground(self.Depth, self.ground)
        if self.create_picmap:
            del screen.screen_voxel
            screen.screen_voxel = {}
            if screen.OBJ_Mode:
                center = self.cube.vcenter.blit_line(self.Depth)
                radius = self.map_to_screen(1.0)
                screen.draw_OBJ(center, radius, self.cube3d.get_angle(), self.cube3d.local, self.cube.get_angle(), self.cube.local, self.Depth)
                if screen.SDL_Mode:
                    glMatrixMode(GL_MODELVIEW)
                    glLoadIdentity()
                else:
                    self.cube3d.blit_line(self.Depth)
        if screen.SDL_Mode:
            self.cube.get_diagonals()
            voxels = self.z_sort()
            L = len(voxels)
            if L > self.voxelLimit:
                voxels = voxels[-self.voxelLimit:]
            angle = self.get_angle()
            for x, i in enumerate(voxels):
                i.blit_at(self.Depth, x, L, self.draft_Mode, self.images, VectorAnimation, angle)
        else:
            voxels = self.z_sort()
            L = len(voxels)
            if L > self.voxelLimit:
                voxels = voxels[-self.voxelLimit:]
            for x, i in enumerate(voxels):
                i.blit_at(self.Depth, x, L, self.draft_Mode, self.images)
        if self.draw_Cube:
            self.cube.blit_line(self.Depth)

    def z_sort(self):
        min_list = []
        voxels = set(self.voxels)
        values = []
        #values = [(x.z_rotated, x) for x in voxels]
        values = [(x.xyz_rotated[2], x) for x in voxels]
        values.sort(key = lambda tup: tup[0])
        min_list = [val for (key, val) in values]
        return min_list

    def add_voxels(self, voxel):
        voxel.superior = self
        self.voxels.append(voxel)
        voxel.currency = len(self.voxels) - 1

    def insert_voxels(self, candidate):
        self.voxels = list(candidate[::-1] + self.voxels)

    def validate_voxels(self):
        voxel = None
        for x, i in enumerate(self.voxels):
            if i == voxel:
                continue
            i.currency = x
            try:
                i.label = label[x]
            except:
                pass
            if voxel == None:
                voxel = i

    def delete_voxels(self):
        voxels = self.collected
        if not voxels:
            v = self.voxels[self.highlighted]
            v.collect_all_child_voxels(self.collected)
            self.remove_highlighted()
        else:
            self.clear_collected()
            self.remove_highlight()
            self.remove_voxels(voxels)
        v = self.get_highlight(0)
        return 0

    def delete_voxel(self, candidates):
        p = None
        for i in candidates:
            if i < len(self.voxels) and len(self.voxels) > 1:
                if self.voxels[i].level < 1.0:
                    self.voxels[i].turn_invisible()
                    p = self.voxels.pop(i)
        self.validate_voxels()
        return p

    def remove_voxels(self, voxels, validate = True):
        #self.remove_highlight()
        remove_list = []
        for i in voxels:
            if i.level < 1.0:
                remove_list.append(i)
                i.turn_invisible()
        self.voxels = list(set(self.voxels) - set(remove_list))
        if validate:
            self.validate_voxels()

    def move_around(self, center = (0, 0, 0)):
        self.position = (self.position[0] + center[0], self.position[1] + center[1], self.position[2] + center[2])
        for i in self.child_voxel:
            i.move_around(self.position)

    def reset_position(self, reset = True):
        conform_position = [-self.conform_position[0],
                            -self.conform_position[1],
                            -self.conform_position[2]]
        voxels = self.child_voxel
        for i in voxels:
            i.move_conform(conform_position)
        for dim in self.visibility_array.keys():
            self.coords_array[dim] += array(conform_position)
        if reset:
            self.conform_position[:] = [0, 0, 0]

    def move_conform(self, center = (0, 0, 0)):
        self.conform_position[0] += center[0]
        self.conform_position[1] += center[1]
        self.conform_position[2] += center[2]
        voxels = self.child_voxel
        for i in voxels:
            i.move_conform(center)
        for dim in self.visibility_array.keys():
            self.coords_array[dim] += array(center)

    def move_to_conform(self, center = (0, 0, 0)):
        voxels = self.child_voxel
        for i in voxels:
            i.move_conform(center)
        for dim in self.visibility_array.keys():
            self.coords_array[dim] += array(center)

    def add_conform_positions(self):
        self.local_conform += self.conform_position
        self.local_position = self.local_conform
        self.conform_position.fill(0.0)

    def switch_conform_position(self):
        self.local_conform = self.conform_position
        self.conform_position = self.local_position
        self.local_position = self.local_conform
        print(self.local_conform)
        print(self.conform_position)
        print(self.local_position)

    def offset_3d_baked_vector(self, local, center, vector):
        for dim in self.visibility_array.keys():
            #if sum(self.visibility_array[dim]):
            coords = self.baked_array[dim].copy()
            coords -= local

            x = coords[:, 0]
            y = coords[:, 1]
            z = coords[:, 2]
            X = vector[2][0] * z + vector[1][0] * y + vector[0][0] * x + center[0]
            Y = vector[2][1] * z + vector[1][1] * y + vector[0][1] * x + center[1]
            Z = vector[2][2] * z + vector[1][2] * y + vector[0][2] * x + center[2]

            self.rotated_array[dim][:, 0] = X
            self.rotated_array[dim][:, 1] = Y
            self.rotated_array[dim][:, 2] = Z

    def offset_3d_vector(self, center, vector):
        for dim in self.visibility_array.keys():
            #if sum(self.visibility_array[dim]):
            coords = self.coords_array[dim].copy()

            x = coords[:, 0]
            y = coords[:, 1]
            z = coords[:, 2]
            X = vector[2][0] * z + vector[1][0] * y + vector[0][0] * x + center[0]
            Y = vector[2][1] * z + vector[1][1] * y + vector[0][1] * x + center[1]
            Z = vector[2][2] * z + vector[1][2] * y + vector[0][2] * x + center[2]

            self.rotated_array[dim][:, 0] = X
            self.rotated_array[dim][:, 1] = Y
            self.rotated_array[dim][:, 2] = Z

    def bake_xyz_rotation_arrays(self):
        for dim in self.visibility_array.keys():
            self.baked_array[dim][:] = self.coords_array[dim][:]
            self.coords_array[dim][:] = self.rotated_array[dim][:]

    def bake_rotation_arrays(self):
        for dim in self.visibility_array.keys():
            self.coords_array[dim][:] = self.rotated_array[dim][:]

    def bake_xyz_rotation(self):
        self.xyz_baked = True
        for i in self.child_nodes:
            i.xyz_baked = True
        for i in self.child_voxel:
            i.rotate_around_vector(self.parent.center, self.parent.vector, self.parent.angle)
            i.bake_xyz_rotation()
        V = self.cube.return_offset_vectors()
        self.offset_3d_vector(self.parent.center, V)
        for i in set(self.voxels):
            i.bake_xyz_rotation()
        #self.bake_xyz_rotation_arrays()

    def bake_rotation(self, center = None, vector = None, angle = None):
        self.baked = True
        for i in self.child_nodes:
            i.baked = True
        for i in self.child_voxel:
            i.rotate_around_vector(center, vector, angle)
            i.bake_rotation()

        V = self.cube.return_offset_vectors()
        local = self.local_conform + self.conform_position
        center = self.cube.give_center_parent()
        self.offset_3d_baked_vector(local, center, V)

    def restore_xyz_baked(self):
        self.baked = False
        self.xyz_baked = False
        for i in self.child_nodes:
            i.baked = False
            i.xyz_baked = False
        voxels = list(set(self.voxels)) + self.child_voxel
        for i in voxels:
            i.restore_xyz_baked()

    def rotate3d_x(self, center = (0, 0, 0), x_angle = 0):
        if screen.OBJ_Mode:
            if self.LOCAL:
                if self.xyz_baked:
                    self.bake_rotation(self.center, self.vector, self.angle)
                else:
                    self.bake_xyz_rotation()
            self.cube3d.rotate3d_x(center, x_angle)
        else:
            if center is None:
                center = self.get_center()
            if x_angle is None:
                self.angle += self.direction
                x_angle = self.angle
            elif x_angle == "self":
                x_angle = self.get_angle()
            else:
                self.angle = x_angle
            for i in self.child_voxel:
                if self.vec_x != (1, 0, 0):
                    i.rotate_around_vector(center, self.vec_x, x_angle)
                else:
                    i.rotate_at_x(center, x_angle)
            V = self.cube.return_offset_vectors()
            if self.LOCAL:
                local = self.local_conform + self.conform_position
                center = self.cube.give_center_parent()
                self.offset_3d_baked_vector(local, center, V)
            else:
                self.offset_3d_vector(center, V)

    def rotate3d_y(self, center = (0, 0, 0), y_angle = 0):
        if screen.OBJ_Mode:
            if self.LOCAL:
                if self.xyz_baked:
                    self.bake_rotation(self.center, self.vector, self.angle)
                else:
                    self.bake_xyz_rotation()
            self.cube3d.rotate3d_y(center, y_angle)
        else:
            if center is None:
                center = self.get_center()
            if y_angle is None:
                self.angle += self.direction
                y_angle = self.angle
            elif y_angle == "self":
                y_angle = self.get_angle()
            else:
                self.angle = y_angle
            for i in self.child_voxel:
                if self.vec_y != (0, 1, 0):
                    i.rotate_around_vector(center, self.vec_y, y_angle)
                else:
                    i.rotate_at_y(center, y_angle)
            V = self.cube.return_offset_vectors()
            if self.LOCAL:
                local = self.local_conform + self.conform_position
                center = self.cube.give_center_parent()
                self.offset_3d_baked_vector(local, center, V)
            else:
                self.offset_3d_vector(center, V)

    def rotate3d_z(self, center = (0, 0, 0), z_angle = 0):
        if screen.OBJ_Mode:
            if self.LOCAL:
                if self.xyz_baked:
                    self.bake_rotation(self.center, self.vector, self.angle)
                else:
                    self.bake_xyz_rotation()
            self.cube3d.rotate3d_z(center, z_angle)
        else:
            if center is None:
                center = self.get_center()
            if z_angle is None:
                self.angle += self.direction
                z_angle = self.angle
            elif z_angle == "self":
                z_angle = self.get_angle()
            else:
                self.angle = z_angle
            for i in self.child_voxel:
                if self.vec_z != (0, 0, 1):
                    i.rotate_around_vector(center, self.vec_z, z_angle)
                else:
                    i.rotate_at_z(center, z_angle)
            V = self.cube.return_offset_vectors()
            if self.LOCAL:
                local = self.local_conform + self.conform_position
                center = self.cube.give_center_parent()
                self.offset_3d_baked_vector(local, center, V)
            else:
                self.offset_3d_vector(center, V)

    def rotate3d_vector(self, center = (0, 0, 0), vector = (0, 1, 0), angle = 0):
        if screen.OBJ_Mode:
            if self.LOCAL:
                if self.xyz_baked:
                    self.bake_rotation(self.center, self.vector, self.angle)
                else:
                    self.bake_xyz_rotation()
            self.cube3d.rotate3d_vector(center, vector, angle)
        else:
            if center is None:
                center = self.get_center()
            if vector is None:
                vector = self.get_vector()
            if angle is None:
                angle = self.get_angle()
                angle += self.direction
                self.set_angle(angle)
            elif angle == "self":
                angle = self.get_angle()

            for i in self.child_voxel:
                i.rotate_around_vector(center, vector, angle)
            V = self.cube.return_offset_vectors()
            if self.LOCAL:
                local = self.local_conform + self.conform_position
                center = self.cube.give_center_parent()
                self.offset_3d_baked_vector(local, center, V)
            else:
                self.offset_3d_vector(center, V)

class voxel3d_o():
    def __init__(self, coordinates, color,
                 size, level, parent):
        self.parent = parent
        self.currency = None
        self.level = level
        self.x_baked = 0
        self.y_baked = 0
        self.z_baked = 0
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.z = coordinates[2]
        self.x_rotated = self.x
        self.y_rotated = self.y
        self.z_rotated = self.z
        self.x_pos = 0
        self.y_pos = 0
        self.z_pos = 0
        self.superior = None

        self.size = 1.0

    def get_position(self):
        return (self.x, self.y, self.z)

    def get_unchanged(self, conform_position):
        return tuple((self.x, self.y, self.z) - array(conform_position))

    def get_transformed(self):
        return (self.x_rotated, self.y_rotated, self.z_rotated)

    def map_to_screen(self, x, y, s):
        w = screen.width
        h = screen.height
        if w > h:
            w = h
        else:
            h = w
        x = x * w / 2 + w / 2
        y = -y * h / 2 + h / 2
        try:
            s = float(s * w / 4)
        except:
            s = 0
        return (x, y, s)

    def move_conform(self, center):
        self.x += center[0]
        self.y += center[1]
        self.z += center[2]

    def move_around(self, center):
        self.x_pos = center[0]
        self.y_pos = center[1]
        self.z_pos = center[2]

    def bake_xyz_rotation(self):
        self.x_baked = self.x
        self.y_baked = self.y
        self.z_baked = self.z
        self.x = self.x_rotated
        self.y = self.y_rotated
        self.z = self.z_rotated

    def bake_rotation(self):
        self.x = self.x_rotated
        self.y = self.y_rotated
        self.z = self.z_rotated

    def restore_xyz_baked(self):
        self.x = self.x_baked
        self.y = self.y_baked
        self.z = self.z_baked

    def rotate_around_vector(self, center, vector, angle):
        x = self.x - center[0]
        y = self.y - center[1]
        z = self.z - center[2]

        y_x_angle = math.atan2(vector[1], vector[0])

        x_1 = math.cos(-y_x_angle) * x - math.sin(-y_x_angle) * y
        y_1 = math.sin(-y_x_angle) * x + math.cos(-y_x_angle) * y

        l_x_y = math.sqrt(vector[0] * vector[0] + vector[1] * vector[1])
        x_z_angle = math.atan2(-vector[2], l_x_y)

        x_2 = math.cos(-x_z_angle) * x_1 + math.sin(-x_z_angle) * z
        z_2 = -math.sin(-x_z_angle) * x_1 + math.cos(-x_z_angle) * z

        y_3 = math.cos(angle) * y_1 - math.sin(angle) * z_2
        z_3 = math.sin(angle) * y_1 + math.cos(angle) * z_2

        x_4 = math.cos(x_z_angle) * x_2 + math.sin(x_z_angle) * z_3
        z_4 = -math.sin(x_z_angle) * x_2 + math.cos(x_z_angle) * z_3

        x_5 = math.cos(y_x_angle) * x_4 - math.sin(y_x_angle) * y_3
        y_5 = math.sin(y_x_angle) * x_4 + math.cos(y_x_angle) * y_3

        self.x_rotated = x_5 + center[0]
        self.y_rotated = y_5 + center[1]
        self.z_rotated = z_4 + center[2]

    def rotate_at_x(self, center, x_angle):
        y = self.y - center[1]
        z = self.z - center[2]
        y_ = math.cos(x_angle) * y - math.sin(x_angle) * z
        z_ = math.sin(x_angle) * y + math.cos(x_angle) * z
        self.x_rotated = self.x
        self.y_rotated = y_ + center[1]
        self.z_rotated = z_ + center[2]

    def rotate_at_y(self, center, y_angle):
        x = self.x - center[0]
        z = self.z - center[2]
        x_ = math.cos(y_angle) * x + math.sin(y_angle) * z
        z_ = -math.sin(y_angle) * x + math.cos(y_angle) * z
        self.y_rotated = self.y
        self.x_rotated = x_ + center[0]
        self.z_rotated = z_ + center[2]

    def rotate_at_z(self, center, z_angle):
        x = self.x - center[0]
        y = self.y - center[1]
        x_ = math.cos(z_angle) * x - math.sin(z_angle) * y
        y_ = math.sin(z_angle) * x + math.cos(z_angle) * y
        self.z_rotated = self.z
        self.x_rotated = x_ + center[0]
        self.y_rotated = y_ + center[1]

    def give_depth(self, depth):
        if depth == 0:
            factor = scale
        else:
            factor = scale - ((self.z_rotated + self.z_pos) / depth)
        if(factor == 0):
            factor = scale
        x = (self.x_rotated + self.x_pos) / factor
        y = (self.y_rotated + self.y_pos) / factor
        s = self.size / factor
        if s > 2:
            s = 1.9
        elif s < 0:
            s = 0

        return(x, y, s)

    def blit_line(self, depth_factor):
        (x, y, s) = self.give_depth(depth_factor)
        (x, y, s) = self.map_to_screen(x, y, s)
        return (x, y, self.z_rotated * (screen_depth))

    def blit_point(self, depth_factor):
        (x, y, s) = self.give_depth(depth_factor)
        (x, y, s) = self.map_to_screen(x, y, s)
        return (x, y, s)

    def give_cube_vectors(self, depth, radius):
        vectors = self.superior.cube.vectors
        V = [(0.0, 0.0, 0.0)] * 8
        for N, v in enumerate(vectors):
            x_rotated = self.x_rotated + v[0] * radius
            y_rotated = self.y_rotated + v[1] * radius
            z_rotated = self.z_rotated + v[2] * radius
            if depth == 0:
                factor = scale
            else:
                factor = scale - ((z_rotated + self.z_pos) / depth)
            if(factor == 0):
                factor = scale
            x = (x_rotated + self.x_pos) / factor
            y = (y_rotated + self.y_pos) / factor
            #
            w = screen.width
            h = screen.height
            if w > h:
                w = h
            else:
                h = w
            x = x * w / 2 + w / 2
            y = -y * h / 2 + h / 2
            V[N] = (x, y, -z_rotated)
        return V

class voxel3d():
    def __init__(self, spawn, superior, Currency, x, y, z,
                 coords_array, baked_array, rotated_array, color_array, vector_array, size_array,
                 visibility_array, index_array,
                 level, parent, images = None, image = None,
                 OBJ_repro = None, repro = None, texture = None,
                 texName = None):
        self.x = x
        self.y = y
        self.z = z
        self.coordinates = coords_array
        self.baked = baked_array
        self.rotated = rotated_array
        self.colors = color_array
        self.sizes = size_array
        self.visibility = visibility_array
        self.indexes = index_array
        self.currency = 0
        self.Currency = Currency
        self.label = label[0]
        self.highlighted = False
        self.illuminated = False
        self.illu_color = array([0, 0, 0], dtype = int)
        self.parent = parent
        self.level = level
        self.xyz_baked = baked_array[self.Currency]
        self.coords = coords_array[self.Currency]
        self.xyz_rotated = rotated_array[self.Currency]
        self.color = color_array[self.Currency]
        self.vector = vector_array[self.Currency]
        self.size = size_array[self.Currency]
        self.spawned = False
        self.zipped = False
        self.superior = superior
        self.voxels = None
        self.voxels_invisible = None
        self.images = images
        self.image = image
        self.OBJ_repro = OBJ_repro
        self.repro = repro
        self.texture = texture
        self.texName = texName
        self.spin = 0
        self.spin_amount = 0
        self.frame = 0
        self.Frames = 0
        if self.OBJ_repro:
            self.Frames = self.OBJ_repro.Frames
        self.Oscillate = 1

        if spawn:
            BackgroundSpawner.spawn_invisible(self)

    def turn_invisible(self):
        self.visibility[self.x, self.y, self.z] = 0

    def turn_visible(self):
        self.visibility[self.x, self.y, self.z] = 1

    def set_oscillate(self):
        if self.Oscillate:
            self.Oscillate = 0
        else:
            self.Oscillate = 1

    def return_Pos_And_Scale(self):
        if self.OBJ_repro:
            return self.OBJ_repro.return_Pos_And_Scale()
        else:
            return (0, 0, 1.0, 1.0, 1.0)

    def return_Wire_Render(self):
        if self.OBJ_repro:
            return self.OBJ_repro.return_Wire_Render()
        else:
            return (0, 1)

    def set_images(self, Status = True):
        if Status is None:
            self.image = None
            self.images = None
        else:
            self.image = image_name
            self.images = images

    def set_frame(self, frame):
        self.frame = frame

    def set_repro(self, repro = None, OBJ_repro = None,
                  texture = None, texName = None):
        self.repro = repro
        self.OBJ_repro = OBJ_repro
        if self.OBJ_repro:
            self.Frames = self.OBJ_repro.Frames
        else:
            self.Frames = 0
        if texture:
            self.texName = texName
            self.texture = texture

    def set_texture(self, texture, texName):
        self.texName = texName
        self.texture = texture

    def neighbours(self):
        step = self.level * float(2)
        return (
            (self.coords[0], self.coords[1] + step, self.coords[2]),
            (self.coords[0], self.coords[1] - step, self.coords[2]),
            (self.coords[0] + step, self.coords[1], self.coords[2]),
            (self.coords[0] - step, self.coords[1], self.coords[2]),
            (self.coords[0], self.coords[1], self.coords[2] + step),
            (self.coords[0], self.coords[1], self.coords[2] - step),
            (self.coords[0] + step, self.coords[1] + step, self.coords[2] + step),
            (self.coords[0] - step, self.coords[1] + step, self.coords[2] + step),
            (self.coords[0] + step, self.coords[1] + step, self.coords[2] - step),
            (self.coords[0] - step, self.coords[1] + step, self.coords[2] - step),
            (self.coords[0] + step, self.coords[1] - step, self.coords[2] + step),
            (self.coords[0] - step, self.coords[1] - step, self.coords[2] + step),
            (self.coords[0] + step, self.coords[1] - step, self.coords[2] - step),
            (self.coords[0] - step, self.coords[1] - step, self.coords[2] - step),
            (self.coords[0], self.coords[1] + step, self.coords[2] + step),
            (self.coords[0], self.coords[1] + step, self.coords[2] - step),
            (self.coords[0], self.coords[1] - step, self.coords[2] + step),
            (self.coords[0], self.coords[1] - step, self.coords[2] - step),
            (self.coords[0] + step, self.coords[1], self.coords[2] + step),
            (self.coords[0] + step, self.coords[1], self.coords[2] - step),
            (self.coords[0] - step, self.coords[1], self.coords[2] + step),
            (self.coords[0] - step, self.coords[1], self.coords[2] - step),
            (self.coords[0] + step, self.coords[1] + step, self.coords[2]),
            (self.coords[0] + step, self.coords[1] - step, self.coords[2]),
            (self.coords[0] - step, self.coords[1] + step, self.coords[2]),
            (self.coords[0] - step, self.coords[1] - step, self.coords[2])
            )

    def find_parent_recursive_parent(self, center):
        p = self.parent
        if p:
            p.find_parent_recursive_parent(center)
        else:
            center[0] = self.xyz_rotated
            return center

    def find_parent_recursive(self, collect):
        p = self.parent
        if p:
            p.find_parent_recursive(collect)
        else:
            collect.append(self)

    def clear_highlight(self):
        self.highlighted = False

    def set_illumination(self):
        if not self.illuminated:
            self.illuminated = True
            self.illu_color[:] = self.color[:]
            self.color[:] = self.superior.highlight_color[:]

    def clear_illumination(self):
        if self.illuminated:
            self.illuminated = False
            self.color[:] = self.illu_color[:]
            self.illu_color[:] = self.superior.highlight_color[:]

    def toggle_illumination(self):
        if self.illuminated:
            self.illuminated = False
            self.color[:] = self.illu_color[:]
            self.illu_color[:] = self.superior.highlight_color[:]
        else:
            self.illuminated = True
            self.illu_color[:] = self.color[:]
            self.color[:] = self.superior.highlight_color[:]

    def get_color(self):
        return self.color

    def get_position(self):
        return tuple(self.coords)

    def get_unchanged(self, conform_position):
        return tuple(self.coords - array(conform_position))

    def get_transformed(self):
        return self.xyz_rotated

    def set_color(self, color):
        self.color[:] = color[:]
        self.illu_color[:] = color[:]

    def get_visibility(self):
        return self.visibility[self.x, self.y, self.z]

    def mix_color(self, color, m, n):
        r = int(self.color[0] * m + color[0] * n)
        g = int(self.color[1] * m + color[1] * n)
        b = int(self.color[2] * m + color[2] * n)
        self.color[:] = (r, g, b)
        self.illu_color[:] = (r, g, b)

    def calc_relative(self):
        if self.parent:
            x = -self.parent.coords[0] + self.coords[0]
            y = self.parent.coords[1] - self.coords[1]
            z = self.parent.coords[2] - self.coords[2]
            if x > 0 and y > 0 and z < 0 : return 0
            if x < 0 and y > 0 and z < 0 : return 1
            if x < 0 and y > 0 and z > 0 : return 5
            if x > 0 and y > 0 and z > 0 : return 4
            if x > 0 and y < 0 and z < 0 : return 3
            if x < 0 and y < 0 and z < 0 : return 2
            if x < 0 and y < 0 and z > 0 : return 6
            if x > 0 and y < 0 and z > 0 : return 7
            return 0
        else:
            return 0

    def spawn_invisible_sub_voxels(self):
        if self.level > self.superior.levelLimit:
            if not self.spawned:
                self.spawned = False
                self.zipped = False
                level = self.level / float(2)
                dimension = int(1.0 / level)
                size = self.size / 2
                if self.voxels == None:
                    if dimension not in self.superior.visibility_array.keys():
                        self.superior.create_arrays(dimension)
                    coordinates = self.superior.coords_array[dimension]
                    baked = self.superior.baked_array[dimension]
                    rotated = self.superior.rotated_array[dimension]
                    colors = self.superior.color_array[dimension]
                    vectors = self.superior.vector_array[dimension]
                    sizes = self.superior.size_array[dimension]
                    visibility = self.superior.visibility_array[dimension]
                    indexes = self.superior.index_array[dimension]
                    coords = self.coords - self.superior.conform_position - self.superior.local_conform
                    self.voxels_invisible = print_voxels(level, size, self, coords, baked, rotated,
                                               self.images, self.image,
                                               self.OBJ_repro, self.repro,
                                               self.texture, self.texName,
                                               coordinates, colors, vectors,
                                               sizes, visibility, indexes,
                                               False, self.superior
                                               )
                    for i in self.voxels_invisible:
                        i.visibility[i.x, i.y, i.z] = 0

    def spawn_sub_voxels(self, withreturn = False, init = False):
        if self.level > self.superior.levelLimit:
            if not self.spawned:
                self.visibility[self.x, self.y, self.z] = 0
                self.spawned = True
                self.zipped = False
                level = self.level / float(2)
                dimension = int(1.0 / level)
                size = self.size / 2
                if self.voxels_invisible:
                    self.voxels = self.voxels_invisible
                if dimension not in self.superior.visibility_array.keys():
                    self.superior.create_arrays(dimension)
                if self.voxels == None:
                    coordinates = self.superior.coords_array[dimension]
                    baked = self.superior.baked_array[dimension]
                    rotated = self.superior.rotated_array[dimension]
                    colors = self.superior.color_array[dimension]
                    vectors = self.superior.vector_array[dimension]
                    sizes = self.superior.size_array[dimension]
                    visibility = self.superior.visibility_array[dimension]
                    indexes = self.superior.index_array[dimension]
                    coords = self.coords - self.superior.conform_position - self.superior.local_conform
                    if init:
                        self.voxels = print_voxels_init(level, size, self, coords, baked, rotated,
                                                   self.images, self.image,
                                                   self.OBJ_repro, self.repro,
                                                   self.texture, self.texName,
                                                   coordinates, colors, vectors,
                                                   sizes, visibility, indexes,
                                                   False, self.superior
                                                   )
                    else:
                        self.voxels = print_voxels(level, size, self, coords, baked, rotated,
                                                   self.images, self.image,
                                                   self.OBJ_repro, self.repro,
                                                   self.texture, self.texName,
                                                   coordinates, colors, vectors,
                                                   sizes, visibility, indexes,
                                                   True, self.superior
                                                   )
                    self.superior.insert_voxels(self.voxels)
                else:
                    for i in self.voxels:
                        i.visibility[i.x, i.y, i.z] = 1
                    self.superior.insert_voxels(self.voxels)
            if withreturn:
                return self.calc_relative()
        else:
            return self.currency

    def set_size_recursive(self):
        if self.spawned:
            size = self.size / 2
            for i in self.voxels:
                i.size[:] = size
                i.set_size_recursive()

    def spawn_recursive(self, level, Zipped = False, validate = True):
        if self.level > level:
            if len(self.superior.voxels) > self.superior.voxelLimit:
                return
            if Zipped and not self.zipped:
                return
            self.spawn_sub_voxels()
            if validate:
                self.superior.validate_voxels()
            for i in self.voxels:
                i.spawn_recursive(level, Zipped, validate)

    def collect_all_child_voxels(self, collected):
        if self.spawned and self.voxels != None:
            for i in self.voxels:
                if i in self.superior.voxels:
                    collected.insert(0, i)
                i.collect_all_child_voxels(collected)

    def collect_voxels(self, validate = True):
        if self.parent and self.parent.spawned:
            self.parent.visibility[self.parent.x, self.parent.y, self.parent.z] = 1
            self.parent.spawned = False
            self.parent.zipped = True
            voxels = self.parent.voxels
            self.superior.remove_voxels(voxels, validate)
            return self.parent.currency
        else:
            return self.currency

    def map_to_screen(self, x, y, s):
        w = screen.width
        h = screen.height
        if w > h:
            w = h
        else:
            h = w
        x = x * w / 2 + w / 2
        y = -y * h / 2 + h / 2
        try:
            s = float(s * w / 4)
        except:
            s = 0
        return (x, y, s)

    def bake_xyz_rotation(self):
        self.xyz_baked[:] = self.coords[:]
        self.coords[:] = self.xyz_rotated[:]

    def bake_rotation(self):
        self.coords[:] = self.xyz_rotated[:]

    def restore_xyz_baked(self):
        self.coords[:] = self.xyz_baked[:]

    def offset_3d_baked_vector(self, local, center, vector):
        x = self.xyz_baked[0] - local[0]
        y = self.xyz_baked[1] - local[1]
        z = self.xyz_baked[2] - local[2]

        x_1 = vector[0][0] * x
        y_1 = vector[0][1] * x
        z_1 = vector[0][2] * x

        x_2 = vector[1][0] * y + x_1
        y_2 = vector[1][1] * y + y_1
        z_2 = vector[1][2] * y + z_1

        x_3 = vector[2][0] * z + x_2
        y_3 = vector[2][1] * z + y_2
        z_3 = vector[2][2] * z + z_2

        self.xyz_rotated[0] = x_3 + center[0]
        self.xyz_rotated[1] = y_3 + center[1]
        self.xyz_rotated[2] = z_3 + center[2]

    def offset_3d_vector(self, center, vector):
        x = self.coords[0]
        y = self.coords[1]
        z = self.coords[2]

        x_1 = vector[0][0] * x
        y_1 = vector[0][1] * x
        z_1 = vector[0][2] * x

        x_2 = vector[1][0] * y + x_1
        y_2 = vector[1][1] * y + y_1
        z_2 = vector[1][2] * y + z_1

        x_3 = vector[2][0] * z + x_2
        y_3 = vector[2][1] * z + y_2
        z_3 = vector[2][2] * z + z_2

        self.xyz_rotated[0] = x_3 + center[0]
        self.xyz_rotated[1] = y_3 + center[1]
        self.xyz_rotated[2] = z_3 + center[2]

    def give_depth(self, depth):
        if depth == 0:
            factor = scale
        else:
            factor = scale - ((self.xyz_rotated[2] + self.superior.position[2]) / depth)
        if(factor == 0):
            factor = scale
        x = (self.xyz_rotated[0] + self.superior.position[0]) / factor
        y = (self.xyz_rotated[1] + self.superior.position[1]) / factor
        s = self.size / factor
        if s > 2:
            s = 1.9
        elif s < 0:
            s = 0

        return(x, y, s)

    def blit_line(self, depth_factor):
        (x, y, s) = self.give_depth(depth_factor)
        (x, y, s) = self.map_to_screen(x, y, s)
        return (x, y, self.xyz_rotated[2] * (screen_depth))

    def blit_point(self, depth_factor):
        (x, y, s) = self.give_depth(depth_factor)
        (x, y, s) = self.map_to_screen(x, y, s)
        return (x, y, s)

    def give_cube_vectors(self, depth, radius):
        vectors = self.superior.cube.vectors
        V = [(0.0, 0.0, 0.0)] * 8
        for N, v in enumerate(vectors):
            x_rotated = self.xyz_rotated[0] + v[0] * radius
            y_rotated = self.xyz_rotated[1] + v[1] * radius
            z_rotated = self.xyz_rotated[2] + v[2] * radius
            if depth == 0:
                factor = scale
            else:
                factor = scale - ((z_rotated + self.superior.position[2]) / depth)
            if(factor == 0):
                factor = scale
            x = (x_rotated + self.superior.position[0]) / factor
            y = (y_rotated + self.superior.position[1]) / factor
            #
            w = screen.width
            h = screen.height
            if w > h:
                w = h
            else:
                h = w
            x = x * w / 2 + w / 2
            y = -y * h / 2 + h / 2
            V[N] = (x, y, -z_rotated)
        return V

    def blit_at(self, depth_factor, i, L, draft = True, images = None, VectorAnimation = None, angle = 0):
        if self.visibility[self.x, self.y, self.z] or self.currency == self.superior.highlighted:
            (x, y, s) = self.give_depth(depth_factor)
            (x, y, s) = self.map_to_screen(x, y, s)
            self.spin += self.spin_amount
            S = int(s)
            if S > for_depth_divisions - 2:
                S = for_depth_divisions - 2
            if s > 0:
                size = images[S].get_size()
                coordinates = (int(x - size[0] / 2), int(y - size[1] / 2))
                (x0, y0, x1, y1) = (int(x - size[0] / 2), int(y - size[1] / 2),
                                    size[0], size[1])
                radius = s * 1.75
                if draft:
                    if screen.SDL_Mode:
                        if self.texture is None or self.superior.propagate:
                            texture = self.superior.texture
                        else:
                            texture = self.texture
                        if self.highlighted:
                            color = h_color
                        else:
                            color = self.color
                        if screen.alphamode:
                            alpha = (i + 1) / float(L + 1)
                        else:
                            alpha = 1.0
                        glColor4fv((float(color[0]/255.0),
                                    float(color[1]/255.0),
                                    float(color[2]/255.0),
                                    float(alpha)))
                        screen.draw_GL_Circle((float(x), float(y), float(-self.xyz_rotated[2] * screen_depth)),
                                              float(radius), 4, texture)
                    else:
                        if self.illuminated:
                            if self.highlighted:
                                pygame.draw.ellipse(screen.surface, h_color, (x0, y0, x1, y1), 0)
                            else:
                                pygame.draw.ellipse(screen.surface, i_color, (x0, y0, x1, y1), 0)
                        else:
                            pygame.draw.ellipse(screen.surface, self.color, (x0, y0, x1, y1), 0)
                else:
                    if screen.SDL_Mode:
                        if screen.Frames:
                            if self.Oscillate:
                                self.frame += screen.Tween * self.Oscillate
                            else:
                                self.frame += screen.Tween
                        if self.OBJ_repro is None or self.superior.propagate:
                            OBJ = self.superior.OBJ_repro
                            if not OBJ:
                                pass
                            elif self.frame >= self.superior.OBJ_repro.Frames:
                                if self.Oscillate:
                                    self.Oscillate = -1
                                    self.frame = self.superior.OBJ_repro.Frames - 1
                                else:
                                    self.frame = 0
                            elif self.frame < 0:
                                if self.Oscillate:
                                    self.Oscillate = 1
                                self.frame = 0
                        else:
                            OBJ = self.OBJ_repro
                            if not OBJ:
                                pass
                            elif self.frame >= self.OBJ_repro.Frames:
                                if self.Oscillate:
                                    self.Oscillate = -1
                                    self.frame = self.OBJ_repro.Frames - 1
                                else:
                                    self.frame = 0
                            elif self.frame < 0:
                                if self.Oscillate:
                                    self.Oscillate = 1
                                self.frame = 0
                        frame = self.frame
                        if self.texture is None or self.superior.propagate:
                            texture = self.superior.texture
                        else:
                            texture = self.texture
                        if self.highlighted:
                            color = h_color
                        else:
                            color = self.color
                        if screen.alphamode:
                            alpha = (i + 1) / float(L + 1)
                        else:
                            alpha = 1.0

                        Color = (float(color[0]/255.0),
                                 float(color[1]/255.0),
                                 float(color[2]/255.0),
                                 float(alpha))
                        glColor4fv(Color)
                        if self.superior.GL_depth_cued:
                            vectors = self.give_cube_vectors(depth_factor, float(self.size / 1.5))
                            screen.draw_GL_Cube_In_View(vectors, texture)
                        elif OBJ:
                            if VectorAnimation:
                                Vector = (self.vector[0], self.vector[1], self.vector[2])
                            else:
                                Vector = None
                            screen.draw_GL_Repro((float(x), float(y), float(-self.xyz_rotated[2] * screen_depth)),
                                                 float(radius), OBJ, texture, angle,
                                                 self.superior.local, self.spin, frame, self.Oscillate, Color, Vector = Vector)
                        else:
                            screen.draw_GL_Cube((float(x), float(y), float(-self.xyz_rotated[2] * screen_depth)),
                                                float(radius), self.superior.cube.vectors, texture)
                    else:
                        if self.images is None or self.superior.propagate:
                            if self.superior.images:
                                surf = self.superior.images[S].copy()
                            else:
                                surf = images[S].copy()
                        else:
                            surf = self.images[S].copy()

                        if screen.blurred or screen.median or screen.edge:
                            blur_radius = L / (i + 1)
                            if blur_radius > size[0] / 6:
                                blur_radius = size[0] / 6
                            img_array = pygame.image.tostring(surf, "RGBA")

                            pil_image = Image.frombuffer("RGBA", size, img_array, 'raw', "RGBA", 0, 1)
                            if screen.median:
                                pil_image = pil_image.filter(ImageFilter.MedianFilter(size = 5))
                            if screen.blurred:
                                pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius = blur_radius))
                            if screen.edge:
                                pil_image = pil_image.filter(ImageFilter.FIND_EDGES)

                            surf = pygame.image.frombuffer(pil_image.tobytes("raw", "RGBA"), size, "RGBA")

                        if screen.banding or screen.noise:
                            img_array = pygame.surfarray.array2d(surf)
                            if screen.noise:
                                img_array[::2][::random.randint(1, size[0])] //= 2
                            if screen.banding:
                                img_array[:][::2] += 100
                            surf = pygame.image.frombuffer(img_array, size, "RGBA")

                        if screen.alphamode or screen.h_banding:
                            alpha = pygame.surfarray.pixels_alpha(surf)
                            if screen.h_banding:
                                alpha = alpha.transpose()
                                alpha[:][::2] = 0
                                alpha = alpha.transpose()
                            if screen.alphamode:
                                alpha //= int((L + 1) / float(i + 1))
                            del alpha

                        img = imagesRGB[S]

                        if self.illuminated:
                            if self.highlighted:
                                img.fill((255, 255, 255))
                            else:
                                img.fill((255, 255, 0))
                                p = size[0] / 4
                                img.blit(self.label, (p, p))
                        else:
                            try:
                                img.fill(tuple(self.color))
                            except:
                                print("color", self.color)
                        surf.blit(img, (0, 0), special_flags = screen.SPECIAL_FLAG)
                        screen.surface.blit(surf, (x - size[0] / 2, y - size[1] / 2))
                if self.superior.create_picmap:
                    t = (int(x), int(y))
                    if t in screen.screen_voxel:
                        screen.screen_voxel[t].append(self.currency)
                    else:
                        screen.screen_voxel[t] = [self.currency,]
                    screen.pixelmap_picking.paste(S, coordinates, size, self.currency, i)

image_name = None
images = []
loaded_image_name = None
loaded_images = []
imagesRGB = []
imagesRGBA = []
vector = (0, 1, 0)
masks = []
maskimages = []
alphas = []
label = []

def add_visibility_matrix(dim, coords, coords_array, color_array, size_array, visibility_array, index_array, position, color, size):
    level = 1.0 / float(dim)
    x = int((((position[0] + coords[0]) / level) + dim) / 2)
    y = int((((position[1] + coords[1]) / level) + dim) / 2)
    z = int((((position[2] + coords[2]) / level) + dim) / 2)
    i = index_array[x, y, z]
    visibility_array[x, y, z] = 1
    #coords_array[i] = position
    color_array[i] = color
    size_array[i] = size
    return i, x, y, z

def print_voxels(level, size, parent, coords, baked, rotated, images = None, image = None, OBJ_repro = None,
                 repro = None, texture = None, texName = None, coordinates = None,
                 colors = None, vectors = None, sizes = None, visibility = None, indexes = None,
                 spawn = True, superior = None):
    v = []
    positions = (( level,  level, -level), (-level,  level, -level), (-level,  level,  level), ( level,  level,  level),
                 ( level, -level, -level), (-level, -level, -level), (-level, -level,  level), ( level, -level,  level))
    cols = ((255, 100, 0), (0, 255, 0), (255, 0, 255), (255, 0, 0),
              (0, 0, 0), (0, 0, 255), (255, 100, 255), (255, 100, 0))
    dim = int(1.0 / level)
    for pos, col in zip(positions, cols):
        Currency, x, y, z = add_visibility_matrix(dim, coords, coordinates, colors, sizes, visibility, indexes, pos, col, size)
        voxel = voxel3d(spawn, superior, Currency, x, y, z, coordinates, baked, rotated, colors, vectors, sizes, visibility, indexes, level, parent, images, image, OBJ_repro, repro, texture, texName)
        v.append(voxel)
    return v

def print_voxels_init(level, size, parent, coords, baked, rotated, images = None, image = None, OBJ_repro = None,
                 repro = None, texture = None, texName = None, coordinates = None,
                 colors = None, vectors = None, sizes = None, visibility = None, indexes = None,
                 spawn = True, superior = None):
    v = []
    positions = (( level,  level, -level), (-level,  level, -level), (-level,  level,  level), ( level,  level,  level),
                 ( level, -level, -level), (-level, -level, -level), (-level, -level,  level), ( level, -level,  level))
    dim = int(1.0 / level)
    level = 1.0 / float(dim)
    for pos in positions:
        x = int(((pos[0] + coords[0]) / level) + dim) // 2
        y = int(((pos[1] + coords[1]) / level) + dim) // 2
        z = int(((pos[2] + coords[2]) / level) + dim) // 2
        Currency = indexes[x, y, z]
        voxel = voxel3d(spawn, superior, Currency, x, y, z, coordinates, baked, rotated, colors, vectors, sizes, visibility, indexes, level, parent, images, image, OBJ_repro, repro, texture, texName)
        v.append(voxel)
    return v

def init_images(image, rot_amount, rot_combine = False, from_folder = False):
    global image_name
    global images
    global for_depth_divisions
    global loaded_image_name
    global loaded_images
    global masks, maskimages
    global alphas

    if psutil_enable:
        v = psutil.virtual_memory().percent
    else:
        v = 0.0
    if v > mem_Limit:
        return

    print("screen preMultCol", screen.preMultCol)

    try:
        if screen.preMult:
            image_x = Image.open(os.path.join('', image)).convert('RGBA')
            transparent = Image.new("RGBA", image_x.size, screen.preMultCol)
            comp_premult = Image.composite(image_x, transparent, image_x)
            image_1 = pygame.image.frombuffer(array(comp_premult), image_x.size, "RGBA")
        else:
            image_1 = pygame.image.load(os.path.join('', image))
    except:
        print(str(image) + " not found or file scrambled")
        return

    if from_folder:
        (path, name) = os.path.split(image)
        extension = name[-3:]
        R = re.match(r'(\D*)(\d*)', name)
        from_images = []
        if os.path.isdir(path):
            dirs = []
            imgList = []
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
                            imgList.append(i)
                    else:
                        imgList.append(i)
            for i in imgList:
                try:
                    if screen.preMult:
                        Ix = Image.open(os.path.join(path, i)).convert('RGBA')
                        transparent = Image.new("RGBA", Ix.size, screen.preMultCol)
                        comp_premult = Image.composite(Ix, transparent, Ix)
                        I = pygame.image.frombuffer(array(comp_premult), Ix.size, "RGBA")
                    else:
                        I = pygame.image.load(os.path.join(path, i))
                except:
                    print("not found or file scrambled")
                    continue
                from_images.append(I)

    loaded_images = images

    loaded_image_name = image_name
    image_name = image
    images = []

    width = canvas_w
    height = canvas_h

    if canvas_w > canvas_h:
        for_depth_divisions = int(canvas_h / 2)
    else:
        for_depth_divisions = int(canvas_w / 2)

    sizemultiplyer = 2.85

    if len(maskimages) < for_depth_divisions:
        l = len(maskimages)
        i_mage1 = pygame.image.load(os.path.join('', 'Maailmapunkt_Gray.png'))
        for i in range(l, for_depth_divisions):
            width = i * sizemultiplyer
            height = i * sizemultiplyer
            img4 = pygame.transform.smoothscale(i_mage1, (int(width), int(height)))
            alpha = pygame.surfarray.pixels_alpha(img4)
            alpha = alpha.transpose()
            A = Image.fromarray(alpha)
            alphas.append(A)
            alpha3 = alpha.view(uint8)
            alpha3[:] = divide(alpha3, 128)
            masks.append(alpha3)

            alpha1 = multiply(alpha, 255)
            alpha2 = alpha1.astype(uint8)
            img1 = Image.fromarray(alpha2)
            maskimages.append(img1)

    n = 0
    for i in range(1, for_depth_divisions):
        width = i * sizemultiplyer
        height = i * sizemultiplyer
        image_2 = image_1
        if from_folder and from_images:
            image_1 = from_images[n]
            n += 1
            if n >= len(from_images):
                n = 0
            image_2 = image_1
        if rot_amount > 0:
            r = random.randint(-rot_amount, rot_amount)
            img1 = pygame.transform.rotate(image_1, r)
            (w, h) = img1.get_size()
            (W, H) = image_1.get_size()
            if rot_combine:
                img2 = image_1.copy()
            else:
                img2 = pygame.Surface((W, H), SWSURFACE|SRCALPHA, 32)
            img2.blit(img1, ((W - w) / 2, (H - h) / 2))
            image_2 = img2
        try:
            img = pygame.transform.smoothscale(image_2, (int(width / Blur_master), int(height / Blur_master)))
        except:
            img = loaded_images[i - 1]
        try:
            img3 = pygame.Surface((width, height), SWSURFACE|SRCALPHA, 32)
            img3.blit(img, ((width - int(width / Blur_master)) / 2, (height - int(height / Blur_master)) / 2))
        except:
            img3 = img
        images.append(img3)

def restore_images_to_loaded():
    global images
    global loaded_images
    global image_name
    global loaded_image_name
    buf = images
    images = loaded_images
    loaded_images = buf
    buf = image_name
    image_name = loaded_image_name
    loaded_image_name = buf


def init_objects(pic_image):
    global label
    global images
    global imagesRGB
    global imagesRGBA
    global screen
    global masks, maskimages
    global alphas, for_depth_divisions
    global loaded_images
    global image_name
    global BackgroundSpawner

    screen = Screen(canvas_w, canvas_h, datatype, None)
    image = pygame.image.load(os.path.join('', pic_image))
    image1 = pygame.image.load(os.path.join('', 'Maailmapunkt_Gray.png'))
    imageRGB = pygame.Surface((canvas_w, canvas_h), SWSURFACE|SRCALPHA, 32)
    imageRGB.fill((255, 0, 0))

    pygame.display.set_caption('First Class!')

    width = canvas_w
    height = canvas_h

    if canvas_w > canvas_h:
        for_depth_divisions = canvas_h /2
    else:
        for_depth_divisions = canvas_w /2

    #sizemultiplyer = canvas_h / float(for_depth_divisions)
    sizemultiplyer = 2.85

    for i in range(1, int(for_depth_divisions)):
        width = i * sizemultiplyer
        height = i * sizemultiplyer
        img = pygame.transform.smoothscale(image, (int(width / Blur_master), int(height / Blur_master)))
        img3 = pygame.Surface((width, height), SWSURFACE|SRCALPHA, 32)
        img3.blit(img, ((width - int(width / Blur_master)) / 2, (height - int(height / Blur_master)) / 2))
        images.append(img3)
        imgRGB = pygame.transform.scale(imageRGB, (int(width), int(height)))
        imagesRGB.append(imgRGB)

        img4 = pygame.transform.smoothscale(image1, (int(width), int(height)))
        alpha = pygame.surfarray.pixels_alpha(img4)
        alpha = alpha.transpose()
        A = Image.fromarray(alpha)
        alphas.append(A)
        alpha3 = alpha.view(uint8)
        alpha3[:] = divide(alpha3, 128)
        masks.append(alpha3)

        alpha1 = multiply(alpha, 255)
        alpha2 = alpha1.astype(uint8)
        img1 = Image.fromarray(alpha2)
        maskimages.append(img1)

    image_name = pic_image
    loaded_images = images

    mask = masks[4]
    size = mask.shape
    print(mask)
    print(size)
    print(mask.size)

    maskimage = maskimages[8]

    #maskimage.save('maskimage.png')

    image = images[8]

    #image.save('image.png')

    alpha = alphas[8]

    #alpha.save('alpha.png')

    for x in range(size[0]):
        N = []
        for y in range(size[1]):
            n = mask[x][y]
            N.append(n)
        print(N)

    def give_label(n):
        img = pygame.Surface((20, 20), SWSURFACE|SRCALPHA, 32)
        img.fill(backgroundcolor)
        img_plaster = fonts[0].render(n, True, fontcolor, backgroundcolor)
        img.blit(img_plaster, (0, 0), special_flags = BLEND_ADD)
        return img

    for i in range(voxel_limit * 2):
        label.append(give_label(str(i)))

    object1 = object3d(position = (0, 0, 0), name = "object1", pic_index = -1, images = images, image = image_name)

    object2 = object3d(position = (2, 0, 0), name = "object2", pic_index = -2, images = images, image = image_name)

    object3 = object3d(position = (4, 0, 0), name = "object3", pic_index = -3, images = images, image = image_name)

    object4 = object3d(position = (6, 0, 0), name = "object4", pic_index = -4, images = images, image = image_name)


    object1.create_arrays(1)
    object2.create_arrays(1)
    object3.create_arrays(1)
    object4.create_arrays(1)

    objects = [object1, object2, object3, object4]

    init_arrays(objects)

    BackgroundSpawner = background_spawner()

    v0 = voxel3d(True, object1, 0, 0, 0, 0, coords_array = object1.coords_array[1],
                    baked_array = object1.baked_array[1],
                    rotated_array = object1.rotated_array[1],
                    color_array = object1.color_array[1],
                    vector_array = object1.vector_array[1],
                    size_array = object1.size_array[1],
                    visibility_array = object1.visibility_array[1],
                    index_array = object1.index_array[1],
                    level = 1.0, parent = None)

    v1 = voxel3d(True, object2, 0, 0, 0, 0, coords_array = object2.coords_array[1],
                    baked_array = object2.baked_array[1],
                    rotated_array = object2.rotated_array[1],
                    color_array = object2.color_array[1],
                    vector_array = object2.vector_array[1],
                    size_array = object2.size_array[1],
                    visibility_array = object2.visibility_array[1],
                    index_array = object2.index_array[1],
                    level = 1.0, parent = None)

    v2 = voxel3d(True, object3, 0, 0, 0, 0, coords_array = object3.coords_array[1],
                    baked_array = object3.baked_array[1],
                    rotated_array = object3.rotated_array[1],
                    color_array = object3.color_array[1],
                    vector_array = object3.vector_array[1],
                    size_array = object3.size_array[1],
                    visibility_array = object3.visibility_array[1],
                    index_array = object3.index_array[1],
                    level = 1.0, parent = None)

    v3 = voxel3d(True, object4, 0, 0, 0, 0, coords_array = object4.coords_array[1],
                    baked_array = object4.baked_array[1],
                    rotated_array = object4.rotated_array[1],
                    color_array = object4.color_array[1],
                    vector_array = object4.vector_array[1],
                    size_array = object4.size_array[1],
                    visibility_array = object4.visibility_array[1],
                    index_array = object4.index_array[1],
                    level = 1.0, parent = None)

    object1.voxels = [v0,]
    object2.voxels = [v1,]
    object3.voxels = [v2,]
    object4.voxels = [v3,]

    v0.superior = object1
    v1.superior = object2
    v2.superior = object3
    v3.superior = object4

    return screen, object1, object2, object3, object4, [v0,]

def init_object(position, name, pic_index):
    global images
    global image_name
    object1 = object3d(position = position, name = name, pic_index = pic_index, images = images, image = image_name)
    object1.create_arrays(1)
    objects = [object1,]

    init_arrays(objects)

    v0 = voxel3d(True, object1, 0, 0, 0, 0, coords_array = object1.coords_array[1],
                    baked_array = object1.baked_array[1],
                    rotated_array = object1.rotated_array[1],
                    color_array = object1.color_array[1],
                    vector_array = object1.vector_array[1],
                    size_array = object1.size_array[1],
                    visibility_array = object1.visibility_array[1],
                    index_array = object1.index_array[1],
                    level = 1.0, parent = None)

    object1.voxels = [v0,]

    v0.superior = object1

    return object1, [v0,]

def init_arrays(objects):
    for o in objects:
        o.visibility_array[1][0, 0, 0] = 1
        o.coords_array[1][0] = o.conform_position
        o.color_array[1][0] = (255, 0, 0)
        o.vector_array[1][0] = (0.0, 0.0, 1.0)
        o.size_array[1][0] = 2.0

class Cube3d():
    def __init__(self):

        self.verts = v = [tuple] * 8
        v[0] = ( 1.0, -1.0,  1.0)
        v[1] = ( 1.0,  1.0,  1.0)
        v[2] = (-1.0,  1.0,  1.0)
        v[3] = (-1.0, -1.0,  1.0)
        v[4] = ( 1.0, -1.0, -1.0)
        v[5] = ( 1.0,  1.0, -1.0)
        v[6] = (-1.0,  1.0, -1.0)
        v[7] = (-1.0, -1.0, -1.0)

        self.faces = f = [tuple] * 6
        f[0] = (0, 1, 2, 3)
        f[1] = (7, 6, 5, 4)
        f[2] = (1, 5, 6, 2)
        f[3] = (0, 3, 7, 4)
        f[4] = (3, 2, 6, 7)
        f[5] = (0, 4, 5, 1)

        self.normals = n = [tuple] * 6
        n[0] = ( 0,  0,  1)
        n[1] = ( 0,  0, -1)
        n[2] = ( 0,  1,  0)
        n[3] = ( 0, -1,  0)
        n[4] = (-1,  0,  0)
        n[5] = ( 1,  0,  0)

        self.uvtex = uv = [tuple] * 14
        uv[0] = (0, 0.3333)
        uv[1] = (0, 0.6666)
        uv[2] = (0.3333, 0)
        uv[3] = (0.3333, 0.3333)
        uv[4] = (0.3333, 0.6666)
        uv[5] = (0.3333, 1)
        uv[6] = (0.6666, 0)
        uv[7] = (0.6666, 0.3333)
        uv[8] = (0.6666, 0.6666)
        uv[9] = (0.6666, 1)
        uv[10] = (1, 0.3333)
        uv[11] = (1, 0.6666)
        uv[12] = (1.3333, 0.3333)
        uv[13] = (1.3333, 0.6666)

        self.uvs = uvs = [tuple] * 6
        uvs[0] = (3, 4, 8, 7)
        uvs[1] = (10, 11, 13, 12)
        uvs[2] = (4, 5, 9, 8)
        uvs[3] = (3, 7, 6, 2)
        uvs[4] = (7, 8, 11, 10)
        uvs[5] = (3, 0, 1, 4)

        self.texture = 0

    def load_id_transform(self, angle, vector):
        pass

    def load_id(self, center, radius, angle, vector, baked_angle, vector_c):
        radius /= 2.0
        self.verts = v = [tuple] * 8
        v[0] = ( 1.0, -1.0,  1.0)
        v[1] = ( 1.0,  1.0,  1.0)
        v[2] = (-1.0,  1.0,  1.0)
        v[3] = (-1.0, -1.0,  1.0)
        v[4] = ( 1.0, -1.0, -1.0)
        v[5] = ( 1.0,  1.0, -1.0)
        v[6] = (-1.0,  1.0, -1.0)
        v[7] = (-1.0, -1.0, -1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(float(center[0]), float(center[1]), float(center[2]))
        glRotatef(float(rad2deg(baked_angle)), float(vector_c[0]), float(-vector_c[1]), float(vector_c[2]))
        glRotatef(float(rad2deg(angle)), float(vector[0]), float(-vector[1]), float(vector[2]))
        glScalef(float(radius), float(-radius), float(-radius))

    def set_positions(self, vectors):
        self.verts = vectors

    def set_size_and_position(self, center, radius, vectors):
        self.verts[0] = (radius * vectors[0][0] + center[0], radius * vectors[0][1] + center[1], radius * vectors[0][2] + center[2])
        self.verts[1] = (radius * vectors[1][0] + center[0], radius * vectors[1][1] + center[1], radius * vectors[1][2] + center[2])
        self.verts[2] = (radius * vectors[2][0] + center[0], radius * vectors[2][1] + center[1], radius * vectors[2][2] + center[2])
        self.verts[3] = (radius * vectors[3][0] + center[0], radius * vectors[3][1] + center[1], radius * vectors[3][2] + center[2])
        self.verts[4] = (radius * vectors[4][0] + center[0], radius * vectors[4][1] + center[1], radius * vectors[4][2] + center[2])
        self.verts[5] = (radius * vectors[5][0] + center[0], radius * vectors[5][1] + center[1], radius * vectors[5][2] + center[2])
        self.verts[6] = (radius * vectors[6][0] + center[0], radius * vectors[6][1] + center[1], radius * vectors[6][2] + center[2])
        self.verts[7] = (radius * vectors[7][0] + center[0], radius * vectors[7][1] + center[1], radius * vectors[7][2] + center[2])

    def render(self, mode = GL_QUADS):
        for x in range(len(self.faces)):
            face = self.faces[x]
            glNormal3fv(self.normals[x])
            uvs = self.uvs[x]
            glBegin(mode)
            for y, i in enumerate(face):
                glTexCoord2f(self.uvtex[uvs[y]][0], self.uvtex[uvs[y]][1])
                glVertex3fv(self.verts[i])
            glEnd()


class Screen():
    def __init__(self, w, h, t, image = None):
        self.cube = Cube3d()
        self.screen_voxel = {}
        self.width = w
        self.height = h
        self.datatype = t
        self.image = image
        self.surface = pygame.Surface((w, h), SWSURFACE|SRCALPHA, 32)
        self.pixelmap_picking = picking(w, h, t = t)
        self.alpha = pygame.Surface((w, h), SWSURFACE|SRCALPHA, 32)
        self.SDL_Mode = False
        self.OBJ_Mode = False
        self.OBJ = None
        self.baked_c = 0.0
        self.vector_c = (0, 1, 0)
        self.WireFrame = False
        self.polyDraw = GL_POLYGON
        self.img = None
        self.uvs = [(1, 0), (0, 0), (0, 1), (1, 1)]
        self.random_rot = 0
        self.texture = True
        self.Empty_texture = None
        self.Ground_texture = None
        self.GroundImage = image_folder + ground_image
        self.backgroundImage = None
        self.Background_texture = None
        self.BackgroundImage = image_folder + background_image
        self.BackgroundAlpha = 0
        self.texNamesList = dict()
        self.Texture = []
        self.LoadedImages = dict()
        self.objFileNames = dict()
        self.obj_transforms = []
        self.VBO = True
        self.Frames = True
        self.Tween = 0.5
        self.SPECIAL_FLAG = BLEND_ADD
        self.blurred = False
        self.noise = False
        self.banding = False
        self.median = False
        self.edge = False
        self.alphamode = False
        self.preMultCol = (255, 0, 0, 0)
        self.preMult = False
        self.h_banding = False

    def testCursor(self, arrow):
        hotspot = 0, 0
        s2 = []
        for line in arrow:
            s2.append(line.replace('1', '.').replace('0', 'X'))
        cursor, mask = pygame.cursors.compile(s2, 'X', '.', 'o')
        size = len(arrow[0]), len(arrow)
        pygame.mouse.set_cursor(size, hotspot, cursor, mask)

    def set_Tween(self, value):
        if value:
            self.Tween = 0.5
        else:
            self.Tween = 1

    def set_Frames(self, value):
        self.Frames = value

    def renew_objects(self, w, h):
        self.screen_voxel = {}
        self.width = w
        self.height = h
        if self.SDL_Mode:
            self.resize_SDL()
        else:
            self.surface = pygame.Surface((w, h), SWSURFACE|SRCALPHA, 32)
        self.pixelmap_picking = picking(w, h, t = self.datatype)
        self.alpha = pygame.Surface((w, h), SWSURFACE|SRCALPHA, 32)
        print("object renewed!")

    def update_perspective(self, depth):
        if depth == 0:
            return
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        ratio = float(self.width) / float(self.height)
        fov = 30.0 / depth
        dist = 1.3 / tan(deg2rad(float(fov) / 2.0))
        gluPerspective(fov, ratio, float(1.0), float(-10.0))
        glViewport (0, 0, self.width, self.height)
        if ratio > 1.0:
            glTranslatef(1.0 - ratio, 0.0, 0.0)
        elif ratio < 1.0:
            glTranslatef(0.0, 0.0, -((ratio + 1.0) * (1.0 / ratio) - 1.0))
        gluLookAt(0.0, 0.0, dist, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    def set_Lights(self, lights):
        if lights:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)

    def set_LightSource(self, source):
        if source == 0:
            if glIsEnabled(GL_LIGHT0):
                glDisable(GL_LIGHT0)
            else:
                glEnable(GL_LIGHT0)
        elif source == 1:
            if glIsEnabled(GL_LIGHT1):
                glDisable(GL_LIGHT1)
            else:
                glEnable(GL_LIGHT1)

    def set_Geometry(self, value):
        self.WireFrame = value

    def set_Wireframe(self, value):
        if value:
            self.polyDraw = GL_LINE_LOOP
        else:
            self.polyDraw = GL_POLYGON

    def setup_Texture(self):
        if self.image is not None:
            if self.image in self.texNamesList:
                self.img = self.texNamesList[self.image]
            else:
                self.img = self.TexFromPNG(self.image)

    def clean_Texture(self):
        if self.image is not None:
            self.image = None
            self.img = None

    def set_Texture(self, texture):
        self.texture = texture
        if texture:
            glEnable(GL_TEXTURE_2D)
            if self.img:
                glCallList(self.img)
                #glBindTexture(GL_TEXTURE_2D, self.img)
        else:
            glDisable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)

    def delete_display_list(self):
        for i in self.Texture:
            print(i, type(i))
            glDeleteLists(i, i)
        self.Texture = []

    def createBackgroundSurface(self, pil_image):
        size = (pil_image.size[0], pil_image.size[1])
        #self.backgroundImage = pygame.image.fromstring(pil_image.tostring("raw", "RGBA"), size, "RGBA")
        self.backgroundImage = pygame.image.fromstring(pil_image.tobytes(), size, "RGBA")

    def createBackground(self, filename = None):
        if psutil_enable:
            v = psutil.virtual_memory().percent
        else:
            v = 0.0
        if not filename or v > mem_Limit or not self.SDL_Mode:
            return self.Empty_texture
        else:
            background = self.TexFromPNG(filename, force = True, mixing = True)
            if background == None:
                return self.Empty_texture
            else:
                return background

    def create_Background(self, imagename):
        self.Background_texture = self.createBackground(imagename)

    def createGround(self, filename = None):
        if psutil_enable:
            v = psutil.virtual_memory().percent
        else:
            v = 0.0
        if not filename or v > mem_Limit or not self.SDL_Mode:
            return self.Empty_texture
        else:
            ground = self.TexFromPNG(filename)
            if ground == None:
                return self.Empty_texture
            else:
                return ground

    def create_Ground(self, imagename):
        if imagename not in self.texNamesList:
            self.Ground_texture = self.createGround(imagename)
        else:
            self.Ground_texture = self.texNamesList[imagename]

    def setup_Objects_Ground(self, objects):
        for i in objects:
            imagename = i.GroundImage()
            print("imagename", imagename)
            if imagename not in self.texNamesList:
                ground = self.createGround(imagename)
            else:
                ground = self.texNamesList[imagename]
            i.set_Ground_Texture(ground)

    def createEmpty(self):
        displayList = glGenLists(1)
        self.Texture.append(displayList)
        glNewList(displayList, GL_COMPILE)
        glBindTexture(GL_TEXTURE_2D, 0)
        glEndList()
        self.texNamesList["empty"] = displayList
        return displayList

    def TexFromPNG(self, filename, force = False, mixing = False):
        print("TexFromPNG", filename)
        if psutil_enable:
            v = psutil.virtual_memory().percent
        else:
            v = 0.0
        if v > mem_Limit:
            return None
        if not force and filename in self.LoadedImages:
            img = self.LoadedImages[filename]
        elif filename and validators.url(filename):
            f = cStringIO.StringIO(urllib.urlopen(filename).read())
            try:
                img = Image.open(f)
            except(Exception) as detail:
                print(detail)
                return None
            self.LoadedImages[filename] = img
        else:
            try:
                img = Image.open(filename)
            except:
                return None
            self.LoadedImages[filename] = img

        img = img.convert("RGBA")

        if mixing and self.BackgroundAlpha:
            color = 255 - self.BackgroundAlpha
            mask = Image.new('L', img.size, color = color)
            img.putalpha(mask)
        
        img = img.transpose(1)
        try:
            img_data = array(list(img.getdata()), dtype = uint8)
        except:
            return None
        displayList = glGenLists(1)
        self.Texture.append(displayList)

        texture = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        #gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, img.size[0], img.size[1], GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.size[0], img.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        glNewList(displayList, GL_COMPILE)
        glBindTexture(GL_TEXTURE_2D, texture)
        glEndList()

        self.texNamesList[filename] = displayList
        #
        return displayList

    def IsExtensionSupported(self, szTargetExtension):
        pszExtensions = glGetString(GL_EXTENSIONS)
        glversion = glGetString(GL_VERSION)
        print("OpenGL ", glversion)

        s = pszExtensions.split(b' ')
        if szTargetExtension in s:
            return True
        else:
            return False

    def resize_SDL(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(float(0), float(self.width), float(self.height), float(0), float(6000.0), float(-10000.0))
        glViewport (0, 0, self.width, self.height)

    def setup_SDL(self, depth):
        self.SDL_Mode = True
        screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF|OPENGL|RESIZABLE)
        pygame.event.set_allowed(None)
        pygame.event.set_allowed(KEYDOWN)
        pygame.event.set_allowed(KEYUP)
        pygame.event.set_allowed(MOUSEBUTTONDOWN)
        #pygame.event.set_allowed(MOUSEBUTTONUP)
        #pygame.event.set_grab(1)
        self.testCursor(arrow)
        glLineStipple(1, 0x3F07)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.0, 0.5, 0.2))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 5.0, -3.0))

        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.0, 0.5, 0.5))
        glLightfv(GL_LIGHT1, GL_SPECULAR, (1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT1, GL_POSITION, (5.0, 3.0, 3.0))

        glEnable(GL_TEXTURE_2D)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        glEnable(GL_RESCALE_NORMAL)

        glCullFace(GL_FRONT)

        glShadeModel(GL_SMOOTH)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

##        glDisable(GL_POINT_SMOOTH)
##        glHint(GL_POINT_SMOOTH_HINT, GL_FASTEST)
##
##        glEnable(GL_LINE_SMOOTH)
##        glEnable(GL_POLYGON_SMOOTH)
##        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
##        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        ratio = float(self.width) / float(self.height)
##        fov = 30.0 / depth
##        dist = 1.3 / tan(deg2rad(float(fov) / 2.0))
        glOrtho(float(0), float(self.width), float(self.height), float(0), float(6000.0), float(-10000.0))
        #gluPerspective(fov, ratio, float(1.0), float(-10.0))
        glViewport (0, 0, self.width, self.height)
##        if ratio > 1.0:
##            glTranslatef(1.0 - ratio, 0.0, 0.0)
##        elif ratio < 1.0:
##            glTranslatef(0.0, 0.0, -((ratio + 1.0) * (1.0 / ratio) - 1.0))
##
        #gluLookAt(0.0, 0.0, dist, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        self.setup_Texture()
        #self.Empty_texture = self.TexFromPNG(EMPTY)
        self.Empty_texture = self.createEmpty()
        self.Ground_texture = self.createGround(self.GroundImage)
        self.create_Background(self.BackgroundImage)
        self.surface = screen
        if self.VBO:
            self.VBO = self.enable_VBO()

    def enable_VBO(self):
        if self.IsExtensionSupported("GL_ARB_vertex_buffer_object"):
            glEnable(GL_VERTEX_ARRAY)
            glEnable(GL_NORMAL_ARRAY)
            glEnable(GL_TEXTURE_COORD_ARRAY)
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            return True
        else:
            return False

    def disable_VBO(self):
        if self.IsExtensionSupported("GL_ARB_vertex_buffer_object"):
            glDisable(GL_VERTEX_ARRAY)
            glDisable(GL_NORMAL_ARRAY)
            glDisable(GL_TEXTURE_COORD_ARRAY)
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    def set_VBO(self, value):
        self.VBO = value
        if value and self.SDL_Mode:
            self.VBO = self.enable_VBO()
        return self.VBO

    def set_OBJ_Mode(self, mode, OBJ):
        self.OBJ = OBJ
        self.OBJ_Mode = mode
        if self.SDL_Mode:
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

    def set_Clear_Color(self, color):
        self.preMultCol = (color[0], color[1], color[2], 0)
        self.BackgroundAlpha = color[3]
        if self.SDL_Mode:
            glClearColor(float(color[0] / 255.0),
                         float(color[1] / 255.0),
                         float(color[2] / 255.0),
                         float(color[3] / 255.0))

    def release_SDL(self):
        self.SDL_Mode = False
        self.texNamesList = {}
        self.delete_display_list()
        self.disable_VBO()
        pygame.display.quit()

        self.surface = pygame.Surface((self.width, self.height), SWSURFACE|SRCALPHA, 32)

    def draw_OBJ(self, center, radius, angle, vector, angle1, vector1, depth):
        OBJ = self.OBJ
        if OBJ == None:
            OBJ = self.cube
        if self.SDL_Mode:
            if self.texture == self.img:
                pass
            elif self.texture and self.img:
                glCallList(self.img)
                self.texture = self.img
            else:
                glActiveTexture(GL_TEXTURE0)
            OBJ.load_id(center, radius, angle, vector, self.baked_c, self.vector_c, angle1, vector1)
            glColor4fv(gl_objectcolor)
            OBJ.render(self.polyDraw)
        else:
            OBJ.load_id_transform(angle, vector)

    def draw_GL_Repro(self, center, radius, OBJ, texture, angle = 0, vector = (0, 1, 0), spin = 0, frame = None, oscillate = 0, color = (0.0, 0.0, 0.0), Vector = None):
        if texture is None:
            texture = self.Empty_texture
        if self.texture == texture:
            pass
        elif self.texture and texture:
            glCallList(texture)
            self.texture = texture
        else:
            glActiveTexture(GL_TEXTURE0)

        OBJ.position_and_scale(center, radius, angle, vector, self.baked_c, self.vector_c, self.random_rot, spin, Vector)
        OBJ.render(self.polyDraw, frame, oscillate, color, self.WireFrame)

    def draw_GL_Cube(self, center, radius, vectors, texture):
        if texture is None:
            texture = self.Empty_texture
        if self.texture == texture:
            pass
        elif self.texture and texture:
            glCallList(texture)
            self.texture = texture
        else:
            glActiveTexture(GL_TEXTURE0)
        self.cube.set_size_and_position(center, radius, vectors)
        self.cube.render()

    def draw_GL_Cube_In_View(self, vectors, texture):
        if texture is None:
            texture = self.Empty_texture
        if self.texture == texture:
            pass
        elif self.texture and texture:
            glCallList(texture)
            self.texture = texture
        else:
            glActiveTexture(GL_TEXTURE0)
        self.cube.set_positions(vectors)
        self.cube.render()

    def draw_GL_Circle(self, center, radius, refine = 30, texture = None, GL_func = GL_POLYGON):
        if texture is None:
            texture = self.Empty_texture
        if self.texture == texture:
            pass
        elif self.texture and texture:
            glCallList(texture)
            self.texture = texture
        else:
            glActiveTexture(GL_TEXTURE0)
        step = pi2 / float(refine)
        glBegin(GL_func)
        c = pi / 4.0
        glNormal3fv((0.0, 1.0, 0.0))
        for i in range(refine):
            glTexCoord2fv(self.uvs[i])
            glVertex3f(cos(c) * radius + center[0],
                       sin(c) * radius + center[1],
                       center[2])
            c += step
        glEnd()

    def draw_background(self):
        if self.SDL_Mode and self.Background_texture:
            glDisable(GL_DEPTH_TEST)
            glCallList(self.Background_texture)
            glBegin(GL_QUADS)
            glNormal3fv((0.0, 1.0, 0.0))
            glColor4fv(gl_backgroundcolor)
            glTexCoord2f(0.0, 1.0)
            glVertex2f(0.0, 0.0)
            glTexCoord2f(1.0, 1.0)
            glVertex2f(float(self.width), 0.0)
            glTexCoord2f(1.0, 0.0)
            glVertex2f(float(self.width), float(self.height))
            glTexCoord2f(0.0, 0.0)
            glVertex2f(0.0, float(self.height))
            glEnd()
            glEnable(GL_DEPTH_TEST)
            glCallList(self.Empty_texture)
            self.texture = self.Empty_texture

    def __getitem__(self, v):
        if self.SDL_Mode:
            step = 20
            w = int(self.width) / int(step)
            h = int(self.height) / int(step)
            w1 = int(self.width) % int(step)
            h1 = int(self.height) % int(step)
            W = w * step + w1
            H = h * step + h1
            image = Image.new("RGBA", (W, H))
            W1 = [step] * w + [w1]
            H1 = [step] * h + [h1]
            X = 0
            for x in W1:
                Y = 0
                for y in H1:
                    a = glReadPixelsf(X, Y, x, y, GL_RGBA, GL_FLOAT)
                    a = multiply(a, 255.0)
                    img = Image.frombuffer("RGBA", (int(x), int(y)), a.astype('uint8'), "raw", "RGBA", 0, 1)
                    image.paste(img, (X, Y))
                    Y += y
                X += x
            image = image.transpose(1)
        else:
            #img1 = pygame.surfarray.pixels2d(self.surface)
            if (pyversion >= 3):
                img1 = pygame.surfarray.array2d(self.surface)
                #img1 = asarray(img1, order = 'C')
                image = Image.frombuffer("RGBA", (int(self.height), int(self.width)), img1, "raw", "BGRA", 0, 1)
                image = image.transpose(Image.TRANSPOSE)
            else:
                img1 = pygame.surfarray.pixels2d(self.surface)
                image = Image.frombuffer("RGBA", (int(self.width), int(self.height)), img1, "raw", "BGRA", 0, 1)
        return image
