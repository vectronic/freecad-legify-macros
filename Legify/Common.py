# coding: UTF-8

from FreeCAD import Console
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

DIMS_STUD_SPACING_INNER = 8
DIMS_HALF_STUD_SPACING_OUTER = 3.9
DIMS_PLATE_HEIGHT = 3.2
DIMS_EDGE_FILLET = 0.1
DIMS_STUD_FILLET = 0.25
# TODO - confirm dimension
DIMS_TOP_THICKNESS = 1.0
DIMS_SIDE_THICKNESS = 1.2
DIMS_SIDE_RIB_WIDTH = 0.7
# TODO - confirm dimension
DIMS_SIDE_RIB_DEPTH = 0.3
# TODO - confirm dimension
DIMS_STICK_OUTER_RADIUS = 1.55
# TODO - confirm dimension
DIMS_STICK_INNER_RADIUS = 0.75
# TODO - confirm dimension
DIMS_STICK_RIB_THICKNESS = 0.8
# TODO - confirm dimension
DIMS_STICK_RIB_BOTTOM_OFFSET = 1.7
DIMS_STICK_AND_TUBE_BOTTOM_INSET = 0.3
DIMS_TUBE_OUTER_RADIUS = 4 * math.sqrt(2) - 2.4
DIMS_TUBE_INNER_RADIUS = 2.5
# TODO - confirm dimension
DIMS_TUBE_FLAT_THICKNESS = 1
DIMS_TUBE_RIB_THICKNESS = 0.75
# TODO - confirm dimension
DIMS_TUBE_RIB_BOTTOM_OFFSET = 1.7
DIMS_STUD_OUTER_RADIUS = 2.5
# TODO: add flat edges
DIMS_STUD_INNER_RADIUS = 1.65
# TODO - confirm dimension
DIMS_STUD_HEIGHT = 1.8
DIMS_STUD_INSIDE_HOLE_RADIUS = 1.25
DIMS_STUD_INSIDE_HOLE_TOP_OFFSET = 1.7
DIMS_SIDE_STUD_CENTRE_HEIGHT = 5.6
DIMS_TECHNIC_HOLE_CENTRE_HEIGHT = 5.75
# TODO - are technic vertical pins hollow?
# TODO - change to filled instead of tube
DIMS_TECHNIC_HOLE_OUTER_RADIUS = 2.95
DIMS_TECHNIC_HOLE_INNER_RADIUS = 2.4
DIMS_TECHNIC_HOLE_COUNTERBORE_RADIUS = 3.1
# TODO - confirm dimension
DIMS_TECHNIC_HOLE_COUNTERBORE_DEPTH = 0.8

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


def get_circle_edge_names(plane, inverted, feature, radius):
    Console.PrintMessage("get_circle_edge_names({0},{1},{2},{3})\n".format(plane, inverted, feature, radius))

    plane_normal = plane.Shape.normalAt(0, 0)
    plane_normal = plane_normal if inverted else plane_normal.negative()

    edge_names = []
    potential_edges = []

    for i in range(0, len(feature.Shape.Faces)):
        face = feature.Shape.Faces[i]

        # desired faces have two edges, both circles
        if len(face.Edges) == 2:

            # desired faces are normal to plane
            face_normal = face.normalAt(0, 0)
            if face_normal.isEqual(plane_normal, 1e-7):

                # circles have only one vertex and a LastParameter of 2 PI
                edge0 = face.Edges[0]
                edge1 = face.Edges[1]

                if len(edge0.Vertexes) == 1 and edge0.LastParameter > 6.28 and \
                        len(edge1.Vertexes) == 1 and edge1.LastParameter > 6.28:

                    # circle needs to have desired radius
                    if edge0.Curve.Radius == radius:
                        potential_edges.append(edge0)
                    if edge1.Curve.Radius == radius:
                        potential_edges.append(edge1)

    for i in range(0, len(feature.Shape.Edges)):
        edge = feature.Shape.Edges[i]

        # circles have only one vertex and a LastParameter of 2 PI
        if len(edge.Vertexes) == 1 and edge.LastParameter > 6.28:

            # circle needs to have desired radius
            if edge.Curve.Radius == radius:

                # circle needs to be in potential edges
                for j in range(0, len(potential_edges)):
                    potential_edge = potential_edges[j]
                    c1 = potential_edge.Curve
                    c2 = edge.Curve
                    if c1.Center == c2.Center and c1.Axis == c2.Axis:
                        edge_names.append("Edge" + repr(i + 1))
    return edge_names
