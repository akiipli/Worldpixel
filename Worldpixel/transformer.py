#
# Worldpixel module
# authors: A. Kiipli
#

import math
from numpy import *

""" Classy:

    def move_conform(self, center):
        self.x += center[0]
        self.y += center[1]
        self.z += center[2]

    def move_around(self, center): // give_depth // x = (x_rotated + self.x_pos) / factor
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

    def restore_xyz_baked(self):
        self.x = self.x_baked
        self.y = self.y_baked
        self.z = self.z_baked

    def bake_rotation(self):
        self.x = self.x_rotated
        self.y = self.y_rotated
        self.z = self.z_rotated
"""

rotation_amount = pi / 180.0

class Transformer():
    def __init__(self,
                 voxels = [],           # voxels type voxel3d
                 vector = (0, 1, 0),
                 angle = 0,
                 position = [0, 0, 0],
                 superior = None,
                 name = "",
                 index = 0):
        self.voxels = voxels
        self.angle = angle              # rotation angle around Tvector
        self.direction = rotation_amount
                                        # or vec type vector
        self.vector = vector            # transformed local vector
        self.local = vector             # local vector like (0, 1, 0)
        self.center = position        # Tposition represents localized
                                        # center to rotate around
        self.conform_position = position
                                        # Tconform_position is position
                                        # that is applyed before rotation
        self.parent = superior          # parent type implements Transformer
        self.vec_x = (1, 0, 0)
        self.vec_y = (0, 1, 0)
        self.vec_z = (0, 0, 1)
        self.name = name
        self.local_conform = position   # this operates with conform_position
        self.local_position = position  # this operates with conform_position

        self.child_nodes = []
        self.child_voxel = []

        self.baked = False
        self.xyz_baked = False

        self.LOCAL = False
        self.index = index

    def get_index(self):
        return self.index

    def get_LOCAL(self):
        return self.LOCAL

    def get_angle(self):
        if self.LOCAL:
            return self.angle
        else:
            return self.parent.angle

    def get_vector(self):
        if self.LOCAL:
            return self.vector
        else:
            return self.parent.vector

    def get_center(self):
        if self.LOCAL:
            return self.center
        else:
            return self.parent.center
        
    def get_local(self):
        if self.LOCAL:
            local = "%d %d %d" % self.local
        else:
            local = "%d %d %d" % self.parent.local
        return local

    def set_LOCAL(self, value):
        self.LOCAL = value

    def set_direction(self, amount):
        self.direction = amount

    def set_angle(self, angle):
        if self.LOCAL:
            self.angle = angle
        else:
            self.parent.angle = angle

    def set_vector(self, vector):
        if self.LOCAL:
            self.local = vector
            self.localize_vector(vector)
        else:
            self.parent.local = vector

    def put_child_nodes(self, candidates):
        for i in candidates:
            if i not in self.child_nodes:
                i.parent = self
                self.child_nodes.append(i)

    def pop_child_nodes(self, candidates):
        for i in self.child_nodes:
            if i in candidates:
                i.parent = None
                self.child_nodes.pop(i)
                
    def collect_voxels(self):
        self.child_voxel = []
        self.get_child_voxels(self.child_voxel)

    def get_child_voxels(self, voxels):
        for c in self.child_nodes:
            voxels += c.voxels
            c.get_child_voxels(voxels)

    def localize(self, vector):
        self.localize_position()
        self.localize_vector(vector)

    def give_center_parent(self):
        if self.parent:
            return self.parent.give_center_parent()

    def localize_position(self):
        self.center = self.give_center_parent()
        print("CENTER", self.center)

    def collect_Vectors(self, Angle, Vector, Name):
        if self.parent:
            Angle.append(self.parent.angle)
            Vector.append(self.parent.vector)
            Name.append(self.parent.name)
            self.parent.collect_Vectors(Angle, Vector, Name)

    def give_vector_parent(self, vector):
        Angle = []
        Vector = []
        Name = []
        self.collect_Vectors(Angle, Vector, Name)
        for angle, space, name in reversed(list(zip(Angle, Vector, Name))):
            if space and angle:
                print("|{0[0]: 0.1f} {0[1]: 0.1f} {0[2]: 0.1f} | {1[0]: 0.1f} {1[1]: 0.1f} {1[2]: 0.1f} | {2: 2.2f} | {3:s}"
                      .format(vector, space, rad2deg(angle), name))
                vector = self.rotate_center(vector, space, angle)
        return vector

    def localize_vector(self, vector):
        if vector is None:
            vector = self.local
        self.local = vector
        self.vector = self.give_vector_parent(vector)
        self.vec_x = self.give_vector_parent((1, 0, 0))
        self.vec_y = self.give_vector_parent((0, 1, 0))
        self.vec_z = self.give_vector_parent((0, 0, 1))
