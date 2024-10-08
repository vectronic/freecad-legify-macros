# coding: UTF-8

from FreeCAD import Console, Placement, Rotation, Vector
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

DIMS_STUD_SPACING = 8
DIMS_PLATE_HEIGHT = 3.2
DIMS_BRICK_OUTER_REDUCTION = 0.1

DIMS_EDGE_FILLET = 0.1
DIMS_STUD_FILLET = 0.25

DIMS_TOP_THICKNESS = 1.1
DIMS_FLAT_SIDE_THICKNESS = 1.5
DIMS_RIBBED_SIDE_THICKNESS = 1.2

DIMS_SIDE_RIB_WIDTH = 0.7
DIMS_SIDE_RIB_DEPTH = 0.3

DIMS_STUD_OUTER_RADIUS = 2.45
DIMS_STUD_INNER_RADIUS = 1.6
DIMS_STUD_FLAT_THICKNESS = 0.9
DIMS_STUD_HEIGHT = 1.8
DIMS_STUD_INSIDE_HOLE_RADIUS = 1.2
DIMS_STUD_INSIDE_HOLE_TOP_OFFSET = 1.7

DIMS_STICK_OUTER_RADIUS = 1.5
DIMS_STICK_INNER_RADIUS = 0.75
DIMS_STICK_RIB_THICKNESS = 0.9
DIMS_STICK_RIB_BOTTOM_OFFSET = 2.15
DIMS_STICK_AND_TUBE_BOTTOM_INSET = 0.2

DIMS_TUBE_OUTER_RADIUS = 3.25
DIMS_TUBE_INNER_RADIUS = 2.45
DIMS_TUBE_FLAT_THICKNESS = 0.9
DIMS_TUBE_RIB_THICKNESS = 0.8
DIMS_TUBE_RIB_BOTTOM_OFFSET = 2.15

DIMS_SIDE_STUD_CENTRE_HEIGHT = 5.7

DIMS_TECHNIC_HOLE_CENTRE_HEIGHT = 5.8
DIMS_TECHNIC_HOLE_OUTER_RADIUS = 3.55
DIMS_TECHNIC_HOLE_INNER_RADIUS = 2.4
DIMS_TECHNIC_HOLE_COUNTERBORE_RADIUS = 3.05
DIMS_TECHNIC_HOLE_COUNTERBORE_DEPTH = 0.85

DIMS_PIN_COLLAR_DEPTH = 0.8
DIMS_PIN_COLLAR_RADIUS = 2.95
DIMS_PIN_OUTER_RADIUS = 2.35
DIMS_PIN_INNER_RADIUS = 1.7
DIMS_PIN_LENGTH = 8
DIMS_PIN_FLANGE_HEIGHT = 0.25
DIMS_PIN_FLANGE_DEPTH = 0.75
DIMS_PIN_NOTCH_WIDTH = 0.9
DIMS_PIN_NOTCH_DEPTH = 2.8
DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS = 0.35

# Part Design Constants

SKETCH_GEOMETRY_VERTEX_START_INDEX = 1
SKETCH_GEOMETRY_VERTEX_END_INDEX = 2
SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX = 3

# Origin geometry is indexed at -1
SKETCH_GEOMETRY_ORIGIN_INDEX = -1
# External geometry is indexed from -3 descending! https://forum.freecadweb.org/viewtopic.php?t=24211
SKETCH_GEOMETRY_FIRST_EXTERNAL_INDEX = -3

PAD_TYPE_DIMENSION = 0
PAD_TYPE_THROUGH_ALL = 1
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


