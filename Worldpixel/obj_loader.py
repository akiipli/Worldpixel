#A. Kiipli
#---------------
from PIL import Image
from OpenGL.GL import *
from OpenGL.GLU import *
from numpy import *
import random
import os, re

#from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.arrays import ArrayDatatype as ADT

try:
    import psutil
    psutil_enable = True
except:
    psutil_enable = False

mem_Limit = 80.0

import ctypes

folders             = "Folders"
obj_files           = "OBJ"

def cross(A, B, C):
    v1 = (A[0] - B[0], A[1] - B[1], A[2] - B[2])
    v2 = (C[0] - B[0], C[1] - B[1], C[2] - B[2])
    n = (v1[1] * v2[2] - v1[2] * v2[1],
         v1[2] * v2[0] - v1[0] * v2[2],
         v1[0] * v2[1] - v1[1] * v2[0])
    d = sqrt(n[0]**2 + n[1]**2 + n[2]**2)

    if d != 0:
        n = (n[0] / d, n[1] / d, n[2] / d)
    return n

class polygon:
    def __init__(self):
        self.vertex = []
        self.uvtext = []
        self.normal = []
        self.verts = self.getverts
        self.norms = self.getnormals
        self.texts = self.getuvcoords

    def create_normal(self):
        polypoints = self.verts()
        planenormal = cross(polypoints[0], polypoints[1], polypoints[2])
        for n in self.normal:
            n.__init__(planenormal)

    def getverts(self):
        return [(x.coords) for x in self.vertex]

    def getnormals(self):
        return [(x.coords) for x in self.normal]

    def getuvcoords(self):
        return [(x.coords) for x in self.uvtext]

class vertex:
    def __init__(self, coords, index = -1):
        self.coords = coords
        self.x = coords[0]
        self.y = coords[1]
        self.z = coords[2]
        self.index = index

    def __getitem__(self, i):
        return self.coords[i]

class texture:
    def __init__(self, coords):
        self.coords = coords
        self.x = coords[0]
        self.y = coords[1]

    def __getitem__(self, i):
        return self.coords[i]

class normal:
    def __init__(self, coords):
        self.coords = coords
        self.x = coords[0]
        self.y = coords[1]
        self.z = coords[2]

    def __getitem__(self, i):
        return self.coords[i]

def qualify(faces):
    F = []
    for f in faces:
        verts = f.verts()
        for v in verts:
            if (v[0] >= -1 and v[0] <= 1 and
                v[1] >= -1 and v[1] <= 1 and
                v[2] >= -1 and v[2] <= 1):
                F.append(f)
                break
    return F
                

def load(filename):
    verts = []
    norms = []
    uvtex = []
    faces = []
    vcount = 0
    if psutil_enable:
        v = psutil.virtual_memory().percent
    else:
        v = 0.0
    if v > mem_Limit:
        filename = os.path.join(folders, obj_files, "Cube.obj")
    for line in open(filename, "r"):
        vals = line.split()
        if len(vals) < 1:
            continue
        if vals[0] == "v":
            verts.append(vertex(list(map(float, vals[1:4])), vcount))
            vcount += 1
        if vals[0] == "vt":
            uvtex.append(texture(list(map(float, vals[1:3]))))
        if vals[0] == "vn":
            norms.append(normal(list(map(float, vals[1:4]))))
        if vals[0] == "f":
            faces.append(polygon())
            for f in vals[1:]:
                w = f.split("/")
                if verts:
                    faces[-1].vertex.append(verts[int(w[0])-1])
                if uvtex:
                    try:
                        faces[-1].uvtext.append(uvtex[int(w[1])-1])
                    except:
                        faces[-1].uvtext.append(texture([0, 0]))
                else:
                    faces[-1].uvtext.append(texture([0, 0]))
                if norms:
                    try:
                        faces[-1].normal.append(norms[int(w[2])-1])
                    except:
                        faces[-1].normal.append(normal([0, 1, 0]))
                else:
                    faces[-1].normal.append(normal([0, 1, 0]))
    if not norms:
        for f in faces:
            f.create_normal()
    return faces

