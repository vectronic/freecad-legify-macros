# coding: UTF-8

from FreeCAD import Console
from FreeCAD import Vector
import math
import Part
import Sketcher


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

DIMS_TOP_THICKNESS = 1.1
DIMS_FLAT_SIDE_THICKNESS = 1.5
DIMS_RIBBED_SIDE_THICKNESS = 1.2

DIMS_SIDE_RIB_WIDTH = 0.65
DIMS_SIDE_RIB_DEPTH = 0.3

DIMS_STUD_OUTER_RADIUS = 2.5
DIMS_STUD_INNER_RADIUS = 1.65
DIMS_STUD_FLAT_THICKNESS = 0.9
DIMS_STUD_HEIGHT = 1.8
DIMS_STUD_INSIDE_HOLE_RADIUS = 1.2
DIMS_STUD_INSIDE_HOLE_TOP_OFFSET = 1.7

DIMS_STICK_OUTER_RADIUS = 1.55
DIMS_STICK_INNER_RADIUS = 0.8
DIMS_STICK_RIB_THICKNESS = 0.8
DIMS_STICK_RIB_BOTTOM_OFFSET = 2.15
DIMS_STICK_AND_TUBE_BOTTOM_INSET = 0.15

DIMS_TUBE_OUTER_RADIUS = 4 * math.sqrt(2) - 2.4
DIMS_TUBE_INNER_RADIUS = 2.5
DIMS_TUBE_FLAT_THICKNESS = 0.9
DIMS_TUBE_RIB_THICKNESS = 0.8
DIMS_TUBE_RIB_BOTTOM_OFFSET = 2.15

DIMS_SIDE_STUD_CENTRE_HEIGHT = 5.7

DIMS_TECHNIC_HOLE_CENTRE_HEIGHT = 5.8
DIMS_TECHNIC_HOLE_OUTER_RADIUS = 3
DIMS_TECHNIC_HOLE_INNER_RADIUS = 2.45
DIMS_TECHNIC_HOLE_COUNTERBORE_RADIUS = 3.1
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


def add_circle_to_sketch(sketch, radius, x, y):
    Console.PrintMessage("add_circle_to_sketch({0})\n".format(radius))

    geometries = []
    constraints = []

    geometries.append(Part.Circle())
    constraints.append(Sketcher.Constraint("Radius", 0, radius))
    constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, x))
    constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, y))

    sketch.addGeometry(geometries, False)
    sketch.addConstraint(constraints)