def add_circle_to_sketch(sketch, radius, x, y, as_arcs):
    Console.PrintMessage("add_circle_to_sketch({},{},{},{})\n".format(radius, x, y, as_arcs))

    geometries = []
    constraints = []

    if as_arcs:

        # Construction lines
        geometries.append(Part.LineSegment(xy_plane_bottom_left_vector(), xy_plane_top_right_vector()))
        constraints.append(Sketcher.Constraint('Angle', 0, 45 * math.pi / 180))
        constraints.append(Sketcher.Constraint("Distance",
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               radius * 2))

        # Drawn as two arcs instead of one circle so that an edge appears in geometry - this allows
        # measurement between vertices of distance between arc and flat edge
        rad1 = 135 * math.pi / 180
        rad2 = 445 * math.pi / 180
        rad3 = 45 * math.pi / 180
        rad4 = 225 * math.pi / 180

        # arcs
        geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), radius), rad1, rad2))
        geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), radius), rad3, rad4))

        # position arc midpoint
        constraints.append(Sketcher.Constraint("DistanceX",
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               1, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               x))
        constraints.append(Sketcher.Constraint("DistanceY",
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               1, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               y))
        constraints.append(Sketcher.Constraint('PointOnObject',
                                               1, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               0))
        constraints.append(Sketcher.Constraint('PointOnObject',
                                               2, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               0))

        # position arc and construction endpoints
        constraints.append(Sketcher.Constraint('Coincident',
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               1, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint('Coincident',
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               2, SKETCH_GEOMETRY_VERTEX_END_INDEX))
        constraints.append(Sketcher.Constraint('Coincident',
                                               0, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               1, SKETCH_GEOMETRY_VERTEX_END_INDEX))
        constraints.append(Sketcher.Constraint('Coincident',
                                               0, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               2, SKETCH_GEOMETRY_VERTEX_START_INDEX))

        sketch.addGeometry(geometries, False)
        sketch.addConstraint(constraints)

        # Set construction lines
        sketch.toggleConstruction(0)
    else:
        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", 0, radius))
        constraints.append(Sketcher.Constraint("DistanceX",
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               x))
        constraints.append(Sketcher.Constraint("DistanceY",
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               y))
        sketch.addGeometry(geometries, False)
        sketch.addConstraint(constraints)


def add_inner_circle_with_flats_to_sketch(sketch, outer_radius, inner_radius, flat_thickness, x_offset, y_offset):
    Console.PrintMessage("add_inner_circle_with_flats_to_sketch({},{},{},{},{})\n"
                         .format(outer_radius, inner_radius, flat_thickness, x_offset, y_offset))

    geometries = []
    constraints = []

    # Construction line
    geometries.append(Part.LineSegment(xy_plane_bottom_left_vector(), xy_plane_top_right_vector()))
    constraints.append(Sketcher.Constraint('Angle', 0, 45 * math.pi / 180))
    constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_END_INDEX, x_offset))
    constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                           SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                           SKETCH_GEOMETRY_VERTEX_END_INDEX, y_offset))
    constraints.append(Sketcher.Constraint("Distance", 0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_END_INDEX, outer_radius))

    # Four Line Segments
    x1 = (DIMS_STUD_SPACING / 2) - 2
    x2 = (DIMS_STUD_SPACING / 2) - 1
    x3 = (DIMS_STUD_SPACING / 2) + 1
    x4 = (DIMS_STUD_SPACING / 2) + 2
    y1 = (DIMS_STUD_SPACING / 2) - 2
    y2 = (DIMS_STUD_SPACING / 2) - 1
    y3 = (DIMS_STUD_SPACING / 2) + 1
    y4 = (DIMS_STUD_SPACING / 2) + 2

    geometries.append(Part.LineSegment(Vector(x2, y1, 0), Vector(x1, y2, 0)))
    geometries.append(Part.LineSegment(Vector(x1, y3, 0), Vector(x2, y4, 0)))
    geometries.append(Part.LineSegment(Vector(x3, y4, 0), Vector(x4, y3, 0)))
    geometries.append(Part.LineSegment(Vector(x4, y2, 0), Vector(x3, y1, 0)))

    # Four Arcs
    rad1 = 160 * math.pi / 180
    rad2 = 200 * math.pi / 180
    rad3 = 70 * math.pi / 180
    rad4 = 110 * math.pi / 180
    rad5 = -20 * math.pi / 180
    rad6 = 20 * math.pi / 180
    rad7 = -110 * math.pi / 180
    rad8 = -70 * math.pi / 180

    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), inner_radius), rad1, rad2))
    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), inner_radius), rad3, rad4))
    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), inner_radius), rad5, rad6))
    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(4, 4, 0), Vector(0, 0, 1), inner_radius), rad7, rad8))

    # Lines equal
    constraints.append(Sketcher.Constraint('Equal', 1, 2))
    constraints.append(Sketcher.Constraint('Equal', 1, 3))
    constraints.append(Sketcher.Constraint('Equal', 1, 4))

    # Lines parallel/perpendicular to construction line
    # Use angle constrain instead of parallel/perpendicular so that they
    # can't 'flip' and fail to resolve the constraints
    constraints.append(Sketcher.Constraint('Angle', 1, 135 * math.pi / 180))
    constraints.append(Sketcher.Constraint('Angle', 2, 45 * math.pi / 180))
    constraints.append(Sketcher.Constraint('Angle', 3, -45 * math.pi / 180))
    constraints.append(Sketcher.Constraint('Angle', 4, -135 * math.pi / 180))

    # All arcs centred
    constraints.append(Sketcher.Constraint('Coincident',
                                           5, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           6, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           7, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           8, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_END_INDEX))

    # All equal radius arcs
    constraints.append(Sketcher.Constraint('Radius', 5, inner_radius))
    constraints.append(Sketcher.Constraint('Equal', 5, 6))
    constraints.append(Sketcher.Constraint('Equal', 5, 7))
    constraints.append(Sketcher.Constraint('Equal', 5, 8))

    # Link arcs to segments
    constraints.append(Sketcher.Constraint('Coincident',
                                           1, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           8, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           5, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           2, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           5, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           6, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           3, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           6, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           3, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           7, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           4, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           7, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint('Coincident',
                                           4, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           8, SKETCH_GEOMETRY_VERTEX_END_INDEX))

    # The critical measurement: distance to end of construction line
    constraints.append(Sketcher.Constraint('Distance', 0, SKETCH_GEOMETRY_VERTEX_START_INDEX, 1, flat_thickness))

    sketch.addGeometry(geometries, False)
    sketch.addConstraint(constraints)

    # Set construction lines
    sketch.toggleConstruction(0)


def get_circle_edge_names(plane, inverted, offset, feature, radius):
    Console.PrintMessage("get_circle_edge_names({},{},{},{})\n".format(plane, inverted, offset, radius))

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


def get_arc_edge_names(plane, inverted, offset, feature, radius):
    Console.PrintMessage("get_arc_edge_names({},{},{})\n".format(inverted, offset, radius))

    plane_normal = plane.Shape.normalAt(0, 0)
    plane_normal = plane_normal if inverted else plane_normal.negative()

    edge_names = []
    potential_edges = []

    for i in range(0, len(feature.Shape.Faces)):
        face = feature.Shape.Faces[i]

        # desired faces are normal to plane
        face_normal = face.normalAt(0, 0)
        if face_normal.isEqual(plane_normal, 1e-7):

            # desired faces have an arc edge
            for j in range(0, len(face.Edges)):
                edge = face.Edges[j]

                # arcs have two vertices and arc needs to have a curve with desired radius
                if len(edge.Vertexes) == 2 and hasattr(edge, 'Curve') and hasattr(edge.Curve, 'Radius') \
                        and abs(edge.Curve.Radius - radius) < 1e-4:

                    # face with negative offset along normal lies in plane
                    offset_centre = edge.Vertexes[0].Point - (offset * face_normal)

                    if plane.Shape.isInside(offset_centre, 1e-6, True):
                        potential_edges.append(edge)

    for i in range(0, len(feature.Shape.Edges)):
        edge = feature.Shape.Edges[i]

        # arcs have two vertices and arc needs to have a curve with desired radius
        if len(edge.Vertexes) == 2 and hasattr(edge, 'Curve') and hasattr(edge.Curve, 'Radius') \
                and abs(edge.Curve.Radius - radius) < 1e-4:

            # arc needs to be in potential edges
            for j in range(0, len(potential_edges)):
                potential_edge = potential_edges[j]
                c1 = potential_edge.Curve
                c2 = edge.Curve
                if c1.Center == c2.Center and c1.Axis == c2.Axis:
                    edge_names.append("Edge" + repr(i + 1))
                    break
    return edge_names


def _render_pin_revolution(label, datum_line, body, doc):
    Console.PrintMessage("_render_pin_revolution({})\n".format(label))

    pin_revolution_sketch = body.newObject("Sketcher::SketchObject", label + "_pin_revolution_sketch")
    pin_revolution_sketch.AttachmentSupport = [(datum_line, '')]
    pin_revolution_sketch.MapMode = 'ObjectXY'
    pin_revolution_sketch.AttachmentOffset = Placement(Vector(0, 0, 0), Rotation(0, 90, 0))

    geometries = []
    constraints = []

    # construction line for rotation

    geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_top_left_vector()))
    constraints.append(Sketcher.Constraint("Horizontal", 0))

    # lines for profile

    geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_top_left_vector()))
    constraints.append(Sketcher.Constraint('Horizontal', 1))

    geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_bottom_left_vector()))
    constraints.append(Sketcher.Constraint('Vertical', 2))

    geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_top_left_vector()))
    constraints.append(Sketcher.Constraint('Horizontal', 3))

    geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_bottom_left_vector()))
    constraints.append(Sketcher.Constraint('Vertical', 4))

    geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_top_left_vector()))
    constraints.append(Sketcher.Constraint('Horizontal', 5))

    geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_bottom_left_vector()))
    constraints.append(Sketcher.Constraint('Vertical', 6))

    # constraints for profile

    constraints.append(Sketcher.Constraint("Coincident", 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           2, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint("Coincident", 2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           3, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint("Coincident", 3, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           4, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint("Coincident", 4, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           5, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint("Coincident", 5, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           6, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint("Coincident", 6, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           1, SKETCH_GEOMETRY_VERTEX_START_INDEX))

    constraints.append(Sketcher.Constraint('DistanceX',
                                           0, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           DIMS_PIN_LENGTH))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_START_INDEX, 0))

    # constraints for profile and construction line

    constraints.append(Sketcher.Constraint('DistanceX',
                                           1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           1, SKETCH_GEOMETRY_VERTEX_START_INDEX, DIMS_PIN_COLLAR_DEPTH))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           4, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           4, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           DIMS_PIN_OUTER_RADIUS - DIMS_PIN_INNER_RADIUS))
    constraints.append(Sketcher.Constraint('DistanceX',
                                           5, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           5, SKETCH_GEOMETRY_VERTEX_START_INDEX, DIMS_PIN_LENGTH))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           6, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           6, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           DIMS_PIN_COLLAR_RADIUS - DIMS_PIN_INNER_RADIUS))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           5, SKETCH_GEOMETRY_VERTEX_END_INDEX, DIMS_PIN_INNER_RADIUS))

    # constrain profile and construction line to datum point

    constraints.append(Sketcher.Constraint('DistanceX',
                                           0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX, 0))
    constraints.append(Sketcher.Constraint('DistanceX',
                                           1, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX, 0))

    pin_revolution_sketch.addGeometry(geometries, False)
    pin_revolution_sketch.addConstraint(constraints)

    # Set construction lines
    pin_revolution_sketch.toggleConstruction(0)

    doc.recompute()

    pin_revolution = body.newObject("PartDesign::Revolution", label + "_pin_revolution")
    pin_revolution.Angle = 360
    pin_revolution.Profile = pin_revolution_sketch
    pin_revolution.ReferenceAxis = (pin_revolution_sketch, ['Axis0'])

    doc.recompute()
    pin_revolution_sketch.ViewObject.Visibility = False

    return pin_revolution