def load_verts(filename):
    verts = []
    faces = []
    norms = []
    vcount = 0
    if psutil_enable:
        v = psutil.virtual_memory().percent
    else:
        v = 0.0
    if v > mem_Limit:
        filename = os.path.join(folders, obj_files, "Cube.obj")
    for line in open(filename, "r"):
        vals = line.split()
        if len(vals) < 1:
            continue
        if vals[0] == "v":
            verts.append(vertex(list(map(float, vals[1:4])), vcount))
            vcount += 1
        if vals[0] == "vn":
            norms.append(normal(list(map(float, vals[1:4]))))
        if vals[0] == "f":
            faces.append(polygon())
            for f in vals[1:]:
                w = f.split("/")
                if verts:
                    faces[-1].vertex.append(verts[int(w[0])-1])
                if norms:
                    try:
                        faces[-1].normal.append(norms[int(w[2])-1])
                    except:
                        faces[-1].normal.append(normal([0, 1, 0]))
                else:
                    faces[-1].normal.append(normal([0, 1, 0]))
    if not norms:
        norms = [object] * len(verts)
        for f in faces:
            f.create_normal()
            for v, n in zip(f.vertex, f.normal):
                norms[v.index] = n
    return faces, verts, norms

def load_Faces(filename, progress = None, advance = False):
    print("load_Faces")
    (path, name) = os.path.split(filename)
    extension = name[-3:]
    R = re.match(r'(\D*)(\d*)', name)

    Faces = []
    Verts = []
    Norms = []

    if os.path.isdir(path):
        dirs = []
        try:
            dirs = os.listdir(path)
            dirs.sort()
        except(Exception) as detail:
            print('EXC0')
            return Faces, Verts, Norms

        for i in dirs:
            if i[-3:] == extension:
                if R.group(2):
                    if R.group(1) == i[:len(R.group(1))]:
                        if psutil_enable:
                            v = psutil.virtual_memory().percent
                        else:
                            v = 0.0
                        if v > mem_Limit:
                            return Faces, Verts, Norms
                        if progress:
                            try:
                                if advance:
                                    progress.advance("repros\n")
                                progress.set_msg1(str(i))
                            except(Exception) as detail:
                                print(detail)
                                return Faces, Verts, Norms
                        faces, verts, norms = load_verts(os.path.join(path, i))
                        Faces.append(faces)
                        Verts.append(verts)
                        Norms.append(norms)
        return Faces, Verts, Norms
    else:
        return Faces, Verts, Norms
    

