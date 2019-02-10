# coding: UTF-8

from FreeCAD import Vector
import math


def _enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type("Enum", (), enums)

# Brick Options

TopStudStyle = _enum("NONE", "CLOSED", "OPEN")
SideStudStyle = _enum("NONE", "OPEN", "HOLE")
PinStyle = _enum("NONE", "PIN", "AXLE")
HoleStyle = _enum("NONE", "HOLE", "AXLE")

# Brick Dimensions

DIMS_STUD_WIDTH_INNER = 8
DIMS_HALF_STUD_WIDTH_OUTER = 3.9
DIMS_PLATE_HEIGHT = 3.2
DIMS_EDGE_FILLET = 0.1
DIMS_TOP_THICKNESS = 1.0
DIMS_SIDE_THICKNESS = 1.2
DIMS_SIDE_RIB_WIDTH = 0.6
DIMS_SIDE_RIB_DEPTH = 0.3
# TODO - confirm dimension
DIMS_STICK_OUTER_RADIUS = 1.6
# TODO - confirm dimension
DIMS_STICK_INNER_RADIUS = 0.5
# TODO - confirm dimension
DIMS_STICK_RIB_THICKNESS = 0.8
# TODO - confirm dimension
DIMS_STICK_RIB_BOTTOM_OFFSET = 1.7
# TODO - confirm dimension
DIMS_STICK_AND_TUBE_BOTTOM_INSET = 0.2
DIMS_TUBE_OUTER_RADIUS = 4 * math.sqrt(2) - 2.4
DIMS_TUBE_INNER_RADIUS = 2.4
DIMS_TUBE_FLAT_THICKNESS = 1
DIMS_TUBE_RIB_THICKNESS = 0.8
DIMS_TUBE_RIB_BOTTOM_OFFSET = 1.7
# TODO - confirm dimension
DIMS_STUD_OUTER_RADIUS = 2.4
# TODO - confirm dimension
DIMS_STUD_INNER_RADIUS = 1.6
# TODO - confirm dimension
DIMS_STUD_HEIGHT = 1.8
DIMS_STUD_INSIDE_HOLE_RADIUS = 1.3
DIMS_STUD_INSIDE_HOLE_TOP_OFFSET = 0.1
# TODO - confirm dimension
DIMS_SIDE_FEATURE_CENTRE_HEIGHT = 5.6
# TODO - confirm dimension
DIMS_HOLE_OUTER_RADIUS = 3.4
# TODO - confirm dimension
DIMS_HOLE_INNER_RADIUS = 2.4
# TODO - confirm dimension
# TODO - confirm dimension
DIMS_HOLE_COUNTERBORE_RADIUS = 3.1
DIMS_HOLE_COUNTERBORE_DEPTH = 0.8

# Part Design Constants

SKETCH_GEOMETRY_VERTEX_START_INDEX = 1
SKETCH_GEOMETRY_VERTEX_END_INDEX = 2
SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX = 3

# Origin geometry is indexed at -1
SKETCH_GEOMETRY_ORIGIN_INDEX = -1
# External geometry is indexed from -3 descending! https://forum.freecadweb.org/viewtopic.php?t=24211
SKETCH_GEOMETRY_FIRST_CONSTRUCTION_INDEX = -3

PAD_TYPE_DIMENSION = 0
PAD_TYPE_TO_LAST = 1
PAD_TYPE_TO_FIRST = 2
PAD_TYPE_UP_TO_FACE = 3
PAD_TYPE_TWO_DIMENSIONS = 4

POCKET_TYPE_DIMENSION = 0
POCKET_TYPE_THROUGH_ALL = 1
POCKET_TYPE_TO_FIRST = 2
POCKET_TYPE_UP_TO_FACE = 3
POCKET_TYPE_TWO_DIMENSIONS = 4

ORIGIN_X_AXIS_INDEX = 0
ORIGIN_Y_AXIS_INDEX = 1
ORIGIN_Z_AXIS_INDEX = 2
ORIGIN_XY_PLANE_INDEX = 3
ORIGIN_XZ_PLANE_INDEX = 4
ORIGIN_YZ_PLANE_INDEX = 5


def xy_plane_top_left_vector():
    return Vector(-1, 1, 0)


def xy_plane_top_right_vector():
    return Vector(1, 1, 0)


def xy_plane_bottom_right_vector():
    return Vector(1, -1, 0)


def xy_plane_bottom_left_vector():
    return Vector(-1, -1, 0)


def xz_plane_top_left_vector():
    return Vector(-1, 0, 1)


def xz_plane_top_right_vector():
    return Vector(1, 0, 1)


def xz_plane_bottom_right_vector():
    return Vector(1, 0, -1)


def xz_plane_bottom_left_vector():
    return Vector(-1, 0, -1)


def yz_plane_top_left_vector():
    return Vector(0, -1, 1)


def yz_plane_top_right_vector():
    return Vector(0, 1, 1)


def yz_plane_bottom_right_vector():
    return Vector(0, 1, -1)


def yz_plane_bottom_left_vector():
    return Vector(0, -1, -1)
