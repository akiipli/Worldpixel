# -----------------------
# scan_object module for
# Worldpixel program
# -----------------------
#
# Author Allan Kiipli (c)
#
# scan obj file loaded with
# obj_loader. Call scan()
# with dimension,
# voxel size to be set inside object
# and faces array
#

from numpy import *
import math, os
from PIL import Image

pi = math.pi

pi2 = pi * 2

tolerance = 1000

def vector(A, B):
    C = list(range(3))
    C[0] = A[0] - B[0]
    C[1] = A[1] - B[1]
    C[2] = A[2] - B[2]
    l = length(C)
    if l != 0:
        C = (C[0] / l, C[1] / l, C[2] / l)
    return C

def vector2d(A, B):
    C = list(range(2))
    C[0] = A[0] - B[0]
    C[1] = A[1] - B[1]
    l = length2d(C)
    if l != 0:
        C = (C[0] / l, C[1] / l)
    return C

def dot_product2d(A, B):
    return (A[0] * B[0] + A[1] * B[1])

def dot_product(A, B):
    return (A[0] * B[0] + A[1] * B[1] + A[2] * B[2])

def length2d(A):
    return math.sqrt(math.pow(A[0], 2) + math.pow(A[1], 2))

def length(A):
    return math.sqrt(math.pow(A[0], 2) + math.pow(A[1], 2) + math.pow(A[2], 2))

def cross(A, B, C):
    v1 = (A[0] - B[0], A[1] - B[1], A[2] - B[2])
    v2 = (C[0] - B[0], C[1] - B[1], C[2] - B[2])
    n = (v1[1] * v2[2] - v1[2] * v2[1],
         v1[2] * v2[0] - v1[0] * v2[2],
         v1[0] * v2[1] - v1[1] * v2[0])
    d = length(n)
    if d != 0:
        n = (n[0] / d, n[1] / d, n[2] / d)
    return n

def nearest(point, plane):
    h_norm = (plane.x - point.x, plane.y - point.y, plane.z - point.z)
    h = length(h_norm)
    if h != 0:
        h_norm = (h_norm[0] / h, h_norm[1] / h, h_norm[2] / h)
        dot = (h_norm[0] * plane.nx + h_norm[1] * plane.ny + h_norm[2] * plane.nz)
        dist = dot * h
    else:
        dist = 0
    return dist

class polyplane():
    def __init__(self, point, normal):
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]
        self.nx = normal[0]
        self.ny = normal[1]
        self.nz = normal[2]

class vertpoint():
    def __init__(self, point):
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]

def cull(point, p_points):
    l = len(p_points)
    P_points = p_points[:]
    P_points.append(P_points[0])
    a = 0
    for i in range(0, l):
        polypoint = P_points[i]
        polypoint1 = P_points[i + 1]
        v1 = vector(polypoint, point)
        v2 = vector(polypoint1, point)
        dot = dot_product(v1, v2)
        if dot < -1:
            dot = -1
        elif dot > 1:
            dot = 1
        a += math.acos(dot)

    if int(a * tolerance) == int(pi2 * tolerance):
        return True
    else:
        return False

def cull1(point, p_points):
    l = len(p_points)
    P_points = p_points[:]
    P_points.append(P_points[0])
    a = 0
    for i in range(0, l):
        polypoint = P_points[i]
        polypoint1 = P_points[i + 1]
        v1 = vector2d(polypoint, point)
        v2 = vector2d(polypoint1, point)
        dot = dot_product2d(v1, v2)
        if dot < -1:
            dot = -1
        elif dot > 1:
            dot = 1
        a += math.acos(dot)

    if int(a * tolerance) == int(pi2 * tolerance):
        return True
    else:
        return False

edgevector = [0, 0, 1]

def uv_value(point, p_points, uvs):
    polycenter3d = [0.0, 0.0, 0.0]
    for p in p_points:
        polycenter3d[0] += p[0]
        polycenter3d[1] += p[1]
        polycenter3d[2] += p[2]
    n_of_points = len(p_points)
    polycenter3d[0] /= n_of_points
    polycenter3d[1] /= n_of_points
    polycenter3d[2] /= n_of_points
    distance = sqrt((polycenter3d[0] - point[0])**2 + (polycenter3d[1] - point[1])**2 + (polycenter3d[2] - point[2])**2)
    circumference = 0.0
    P = p_points[:]
    F = P.pop(0)
    P.append(F)
    for x, p in enumerate(p_points):
        circumference += sqrt((p[0] - P[x][0])**2 + (p[1] - P[x][1])**2 + (p[2] - P[x][2])**2)
    if circumference == 0.0:
        return uvs[0]
    Weight = distance / circumference
    weights = []
    D = 0.0
    for p in p_points:
        dist = sqrt((p[0] - point[0])**2 + (p[1] - point[1])**2 + (p[2] - point[2])**2)
        D += dist
        weights.append(dist)
    if D == 0.0:
        return uvs[0]
    for w in weights:
        w /= D

    polycenter2d = [0.0, 0.0]
    for uv in uvs:
        polycenter2d[0] += uv[0]
        polycenter2d[1] += uv[1]
    polycenter2d[0] /= n_of_points
    polycenter2d[1] /= n_of_points
    uv_circumference = 0.0
    UV = uvs[:]
    F = UV.pop(0)
    UV.append(F)
    for x, uv in enumerate(uvs):
        uv_circumference += sqrt((uv[0] - UV[x][0])**2 + (uv[1] - UV[x][1])**2)
    if uv_circumference == 0.0:
        return uvs[0]
    distance = Weight * uv_circumference
    vect = [0.0, 0.0]
    for x, uv in enumerate(uvs):
        vect[0] += (uv[0] - polycenter2d[0]) * weights[x]
        vect[1] += (uv[1] - polycenter2d[1]) * weights[x]
    length = sqrt(vect[0]**2 + vect[1]**2)
    vect[0] /= length
    vect[1] /= length
    uv_location = [polycenter2d[0] - (vect[0] * distance),
                   polycenter2d[1] - (vect[1] * distance)]
    return uv_location