##        print(self.vector)
        print(self.name)

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

    def reset_position(self, reset = True):
        conform_position = [-self.conform_position[0],
                            -self.conform_position[1],
                            -self.conform_position[2]]
        for voxel in (self.voxels + self.child_voxel):
            voxel.move_conform(conform_position)
        if reset:
            self.conform_position = [0, 0, 0]

    def move_conform(self, center = (0, 0, 0)):
        self.conform_position[0] += center[0]
        self.conform_position[1] += center[1]
        self.conform_position[2] += center[2]
        for voxel in (self.voxels + self.child_voxel):
            voxel.move_conform(center)

    def move_to_conform(self, center = (0, 0, 0)):
        for voxel in (self.voxels + self.child_voxel):
            voxel.move_conform(center)

    def switch_conform_position(self):
        self.local_conform = self.conform_position
        self.conform_position = self.local_position
        self.local_position = self.local_conform

    def bake_xyz_rotation(self):
        self.xyz_baked = True
        for i in self.child_nodes:
            i.xyz_baked = True
        voxels = list(set(self.voxels)) + self.child_voxel
        for i in voxels:
            i.rotate_around_vector(self.parent.center, self.parent.vector, self.parent.angle)
            i.bake_xyz_rotation()

    def bake_rotation(self, center = None, vector = None, angle = None):
        self.baked = True
        for i in self.child_nodes:
            i.baked = True
        voxels = list(set(self.voxels)) + self.child_voxel
        for i in voxels:
            i.rotate_around_vector(center, vector, angle)
            i.bake_rotation()

    def restore_xyz_baked(self):
        self.baked = False
        self.xyz_baked = False
        for i in self.child_nodes:
            i.baked = False
            i.xyz_baked = False
        voxels = list(set(self.voxels)) + self.child_voxel
        for i in voxels:
            i.restore_xyz_baked()

    def rotate3d_x(self, center = None, x_angle = 0):
        if x_angle is None:
            x_angle = self.get_angle()
            x_angle += self.direction
            self.set_angle(x_angle)
        elif x_angle == "self":
            x_angle = self.get_angle()
        if center is None:
            center = self.get_center()
        if self.LOCAL:
            if self.xyz_baked:
                self.bake_rotation(self.center, self.vec_x, self.angle)
            else:
                self.bake_xyz_rotation()
        else:
            for voxel in (self.voxels + self.child_voxel):
                if self.vec_x != (1, 0, 0):
                    voxel.rotate_around_vector(center, self.vec_x, x_angle)
                else:
                    voxel.rotate_at_x(center, x_angle)

    def rotate3d_y(self, center = None, y_angle = 0):
        if y_angle is None:
            y_angle = self.get_angle()
            y_angle += self.direction
            self.set_angle(y_angle)
        elif y_angle == "self":
            y_angle = self.get_angle()
        if center is None:
            center = self.get_center()
        if self.LOCAL:
            if self.xyz_baked:
                self.bake_rotation(self.center, self.vec_y, self.angle)
            else:
                self.bake_xyz_rotation()
        else:
            for voxel in (self.voxels + self.child_voxel):
                if self.vec_y != (0, 1, 0):
                    voxel.rotate_around_vector(center, self.vec_y, y_angle)
                else:
                    voxel.rotate_at_y(center, y_angle)

    def rotate3d_z(self, center = None, z_angle = 0):
        if z_angle is None:
            z_angle = self.get_angle()
            z_angle += self.direction
            self.set_angle(z_angle)
        elif z_angle == "self":
            z_angle = self.get_angle()
        if center is None:
            center = self.get_center()
        if self.LOCAL:
            if self.xyz_baked:
                self.bake_rotation(self.center, self.vec_z, self.angle)
            else:
                self.bake_xyz_rotation()
        else:
            for voxel in (self.voxels + self.child_voxel):
                if self.vec_z != (0, 0, 1):
                    voxel.rotate_around_vector(center, self.vec_z, z_angle)
                else:
                    voxel.rotate_at_z(center, z_angle)

    def rotate3d_vector(self, center = None, vector = None, angle = 0):
        if angle is None:
            angle = self.get_angle()
            angle += self.direction
            self.set_angle(angle)
        elif angle == "self":
            angle = self.get_angle()
        if center is None:
            center = self.get_center()
        if vector is None:
            vector = self.get_vector()
        if self.LOCAL:
            if self.xyz_baked:
                self.bake_rotation(self.center, self.vector, self.angle)
            else:
                self.bake_xyz_rotation()
        else:
            for voxel in (self.voxels + self.child_voxel):
                voxel.rotate_around_vector(center, vector, angle)