def _render_pin_flange(label, datum_line, body, doc):
    Console.PrintMessage("_render_pin_flange({})\n".format(label))

    # path for additive pipe

    pin_pipe_path_sketch = body.newObject("Sketcher::SketchObject", label + "_pin_pipe_path_sketch")
    pin_pipe_path_sketch.AttachmentSupport = [(datum_line.AttachmentSupport[1][0]), (datum_line, '')]
    pin_pipe_path_sketch.MapMode = 'OZX'
    # note 0.005 adjustment to prevent seemingly a bug in freecad rendering
    pin_pipe_path_sketch.AttachmentOffset = Placement(Vector(0, 0, ((-1 * DIMS_PIN_FLANGE_DEPTH) / 2) - 0.005),
                                                      Rotation(0, 0, 0))

    geometries = []
    constraints = []

    geometries.append(Part.Ellipse(Vector(DIMS_PIN_OUTER_RADIUS, 0, 0),
                                   Vector(0, -1 * (DIMS_PIN_OUTER_RADIUS - DIMS_PIN_FLANGE_HEIGHT), 0),
                                   Vector(0, 0, 0)))

    pin_pipe_path_sketch.addGeometry(geometries, False)
    pin_pipe_path_sketch.exposeInternalGeometry(0)

    # constrain ellipse position

    constraints.append(Sketcher.Constraint('Coincident',
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX))

    # constrain ellipse shape

    constraints.append(Sketcher.Constraint('Horizontal', 1))
    constraints.append(Sketcher.Constraint('Distance', 1, 2 * DIMS_PIN_OUTER_RADIUS))
    constraints.append(Sketcher.Constraint('Distance', 2, 2 * (DIMS_PIN_OUTER_RADIUS - DIMS_PIN_FLANGE_HEIGHT)))

    pin_pipe_path_sketch.addConstraint(constraints)

    doc.recompute()

    # profile for additive pipe

    pin_pipe_profile_sketch = body.newObject("Sketcher::SketchObject", label + "_pin_pipe_profile_sketch")
    pin_pipe_profile_sketch.AttachmentSupport = [(pin_pipe_path_sketch, 'Edge1')]
    pin_pipe_profile_sketch.MapMode = 'ObjectXZ'

    geometries = []
    constraints = []

    geometries.append(Part.Ellipse(Vector(0, DIMS_PIN_FLANGE_DEPTH / 2, 0),
                                   Vector(-1 * DIMS_PIN_FLANGE_HEIGHT, 0, 0),
                                   Vector(0, 0, 0)))

    pin_pipe_profile_sketch.addGeometry(geometries, False)
    pin_pipe_profile_sketch.exposeInternalGeometry(0)

    # constrain ellipse position

    constraints.append(Sketcher.Constraint('DistanceX',
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           DIMS_PIN_OUTER_RADIUS))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           0))

    # constrain ellipse shape

    constraints.append(Sketcher.Constraint('Horizontal', 2))
    constraints.append(Sketcher.Constraint('Distance', 1, DIMS_PIN_FLANGE_DEPTH))
    constraints.append(Sketcher.Constraint('Distance', 2, DIMS_PIN_FLANGE_HEIGHT * 2))

    pin_pipe_profile_sketch.addConstraint(constraints)

    doc.recompute()

    # additive pipe for pin flange

    pin_pipe = body.newObject("PartDesign::AdditivePipe", label + "_pin_pipe")
    pin_pipe.Profile = pin_pipe_profile_sketch
    pin_pipe.Spine = pin_pipe_path_sketch

    doc.recompute()

    pin_pipe_path_sketch.ViewObject.Visibility = False
    pin_pipe_profile_sketch.ViewObject.Visibility = False

    return pin_pipe