class obj_transform():
    def __init__(self, faces, Faces = [], Verts = [], Norms = []):
        self.faces = faces
        self.Faces = [faces,]
        self.validate_Faces(len(faces), Faces)
        self.Tfaces = [object] * len(self.faces)
        for x, f in enumerate(self.faces):
            self.Tfaces[x] = polygon()
            self.Tfaces[x].vertex = [object] * len(f.verts())
        self.modelview = False
        self.angle = 0
        self.vector = (0, 1, 0)
        self.sx = 1.0
        self.sy = 1.0
        self.sz = 1.0
        self.px = 0
        self.py = 0
        self.objdisplayList = 0
        self.vertex_arrays = False
        self.VBO = False
        self.Frames = len(self.Faces)
        self.frame = 0
        self.vert_array3 = [list()] * self.Frames
        self.vert_array4 = [list()] * self.Frames
        self.vert_array_Fan = [list()] * self.Frames
        self.verts3 = [list()] * self.Frames
        self.verts4 = [list()] * self.Frames
        self.verts_Fan = [list()] * self.Frames
        self.norm_array3 = [list()] * self.Frames
        self.norm_array4 = [list()] * self.Frames
        self.norm_array_Fan = [list()] * self.Frames
        self.norms3 = [list()] * self.Frames
        self.norms4 = [list()] * self.Frames
        self.norms_Fan = [list()] * self.Frames
        
        self.vert_array_Lines = [list()] * self.Frames
        self.norm_array_Lines = [list()] * self.Frames
        self.text_array_Lines = list()
        self.lines = [list()] * self.Frames
        self.line_norms = [list()] * self.Frames
        self.Edges, self.Lines = self.build_Edges(faces)

        self.Verts = Verts
        self.Norms = Norms
        try:
            print("Faces", len(self.Faces[0]))
            print("Verts", len(self.Verts[0]))
            print("Norms", len(self.Norms[0]))
        except:
            pass

        self.wireDraw = False
        self.objectDraw = True

    def cleanup(self):
        for f in self.Faces:
            for i in f:
                del i
        for i in self.faces:
            del i
        if self.VBO:
            glDeleteBuffers(12, self.buffers)

    def build_Edges(self, Faces):
        edges = {}
        Edges = []
        Lines = []
        for i in Faces:
            index = []
            verts = {}
            norms = {}
            texts = {}
            for v, n, t in zip(i.vertex, i.normal, i.uvtext):
                index.append(v.index)
                verts[v.index] = v
                norms[v.index] = n
                texts[v.index] = t
            INDEX = index[1:] + [index[0]]
            for x, y in zip(index, INDEX):
                edge = (x, y)
                if (y, x) in edges:
                    pass
                else:
                    edges[edge] = 1
                    Edge = (verts[x], verts[y], norms[x], norms[y], texts[x], texts[y])
                    Edges.append(Edge)
                    Lines.append(edge)
        print("Edges number", len(Edges))
        return Edges, Lines

    def validate_Faces(self, length, Faces):
        print("validate_Faces", length)
        for i in Faces:
            print(len(i))
            if len(i) == length:
                self.Faces.append(i)

    def set_up_VBO(self, usage = GL_STATIC_DRAW):
        
        self.VBO = True
        
        print("set_up_VBO", self.Frames)
        
        for x in range(self.Frames):
            try:
                self.verts3[x] = array(self.vert_array3[x], dtype = float32)
                self.verts4[x] = array(self.vert_array4[x], dtype = float32)
                self.verts_Fan[x] = array(self.vert_array_Fan[x], dtype = float32)
                self.norms3[x] = array(self.norm_array3[x], dtype = float32)
                self.norms4[x] = array(self.norm_array4[x], dtype = float32)
                self.norms_Fan[x] = array(self.norm_array_Fan[x], dtype = float32)
                self.lines[x] = array(self.vert_array_Lines[x], dtype = float32)
                self.line_norms[x] = array(self.norm_array_Lines[x], dtype = float32)
            except:
                self.Frames = x

        self.buffers = glGenBuffers(12)

        self.buffer_line_array2 = self.buffers[0]
        self.buffer_norm_array2 = self.buffers[1]
        self.buffer_text_array2 = self.buffers[2]

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_line_array2)
        self.buffer_line_array2_size = ADT.arrayByteCount(self.lines[0])
        glBufferData(GL_ARRAY_BUFFER, self.buffer_line_array2_size, self.lines[0], usage)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_norm_array2)
        self.buffer_line_norms_size = ADT.arrayByteCount(self.line_norms[0])
        glBufferData(GL_ARRAY_BUFFER, self.buffer_line_norms_size, self.line_norms[0], usage)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_text_array2)
        self.line_texts = array(self.text_array_Lines, dtype = float32)
        glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(self.line_texts), self.line_texts, usage)

        self.buffer_vert_array3 = self.buffers[3]
        self.buffer_norm_array3 = self.buffers[4]
        self.buffer_text_array3 = self.buffers[5]

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vert_array3)
        self.buffer_vert_array3_size = ADT.arrayByteCount(self.verts3[0])
        glBufferData(GL_ARRAY_BUFFER, self.buffer_vert_array3_size, self.verts3[0], GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_norm_array3)
        self.buffer_norm_array3_size = ADT.arrayByteCount(self.norms3[0])
        glBufferData(GL_ARRAY_BUFFER, self.buffer_norm_array3_size, self.norms3[0], GL_DYNAMIC_DRAW)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_text_array3)
        self.texts3 = array(self.text_array3, dtype = float32)
        glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(self.texts3), self.texts3, usage)

        self.buffer_vert_array4 = self.buffers[6]
        self.buffer_norm_array4 = self.buffers[7]
        self.buffer_text_array4 = self.buffers[8]

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vert_array4)
        self.buffer_vert_array4_size = ADT.arrayByteCount(self.verts4[0])
        glBufferData(GL_ARRAY_BUFFER, self.buffer_vert_array4_size, self.verts4[0], GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_norm_array4)
        self.buffer_norm_array4_size = ADT.arrayByteCount(self.norms4[0])
        glBufferData(GL_ARRAY_BUFFER, self.buffer_norm_array4_size, self.norms4[0], GL_DYNAMIC_DRAW)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_text_array4)
        self.texts4 = array(self.text_array4, dtype = float32)
        glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(self.texts4), self.texts4, usage)

        self.buffer_vert_array_Fan = self.buffers[9]
        self.buffer_norm_array_Fan = self.buffers[10]
        self.buffer_text_array_Fan = self.buffers[11]

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vert_array_Fan)
        self.buffer_vert_array_Fan_size = ADT.arrayByteCount(self.verts_Fan[0])
        glBufferData(GL_ARRAY_BUFFER, self.buffer_vert_array_Fan_size, self.verts_Fan[0], GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_norm_array_Fan)
        self.buffer_norm_array_Fan_size = ADT.arrayByteCount(self.norms_Fan[0])
        glBufferData(GL_ARRAY_BUFFER, self.buffer_norm_array_Fan_size, self.norms_Fan[0], GL_DYNAMIC_DRAW)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_text_array_Fan)
        self.texts_Fan = array(self.text_array_Fan, dtype = float32)
        glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(self.texts_Fan), self.texts_Fan, usage)

    def set_up_vertex_array(self):
        print("set_up_vertex_array")
        if not self.vertex_arrays:
            self.vertex_arrays = True
            vert_array3 = []
            vert_array4 = []
            vert_array_Fan = []
            vert_array_Lines = []
            norm_array_Lines = []
            norm_array3 = []
            norm_array4 = []
            norm_array_Fan = []
            self.text_array3 = []
            self.text_array4 = []
            self.text_array_Fan = []
            self.arraySize3 = 0
            self.arraySize4 = 0
            self.arraySize_Fan = []
            self.arraySize_Lines = 0
            for f in self.faces:
                verts = f.verts()
                normals = f.norms()
                uv = f.texts()
                if len(verts) == 3:
                    for i in range(3):
                        vert_array3.append(verts[i])
                        norm_array3.append(normals[i])
                        self.text_array3.append(uv[i])
                    self.arraySize3 += 3
                elif len(verts) == 4:
                    for i in range(4):
                        vert_array4.append(verts[i])
                        norm_array4.append(normals[i])
                        self.text_array4.append(uv[i])
                    self.arraySize4 += 4
                elif len(verts) > 4:
                    n = len(verts)
                    for i in range(n):
                        vert_array_Fan.append(verts[i])
                        norm_array_Fan.append(normals[i])
                        self.text_array_Fan.append(uv[i])
                    self.arraySize_Fan.append(n)
                    
            for e in self.Edges:
                vert_array_Lines += [e[0].coords, e[1].coords]
                norm_array_Lines += [e[2].coords, e[3].coords]
                self.text_array_Lines += [e[4].coords, e[5].coords]
                self.arraySize_Lines += 2
            self.vert_array_Lines[0] = vert_array_Lines
            self.norm_array_Lines[0] = norm_array_Lines
            
            self.vert_array3[0] = vert_array3
            self.vert_array4[0] = vert_array4
            self.vert_array_Fan[0] = vert_array_Fan
            self.norm_array3[0] = norm_array3
            self.norm_array4[0] = norm_array4
            self.norm_array_Fan[0] = norm_array_Fan
            if self.Frames > 1:
                for x in range(1, self.Frames):
                    vert_array3 = []
                    vert_array4 = []
                    vert_array_Fan = []
                    vert_array_Lines = []
                    norm_array_Lines = []
                    norm_array3 = []
                    norm_array4 = []
                    norm_array_Fan = []
                    for f in self.Faces[x]:
                        verts = f.verts()
                        normals = f.norms()
                        if len(verts) == 3:
                            for i in range(3):
                                vert_array3.append(verts[i])
                                norm_array3.append(normals[i])
                        elif len(verts) == 4:
                            for i in range(4):
                                vert_array4.append(verts[i])
                                norm_array4.append(normals[i])
                        elif len(verts) > 4:
                            n = len(verts)
                            for i in range(n):
                                vert_array_Fan.append(verts[i])
                                norm_array_Fan.append(normals[i])
                    for l in self.Lines:
                        try:
                            v1 = self.Verts[x - 1][l[0]]
                            v2 = self.Verts[x - 1][l[1]]
                        except(Exception) as detail:
                            pass
                        vert_array_Lines += [v1.coords, v2.coords]
                        try:
                            n1 = self.Norms[x - 1][l[0]]
                            n2 = self.Norms[x - 1][l[1]]
                        except(Exception) as detail:
                            pass
                        norm_array_Lines += [n1.coords, n2.coords]
                    self.vert_array_Lines[x] = vert_array_Lines
                    self.norm_array_Lines[x] = norm_array_Lines                    
                    self.vert_array3[x] = vert_array3
                    self.vert_array4[x] = vert_array4
                    self.vert_array_Fan[x] = vert_array_Fan
                    self.norm_array3[x] = norm_array3
                    self.norm_array4[x] = norm_array4
                    self.norm_array_Fan[x] = norm_array_Fan
        self.set_up_VBO()

    def delete_VBO(self):
        self.VBO = False

    def delete_display_list(self):
        if self.objdisplayList:
            glDeleteLists(self.objdisplayList, self.objdisplayList)
        self.objdisplayList = 0

    def set_up_display_list(self, GL_Function = GL_POLYGON):
        print("set_up_display_list")
        #self.delete_display_list()
        self.objdisplayList = glGenLists(1)
        glNewList(self.objdisplayList, GL_COMPILE)

        #glColor4fv((1.0, 0.5, 0.0, 0.5))
        for f in self.faces:
            normals = f.norms()
            uv = f.texts()
            glBegin(GL_Function)
            for x, v in enumerate(f.verts()):
                glNormal3fv(normals[x])
                glTexCoord2f(uv[x][0], uv[x][1])
                glVertex3fv(v)
            glEnd()
        glEndList()

    def rotate_around_vector(self, x, y, z, vector, angle):
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

        return (x_5, y_5, z_4)

    def get_transformed(self, angle = None, X = 0, Y = 0, Z = 0):
        if angle is None:
            angle = self.angle
        for x, f in enumerate(self.faces):
            for y, v in enumerate(f.verts()):
                center = self.rotate_around_vector(v[0], v[1], v[2], self.vector, angle)
                self.Tfaces[x].vertex[y] = vertex((center[0] + X, center[1] + Y, center[2] + Z))

    def load_id_transform(self, angle, vector):
        self.modelview = True
        self.angle = angle
        self.vector = vector

    def load_id(self, center, radius, angle, vector, baked_angle, vector_c, angle1, vector1):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(float(center[0] + self.px), float(center[1] + self.py), float(center[2]))
        glRotatef(float(rad2deg(baked_angle)), float(vector_c[0]), float(-vector_c[1]), float(vector_c[2]))
        glRotatef(float(rad2deg(angle1)), float(vector1[0]), float(-vector1[1]), float(vector1[2]))
        glRotatef(float(rad2deg(angle)), float(vector[0]), float(-vector[1]), float(vector[2]))
        glScalef(float(radius * self.sx), float(-radius * self.sy), float(-radius * self.sz))
        self.modelview = True
        self.angle = angle
        self.vector = vector

    def position_and_scale(self, center, radius, angle, vector, baked_angle, vector_c, random_rot, spin, Vector):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(float(center[0] + self.px), float(center[1] + self.py), float(center[2]))
        glRotatef(float(rad2deg(baked_angle)), float(vector_c[0]), float(-vector_c[1]), float(vector_c[2]))
        angle1 = rad2deg(angle + spin)
        angle1 = random.randint(int(angle1 - random_rot), int(angle1 + random_rot))
        glRotatef(float(angle1), float(vector[0]), float(-vector[1]), float(vector[2]))
        #
        if Vector is not None:
