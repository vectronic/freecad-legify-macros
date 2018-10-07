# coding: UTF-8

import FreeCAD
import math


def _enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type("Enum", (), enums)


TopStudStyle = _enum("NONE", "CLOSED", "OPEN")
SideStudStyle = _enum("NONE", "OPEN", "HOLE")
PinStyle = _enum("NONE", "PIN", "AXLE")
HoleStyle = _enum("NONE", "HOLE", "AXLE")

DIMS_STUD_WIDTH_INNER = 8
DIMS_HALF_STUD_WIDTH_OUTER = 3.9
DIMS_PLATE_HEIGHT = 3.2
DIMS_EDGE_FILLET = 0.1
DIMS_TOP_THICKNESS = 1.0
DIMS_SIDE_THICKNESS = 1.2
DIMS_SIDE_RIB_WIDTH = 0.6
DIMS_SIDE_RIB_DEPTH = 0.3
# TODO - confirm dimension
DIMS_STICK_OUTER_RADIUS = 1
# TODO - confirm dimension
DIMS_STICK_INNER_RADIUS = 0.5
# TODO - confirm dimension
DIMS_STICK_RIB_THICKNESS = 0.8
# TODO - confirm dimension
DIMS_STICK_RIB_BOTTOM_OFFSET = 1.7
# TODO - confirm dimension
DIMS_STICK_AND_TUBE_BOTTOM_OFFSET = 0.2
DIMS_TUBE_OUTER_RADIUS = 4 * math.sqrt(2) - 2.4
DIMS_TUBE_INNER_RADIUS = 2.4
DIMS_TUBE_FLAT_THICKNESS = 1
DIMS_TUBE_RIB_THICKNESS = 0.8
DIMS_TUBE_RIB_BOTTOM_OFFSET = 1.7
# TODO - confirm dimension
DIMS_STUD_OUTER_RADIUS = 2.4
# TODO - confirm dimension
DIMS_STUD_INNER_RADIUS = 1.6
DIMS_STUD_HEIGHT = 1.8
DIMS_STUD_INSIDE_HOLE_RADIUS = 1.3
DIMS_STUD_INSIDE_HOLE_TOP_OFFSET = 0.1

SKETCH_GEOMETRY_VERTEX_START_INDEX = 1
SKETCH_GEOMETRY_VERTEX_END_INDEX = 2
SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX = 3

# Origin geometry is indexed at -1
SKETCH_GEOMETRY_ORIGIN_INDEX = -1
# External geometry is indexed from -3 descending! https://forum.freecadweb.org/viewtopic.php?t=24211
SKETCH_GEOMETRY_FIRST_CONSTRUCTION_INDEX = -3


def xy_plane_top_left_vector():
    return FreeCAD.Vector(-1, 1, 0)


def xy_plane_top_right_vector():
    return FreeCAD.Vector(1, 1, 0)


def xy_plane_bottom_right_vector():
    return FreeCAD.Vector(1, -1, 0)


def xy_plane_bottom_left_vector():
    return FreeCAD.Vector(-1, -1, 0)


def xz_plane_top_left_vector():
    return FreeCAD.Vector(-1, 0, 1)


def xz_plane_top_right_vector():
    return FreeCAD.Vector(1, 0, 1)


def xz_plane_bottom_right_vector():
    return FreeCAD.Vector(1, 0, -1)


def xz_plane_bottom_left_vector():
    return FreeCAD.Vector(-1, 0, -1)


def yz_plane_top_left_vector():
    return FreeCAD.Vector(0, -1, 1)


def yz_plane_top_right_vector():
    return FreeCAD.Vector(0, 1, 1)


def yz_plane_bottom_right_vector():
    return FreeCAD.Vector(0, 1, -1)


def yz_plane_bottom_left_vector():
    return FreeCAD.Vector(0, -1, -1)