def _render_pin_notch(label, datum_line, body, doc):
    Console.PrintMessage("_render_pin_notch({})\n".format(label))

    # sketch for notch

    pin_notch_sketch = body.newObject("Sketcher::SketchObject", label + "_pin_notch_sketch")
    pin_notch_sketch.AttachmentSupport = [(datum_line.AttachmentSupport[1][0]), (datum_line, '')]
    pin_notch_sketch.MapMode = 'OYZ'
    pin_notch_sketch.AttachmentOffset = Placement(Vector(0, 0, DIMS_PIN_OUTER_RADIUS), Rotation(0, 0, 0))

    geometries = []
    constraints = []

    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(0, -1 * DIMS_PIN_NOTCH_DEPTH, 0),
                                                   Vector(0, 0, 1),
                                                   DIMS_PIN_NOTCH_WIDTH / 2),
                                       math.pi, 0))
    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(1, -1 * DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS, 0),
                                                   Vector(0, 0, 1),
                                                   DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS),
                                       math.pi / 2, math.pi))
    geometries.append(Part.ArcOfCircle(Part.Circle(Vector(-1, -1 * DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS, 0),
                                                   Vector(0, 0, 1),
                                                   DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS),
                                       0, math.pi / 2))

    geometries.append(Part.LineSegment(Vector(-1, 0, 0), Vector(-1,
                                                                -1 * (DIMS_PIN_NOTCH_DEPTH -
                                                                      DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS -
                                                                      (DIMS_PIN_NOTCH_WIDTH / 2)), 0)))
    geometries.append(Part.LineSegment(Vector(1, 0, 0), Vector(1,
                                                               -1 * (DIMS_PIN_NOTCH_DEPTH -
                                                                     DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS -
                                                                     (DIMS_PIN_NOTCH_WIDTH / 2)), 0)))
    geometries.append(Part.LineSegment(Vector(-1, 0, 0), Vector(1, 0, 0)))

    # connect and position notch shape

    constraints.append(Sketcher.Constraint("Vertical", 3))
    constraints.append(Sketcher.Constraint("Vertical", 4))
    constraints.append(Sketcher.Constraint("Horizontal", 5))

    # opening horizontal line

    constraints.append(Sketcher.Constraint('DistanceY',
                                           5, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           0))

    # internal notch end

    constraints.append(Sketcher.Constraint('DistanceY',
                                           0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           DIMS_PIN_NOTCH_DEPTH))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           0))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           0))

    # right opening arc

    constraints.append(Sketcher.Constraint('DistanceX',
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           1, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           (DIMS_PIN_NOTCH_WIDTH / 2) + DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))
    constraints.append(Sketcher.Constraint('DistanceX',
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           1, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           (DIMS_PIN_NOTCH_WIDTH / 2) + DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           1, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))

    # left opening arc

    constraints.append(Sketcher.Constraint('DistanceX',
                                           2, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           (DIMS_PIN_NOTCH_WIDTH / 2) + DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))
    constraints.append(Sketcher.Constraint('DistanceX',
                                           2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           (DIMS_PIN_NOTCH_WIDTH / 2) + DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           2, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))
    constraints.append(Sketcher.Constraint('DistanceY',
                                           2, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))

    # join geometries

    constraints.append(Sketcher.Constraint("Coincident",
                                           5, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           2, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint("Coincident",
                                           5, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           1, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint("Coincident",
                                           1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           4, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint("Coincident",
                                           2, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                           3, SKETCH_GEOMETRY_VERTEX_START_INDEX))
    constraints.append(Sketcher.Constraint("Coincident",
                                           4, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_END_INDEX))
    constraints.append(Sketcher.Constraint("Coincident",
                                           3, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                           0, SKETCH_GEOMETRY_VERTEX_START_INDEX))

    pin_notch_sketch.addGeometry(geometries, False)
    pin_notch_sketch.addConstraint(constraints)

    doc.recompute()

    # pocket for notch

    pin_notch_pocket = body.newObject("PartDesign::Pocket", label + "_pin_notch_pocket")
    pin_notch_pocket.Type = PAD_TYPE_DIMENSION
    pin_notch_pocket.Profile = pin_notch_sketch
    pin_notch_pocket.Length = DIMS_PIN_OUTER_RADIUS * 2

    doc.recompute()

    pin_notch_sketch.ViewObject.Visibility = False

    return pin_notch_pocket


def render_pin(label, datum_line, body, doc):
    Console.PrintMessage("render_pin()\n")

    pin_revolution = _render_pin_revolution(label, datum_line, body, doc)

    pin_flange = _render_pin_flange(label, datum_line, body, doc)

    pin_notch_pocket = _render_pin_notch(label, datum_line, body, doc)

    return [pin_revolution, pin_flange, pin_notch_pocket]