def add_inner_circle_with_flats_to_sketch(sketch, outer_construction_radius, radius, flat_thickness,
                                          outer_circle_is_construction, x_offset, y_offset):
    Console.PrintMessage("add_inner_circle_with_flats_to_sketch({0},{1},{2},{3},{4},{5})\n"
                         .format(outer_construction_radius, radius, flat_thickness, outer_circle_is_construction,
                                 x_offset, y_offset))

    geometries = []
    constraints = []

    # Outer circle for construction
    geometries.append(Part.Circle())
    constraints.append(Sketcher.Constraint("Radius", 0, outer_construction_radius))
    constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, x_offset))
    constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, y_offset))

    # Tangent construction line
    geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_bottom_right_vector()))
    constraints.append(Sketcher.Constraint('Angle', 1, -45 * math.pi / 180))
    constraints.append(Sketcher.Constraint('Tangent', 1, 0))
    constraints.append(Sketcher.Constraint('PointOnObject', 1, SKETCH_GEOMETRY_VERTEX_END_INDEX, 0))
    constraints.append(Sketcher.Constraint("DistanceX", 1, SKETCH_GEOMETRY_VERTEX_START_INDEX, 1,
                                           SKETCH_GEOMETRY_VERTEX_END_INDEX, 1))

    # Four Line Segments
    x1 = (DIMS_STUD_SPACING_INNER / 2) - 2
    x2 = (DIMS_STUD_SPACING_INNER / 2) - 1
    x3 = (DIMS_STUD_SPACING_INNER / 2) + 1
    x4 = (DIMS_STUD_SPACING_INNER / 2) + 2
    y1 = (DIMS_STUD_SPACING_INNER / 2) - 2
    y2 = (DIMS_STUD_SPACING_INNER / 2) - 1
    y3 = (DIMS_STUD_SPACING_INNER / 2) + 1
    y4 = (DIMS_STUD_SPACING_INNER / 2) + 2

    geometries.append(Part.LineSegment(Vector(x2, y1, 0), Vector(x1, y2, 0)))
    geometries.append(Part.LineSegment(Vector(x1, y3, 0), Vector(x2, y4, 0)))
    geometries.append(Part.LineSegment(Vector(x3, y4, 0), Vector(x4, y3, 0)))
    geometries.append(Part.LineSegment(Vector(x4, y2, 0), Vector(x3, y1, 0)))

    constraints.append(Sketcher.Constraint('Equal', 2, 4))
    constraints.append(Sketcher.Constraint('Equal', 3, 5))
    constraints.append(Sketcher.Constraint('Equal', 2, 3))
    constraints.append(Sketcher.Constraint('Parallel', 3, 5))
    constraints.append(Sketcher.Constraint('Parallel', 2, 4))
    constraints.append(Sketcher.Constraint('Perpendicular', 2, 3))

    # Parallel to tangent line as
    constraints.append(Sketcher.Constraint('Parallel', 1, 2))

    # Four Arcs
    rad1 = 160 * math.pi / 180
    rad2 = 200 * math.pi / 180
    rad3 = 70 * math.pi / 180
    rad4 = 110 * math.pi / 180
    rad5 = -20 * math.pi / 180
    rad6 = 20 * math.pi / 180
    rad7 = -110 * math.pi / 180
    rad8 = -70 * math.pi / 180

    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), radius), rad1, rad2))
    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), radius), rad3, rad4))
    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), radius), rad5, rad6))
    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), radius), rad7, rad8))

    # All arcs centred
    constraints.append(Sketcher.Constraint('Coincident', 6, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 7, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 8, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 9, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX))

    # All equal radius arcs
    constraints.append(Sketcher.Constraint('Radius', 6, radius))
    constraints.append(Sketcher.Constraint('Equal', 6, 7))
    constraints.append(Sketcher.Constraint('Equal', 6, 8))
    constraints.append(Sketcher.Constraint('Equal', 6, 9))

    # Link arcs to segments
    constraints.append(Sketcher.Constraint('Coincident', 2, SKETCH_GEOMETRY_VERTEX_END_INDEX, 6,
                                           SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 6, SKETCH_GEOMETRY_VERTEX_START_INDEX, 3,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 3, SKETCH_GEOMETRY_VERTEX_END_INDEX, 7,
                                           SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 7, SKETCH_GEOMETRY_VERTEX_START_INDEX, 4,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 4, SKETCH_GEOMETRY_VERTEX_END_INDEX, 8,
                                           SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 8, SKETCH_GEOMETRY_VERTEX_START_INDEX, 5,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 5, SKETCH_GEOMETRY_VERTEX_END_INDEX, 9,
                                           SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident', 9, SKETCH_GEOMETRY_VERTEX_START_INDEX, 2,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX))

    # The critical measurement: distance to tangent construction line
    constraints.append(Sketcher.Constraint('Distance', 1, SKETCH_GEOMETRY_VERTEX_END_INDEX, 2, flat_thickness))

    sketch.addGeometry(geometries, False)
    sketch.addConstraint(constraints)

    # Set circle as a construction line if specified
    if outer_circle_is_construction:
        sketch.toggleConstruction(0)

    # Set tangent line as a construction line
    sketch.toggleConstruction(1)


def get_circle_edge_names(plane, inverted, offset, feature, radius):
    Console.PrintMessage("get_circle_edge_names({0},{1},{2},{3},{4})\n"
                         .format(plane, inverted, offset, feature, radius))

    plane_normal = plane.Shape.normalAt(0, 0)
    plane_normal = plane_normal if inverted else plane_normal.negative()

    edge_names = []
    potential_edges = []

    for i in range(0, len(feature.Shape.Faces)):
        face = feature.Shape.Faces[i]

        # desired faces are normal to plane
        face_normal = face.normalAt(0, 0)
        if face_normal.isEqual(plane_normal, 1e-7):

            # desired faces have a circle edge
            for j in range(0, len(face.Edges)):
                edge = face.Edges[j]

                # circles have only one vertex and a LastParameter of 2 PI
                if len(edge.Vertexes) == 1 and edge.LastParameter > 6.28:

                    # circle needs to have desired radius
                    if edge.Curve.Radius == radius:

                        # face with negative offset along normal lies in plane
                        offset_centre = edge.Vertexes[0].Point - (offset * face_normal)

                        if plane.Shape.isInside(offset_centre, 1e-7, True):
                            potential_edges.append(edge)

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
