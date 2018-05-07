# coding: UTF-8

import FreeCAD


def _enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type("Enum", (), enums)


TopStudStyle = _enum("NONE", "CLOSED", "OPEN")
SideStudStyle = _enum("NONE", "CLOSED", "OPEN", "HOLE")
PinStyle = _enum("NONE", "PIN", "AXLE")
HoleStyle = _enum("NONE", "HOLE", "AXLE")

DIMS_STUD_WIDTH_INNER = 8
DIMS_HALF_STUD_WIDTH_OUTER = 3.9
DIMS_PLATE_HEIGHT = 3.2
DIMS_EDGE_FILLET = 0.1
DIMS_TOP_THICKNESS = 1.0
DIMS_SIDE_THICKNESS = 1.2
DIMS_FULL_HEIGHT_SIDE_RIB_WIDTH = 0.6
DIMS_FULL_HEIGHT_SIDE_RIB_DEPTH = 0.3


def xy_plane_top_left_vector():
    return FreeCAD.Vector(-1, 1, 0)


def xy_plane_top_right_vector():
    return FreeCAD.Vector(1, 1, 0)


def xy_plane_bottom_right_vector():
    return FreeCAD.Vector(1, -1, 0)


def xy_plane_bottom_left_vector():
    return FreeCAD.Vector(-1, -1, 0)