def projectpoints(points, vector, planenormal):
    C = []
    polynormal = cross(points[0], points[1], points[2])
    dot1 = dot_product(polynormal, vector)
    if dot1 > 0:
        planepoint = (-planenormal[0], -planenormal[1], -planenormal[2])
        plane = polyplane(planepoint, planenormal)
        dot = dot_product(planenormal, vector)
        if dot < 0:
            for i in points:
                point = vertpoint(i)
                dist = nearest(point, plane)
                dist /= dot
                n = (point.x + vector[2] * dist, point.y + vector[2] * dist, point.z + vector[2] * dist)
                C.append(n)
    return C

def bounds(x, y, level, polypoints):
    xless = 0
    xmore = 0
    yless = 0
    ymore = 0
    count = 0
    for i in polypoints:
        count += 1
        if i[0] < x - level:
            xless += 1
        if i[0] > x + level:
            xmore += 1
        if i[1] < y - level:
            yless += 1
        if i[1] > y + level:
            ymore += 1
    if (xless == count or
        xmore == count or
        yless == count or
        ymore == count):
        return False
    return True

def fireray(x, y, faces, level, step, dim, uvfaces, pix, w = 0, h = 0):
    C = []
    Colors = []
    Texels = []
    if pix and uvfaces:
        UVfaces = iter(uvfaces)
    for f in faces:
        polypoints = f.verts()
        uvs = None
        if pix and uvfaces:
            uvs = next(UVfaces).texts()
        b = bounds(x, y, level, polypoints)
        if not b:
            continue
        planenormal = cross(polypoints[0], polypoints[1], polypoints[2])
        dot = dot_product(planenormal, edgevector)
        if dot:
            point = vertpoint([x, y, -2.0])
            plane = polyplane(polypoints[1], planenormal)
            dist = nearest(point, plane)
            dist /= dot
            n = (point.x, point.y, point.z + edgevector[2] * dist)
            c = cull1(n, polypoints)
            if c:
                N = int(n[2] * dim * tolerance) / float(dim * tolerance)
                if uvs:
                    texel = uv_value(n, polypoints, uvs)
                    Texels.append(texel)
                C.append(N)
    if pix:
        for texel in Texels:
            XX = int(w * divmod(texel[0], 1.0)[1])
            YY = int(h * divmod(texel[1], 1.0)[1])
            try:
                (r, g, b, a) = pix[XX, YY]
                Colors.append((r, g, b, a))
            except:
                print("XX, YY", XX, YY)
    C = list(set(C))
    M = []
    C.sort()
    D = C[:]
    if C:
        Z = - 1.0 + level
        c = C.pop(0)
        flag = False
        for z in range(int(dim / 2)):
            if Z >= c:
                if not C:
                    c = 2
                    flag = not flag
                else:
                    while C:
                        c = C.pop(0)
                        flag = not flag
                        if c > Z:
                            break
                        
            if flag:
                M.append(Z)
            Z += step
        # ----------------
        Z = 1.0 - level
        c = D.pop()
        flag = False
        for z in range(int(dim / 2)):
            if Z <= c:
                if not D:
                    c = -2
                    flag = not flag
                else:
                    while D:
                        c = D.pop()
                        flag = not flag
                        if c < Z:
                            break
                        
            if flag:
                M.append(Z)
            Z -= step
    if not Colors:
        Colors = [None,]
    return M, Colors

def scan(dim, size, faces, uvfaces, texture = None):
    pix = None
    w = 0
    h = 0
    r_g_b_a = False
    if texture and os.path.isfile(texture):
        img = Image.open(texture)
        if img.mode == 'RGBA':
            print("mode", img.mode)
            r_g_b_a = True
        else:
            r_g_b_a = False
            img = img.convert("RGBA")
        img = img.resize((512, 512), Image.ANTIALIAS)
        img = img.transpose(1)
        pix = img.load()
        w, h = img.size
    A = zeros((dim, dim, dim, 2), dtype=object)
    level = 1.0 / float(dim)
    step = level * 2.0
    X = - 1.0 + level
    Size = size
    for x in range(dim):
        Y = - 1.0 + level
        for y in range(dim):
            Z = - 1.0 + level
            v, col = fireray(X, Y, faces, level, step, dim, uvfaces, pix, w, h)
            if col[0] != None:
                lenv = len(v) - 1
                if lenv < 1:
                    lenv = 1
                rchange = (col[-1][0] - col[0][0]) / lenv
                gchange = (col[-1][1] - col[0][1]) / lenv
                bchange = (col[-1][2] - col[0][2]) / lenv
                achange = (col[-1][3] - col[0][3]) / lenv
                r = col[0][0]
                g = col[0][1]
                b = col[0][2]
                a = col[0][3]
            for z in range(dim):
                if Z in v:
                    if col[0] != None:
                        if r_g_b_a:
                            Size = size * (float(a) / 255.0)
                        color = (abs(r), abs(g), abs(b), abs(a))
                    else:
                        color = col[0]
                    A[x, y, z] = (Size, color)
                    Size = size
                    if col[0] != None:
                        r += rchange
                        g += gchange
                        b += bchange
                        a += achange
                Z += step
            Y += step
        X += step
    return A