##            y_x_angle = math.atan2(Vector[1], Vector[0])
##            x = math.sqrt(Vector[1]**2 + Vector[0]**2)
##            glRotatef(float(rad2deg(-y_x_angle)), float(0), float(0), float(1))
##            x_z_angle = math.atan2(x, Vector[2])
##            glRotatef(float(rad2deg(-x_z_angle)), float(0), float(1), float(0))

            #Vector = (0, sin(angle), cos(angle))

            x_z_angle = math.atan2(Vector[0], Vector[2])
            z = math.sqrt(Vector[0]**2 + Vector[2]**2)
            glRotatef(float(rad2deg(-x_z_angle)), float(0), float(1), float(0))
            y_z_angle = math.atan2(Vector[1], z)
            glRotatef(float(rad2deg(-y_z_angle)), float(1), float(0), float(0))
        #
        glScalef(float(radius * self.sx), float(-radius * self.sy), float(-radius * self.sz))

    def return_Wire_Render(self):
        return (int(self.wireDraw), int(self.objectDraw))

    def tune_Wire_Render(self, t):
        (self.wireDraw, self.objectDraw) = t

    def return_Pos_And_Scale(self):
        return (self.px, -self.py, self.sx, self.sy, self.sz)

    def tune_Position_And_Scale(self, d):
        self.px = d[0]
        self.py = -d[1]
        self.sx = d[2]
        self.sy = d[3]
        self.sz = d[4]

    def render(self, GL_Function, frame = None, oscillate = 0, color = (0.5, 0.5, 1.0), wireframe = False):
        if GL_Function == GL_LINE_LOOP:
            GL_TRIANGLES_Function    = GL_LINES
            GL_QUADS_Function        = GL_LINES
            GL_TRIANGLE_FAN_Function = GL_LINES
        else:
            GL_TRIANGLES_Function    = GL_TRIANGLES
            GL_QUADS_Function        = GL_QUADS
            GL_TRIANGLE_FAN_Function = GL_TRIANGLE_FAN
            
        if self.frame >= self.Frames:
            self.frame = 0
        if frame is None:
            frame = self.frame
        d = frame % 1

        if oscillate < 1:
            d = -d
        f = int(frame + d)
        F = int(frame - d)
        if f >= self.Frames:
            if oscillate:
                f = self.Frames -1
            else:
                f = 0
        elif f < 0:
            f = 0
        if F >= self.Frames:
            if oscillate:
                F = self.Frames -1
            else:
                F = 0
        elif F < 0:
            F = 0
        if self.objdisplayList:
            glCallList(self.objdisplayList)
        elif self.VBO:
            if self.objectDraw and not wireframe:

                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vert_array3)
                if self.Frames > 1:
                    if d:
                        verts3 = divide(add(self.verts3[F], self.verts3[f]), 2.0)
                    else:
                        verts3 = self.verts3[f]
                    glBufferSubData(GL_ARRAY_BUFFER, 0, self.buffer_vert_array3_size, verts3)
                glVertexPointer(3, GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_norm_array3)
                if self.Frames > 1:
                    if d:
                        norms3 = divide(add(self.norms3[F], self.norms3[f]), 2.0)
                    else:
                        norms3 = self.norms3[f]
                    glBufferSubData(GL_ARRAY_BUFFER, 0, self.buffer_norm_array3_size, norms3)
                glNormalPointer(GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_text_array3)
                glTexCoordPointer(2, GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glDrawArrays(GL_TRIANGLES, 0, self.arraySize3)
    ##            if GL_Function == GL_LINE_LOOP and self.Frames > 1:
    ##                glColor3fv(Color)
    ##                glDrawArrays(GL_TRIANGLES_Function, 0, self.arraySize3)
    ##                glColor3fv(color)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vert_array4)
                if self.Frames > 1:
                    if d:
                        verts4 = divide(add(self.verts4[F], self.verts4[f]), 2.0)
                    else:
                        verts4 = self.verts4[f]
                    glBufferSubData(GL_ARRAY_BUFFER, 0, self.buffer_vert_array4_size, verts4)
                glVertexPointer(3, GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_norm_array4)
                if self.Frames > 1:
                    if d:
                        norms4 = divide(add(self.norms4[F], self.norms4[f]), 2.0)
                    else:
                        norms4 = self.norms4[f]
                    glBufferSubData(GL_ARRAY_BUFFER, 0, self.buffer_norm_array4_size, norms4)
                glNormalPointer(GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_text_array4)
                glTexCoordPointer(2, GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glDrawArrays(GL_QUADS, 0, self.arraySize4)
    ##            if GL_Function == GL_LINE_LOOP and self.Frames > 1:
    ##                glColor3fv(Color)
    ##                glDrawArrays(GL_QUADS_Function, 0, self.arraySize4)
    ##                glColor3fv(color)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vert_array_Fan)
                if self.Frames > 1:
                    if d:
                        verts_Fan = divide(add(self.verts_Fan[F], self.verts_Fan[f]), 2.0)
                    else:
                        verts_Fan = self.verts_Fan[f]
                    glBufferSubData(GL_ARRAY_BUFFER, 0, self.buffer_vert_array_Fan_size, verts_Fan)
                glVertexPointer(3, GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_norm_array_Fan)
                if self.Frames > 1:
                    if d:
                        norms_Fan = divide(add(self.norms_Fan[F], self.norms_Fan[f]), 2.0)
                    else:
                        norms_Fan = self.norms_Fan[f]
                    glBufferSubData(GL_ARRAY_BUFFER, 0, self.buffer_norm_array_Fan_size, norms_Fan)
                glNormalPointer(GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_text_array_Fan)
                glTexCoordPointer(2, GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                x = 0
                for i in self.arraySize_Fan:
                    glDrawElementsui(GL_TRIANGLE_FAN, arange(x, x + i).astype(uint))
                    x += i
    ##            if GL_Function == GL_LINE_LOOP and self.Frames > 1:
    ##                glColor3fv(Color)
    ##                x = 0
    ##                for i in self.arraySize_Fan:
    ##                    glDrawElementsui(GL_TRIANGLE_FAN_Function, arange(x, x + i).astype(uint))
    ##                    x += i

            if GL_Function == GL_LINE_LOOP or self.wireDraw:
                Color = (divmod(color[0] - 0.7, 1.0)[1],
                         divmod(color[1] - 0.7, 1.0)[1],
                         divmod(color[2] - 0.7, 1.0)[1])
                glColor3fv(Color)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_line_array2)
                if self.Frames > 1:
                    if d:
                        verts2 = divide(add(self.lines[F], self.lines[f]), 2.0)
                    else:
                        verts2 = self.lines[f]
                    glBufferSubData(GL_ARRAY_BUFFER, 0, self.buffer_line_array2_size, verts2)
                glVertexPointer(3, GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_norm_array2)
                if self.Frames > 1:
                    if d:
                        norms2 = divide(add(self.line_norms[F], self.line_norms[f]), 2.0)
                    else:
                        norms2 = self.line_norms[f]
                    glBufferSubData(GL_ARRAY_BUFFER, 0, self.buffer_line_norms_size, norms2)
                glNormalPointer(GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, self.buffer_text_array2)
                glTexCoordPointer(2, GL_FLOAT, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glDrawArrays(GL_LINES, 0, self.arraySize_Lines)

            self.frame += 1
        
        elif self.vertex_arrays:
            if GL_Function == GL_LINE_LOOP:
                glVertexPointer(3, GL_FLOAT, 0, self.vert_array_Lines[f])
                glNormalPointer(GL_FLOAT, 0, self.norm_array_Lines[f])
                glTexCoordPointer(2, GL_FLOAT, 0, self.text_array_Lines)
                glDrawArrays(GL_LINES, 0, self.arraySize_Lines)
            else:
                f = int(frame)
                glVertexPointer(3, GL_FLOAT, 0, self.vert_array3[f])
                glNormalPointer(GL_FLOAT, 0, self.norm_array3[f])
                glTexCoordPointer(2, GL_FLOAT, 0, self.text_array3)
                glDrawArrays(GL_TRIANGLES_Function, 0, self.arraySize3)

                glVertexPointer(3, GL_FLOAT, 0, self.vert_array4[f])
                glNormalPointer(GL_FLOAT, 0, self.norm_array4[f])
                glTexCoordPointer(2, GL_FLOAT, 0, self.text_array4)
                glDrawArrays(GL_QUADS_Function, 0, self.arraySize4)

                glVertexPointer(3, GL_FLOAT, 0, self.vert_array_Fan[f])
                glNormalPointer(GL_FLOAT, 0, self.norm_array_Fan[f])
                glTexCoordPointer(2, GL_FLOAT, 0, self.text_array_Fan)
                x = 0
                for i in self.arraySize_Fan:
                    glDrawElementsui(GL_TRIANGLE_FAN_Function, arange(x, x + i).astype(uint))
                    x += i
                self.frame += 1
        else:
            if GL_Function == GL_LINE_LOOP:
                for e in self.Edges:
                    glBegin(GL_LINES)
                    glVertex3fv(e[0].coords)
                    glVertex3fv(e[1].coords)
                    glEnd()
            else:
                for f in self.faces:
                    glNormal3fv(f.norms()[0])
                    uv = f.texts()
                    glBegin(GL_Function)
                    for x, v in enumerate(f.verts()):
                        glTexCoord2f(uv[x][0], uv[x][1])
                        glVertex3fv(v)
                    glEnd()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
