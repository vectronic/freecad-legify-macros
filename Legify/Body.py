# coding: UTF-8

from FreeCAD import Console, Vector, Placement, Rotation
import Part
import Sketcher
from Legify.Common import *


class BodyRenderer(object):

    def __init__(self):
        Console.PrintMessage("BodyRenderer\n")

        self.width = None
        self.depth = None
        self.height = None

        self.hole_style = None
        self.holes_offset = None

        self.doc = None
        self.brick = None

        self.top_datum_plane = None
        self.top_inside_datum_plane = None
        self.front_inside_datum_plane = None
        self.back_inside_datum_plane = None
        self.left_inside_datum_plane = None
        self.right_inside_datum_plane = None

    @staticmethod
    def _add_horizontal_sketch_segment(geometries, constraints, length, hor_vec_start, hor_vec_end, reverse):
        Console.PrintMessage("_add_horizontal_sketch_segment({0},{1})\n".format(length, reverse))

        segment_count = len(geometries)

        geometries.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count))
        if segment_count > 0:
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                                   segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (-1 if reverse else 1) * length))

    @staticmethod
    def _add_vertical_sketch_segment(geometries, constraints, length, ver_vec_start, ver_vec_end, reverse):
        Console.PrintMessage("_add_vertical_sketch_segment({0},{1})\n".format(length, reverse))

        segment_count = len(geometries)

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count))
        if segment_count > 0:
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                                   segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (-1 if reverse else 1) * length))

    @staticmethod
    def _add_horizontal_sketch_segment_with_rib(geometries, constraints, length,
                                                hor_vec_start, hor_vec_end, ver_vec_start, ver_vec_end,
                                                reverse):
        Console.PrintMessage("_add_horizontal_sketch_segment_with_rib({0},{1})\n"
                             .format(length, reverse))

        segment_count = len(geometries)

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count))
        if segment_count > 0:
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                                   segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (-1 if reverse else 1) * DIMS_SIDE_RIB_DEPTH))

        geometries.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 1, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 1, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count + 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (-1 if reverse else 1) * DIMS_SIDE_RIB_WIDTH))

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 2))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 2, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 2, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count + 2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (1 if reverse else -1) * DIMS_SIDE_RIB_DEPTH))

        geometries.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 3))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 3, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 3, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count + 3, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (-1 if reverse else 1) * (length - DIMS_SIDE_RIB_WIDTH)))

    @staticmethod
    def _add_vertical_sketch_segment_with_rib(geometries, constraints, length,
                                              ver_vec_start, ver_vec_end, hor_vec_start, hor_vec_end,
                                              reverse):
        Console.PrintMessage("_add_vertical_sketch_segment_with_rib({0},{1})\n"
                             .format(length, reverse))

        segment_count = len(geometries)

        geometries.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count))
        if segment_count > 0:
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                                   segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (1 if reverse else -1) * DIMS_SIDE_RIB_DEPTH))

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 1, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 1, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count + 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (-1 if reverse else 1) * DIMS_SIDE_RIB_WIDTH))

        geometries.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 2))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 2, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 2, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count + 2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (-1 if reverse else 1) * DIMS_SIDE_RIB_DEPTH))

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 3))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 3, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 3, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count + 3, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               (-1 if reverse else 1) * (length - DIMS_SIDE_RIB_WIDTH)))

    @staticmethod
    def _add_rib_sketch(geometries, constraints, tube_index, rib_thickness, bottom_offset,
                        hor_vec_start, hor_vec_end, ver_vec_start, ver_vec_end):
        Console.PrintMessage("_add_rib_sketch({0})\n".format(tube_index))

        segment_count = len(geometries)

        # offset from origin for this rib
        rib_x_offset = (tube_index - 1) * DIMS_STUD_SPACING_INNER + (DIMS_STUD_SPACING_INNER - rib_thickness) / 2

        fillet_radius = rib_thickness / 2

        # Fillet on top of rib
        geometries.append(Part.ArcOfCircle(
            Part.Circle(Vector(rib_x_offset + fillet_radius, (bottom_offset + fillet_radius), 0),
                        Vector(0, 0, 1), fillet_radius), math.pi, 2 * math.pi))

        # Position of rib on brick from origin point (arc first point)
        constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, rib_x_offset))
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, (bottom_offset + fillet_radius)))

        # Arc centre
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, (bottom_offset + fillet_radius)))

        # Arc second point
        constraints.append(Sketcher.Constraint("DistanceX", segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX, rib_thickness))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX, 0))

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 1, SKETCH_GEOMETRY_VERTEX_START_INDEX))

        # Render up until top_inside_datum_plane - already added as a line geometry element to the sketch
        constraints.append(Sketcher.Constraint("PointOnObject", segment_count + 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               SKETCH_GEOMETRY_FIRST_CONSTRUCTION_INDEX))

        geometries.append(Part.LineSegment(hor_vec_end, hor_vec_start))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 2))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 2, SKETCH_GEOMETRY_VERTEX_START_INDEX))

        geometries.append(Part.LineSegment(ver_vec_end, ver_vec_start))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 3))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 3, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 3, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX))

    def _render_body_pad_and_fillets(self):
        Console.PrintMessage("_render_body_pad_and_edge_fillets()\n")

        # body pad

        body_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "body_pad_sketch")

        body_pad_sketch.addGeometry([

            # Rectangle geometry
            Part.LineSegment(xy_plane_top_left_vector(), xy_plane_top_right_vector()),
            Part.LineSegment(xy_plane_top_right_vector(), xy_plane_bottom_right_vector()),
            Part.LineSegment(xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector()),
            Part.LineSegment(xy_plane_bottom_left_vector(), xy_plane_top_left_vector())
        ], False)

        body_pad_sketch.addConstraint([

            # Rectangle constraints
            Sketcher.Constraint("Coincident", 0, SKETCH_GEOMETRY_VERTEX_END_INDEX, 1,
                                SKETCH_GEOMETRY_VERTEX_START_INDEX),
            Sketcher.Constraint("Coincident", 1, SKETCH_GEOMETRY_VERTEX_END_INDEX, 2,
                                SKETCH_GEOMETRY_VERTEX_START_INDEX),
            Sketcher.Constraint("Coincident", 2, SKETCH_GEOMETRY_VERTEX_END_INDEX, 3,
                                SKETCH_GEOMETRY_VERTEX_START_INDEX),
            Sketcher.Constraint("Coincident", 3, SKETCH_GEOMETRY_VERTEX_END_INDEX, 0,
                                SKETCH_GEOMETRY_VERTEX_START_INDEX),
            Sketcher.Constraint("Horizontal", 0),
            Sketcher.Constraint("Horizontal", 2),
            Sketcher.Constraint("Vertical", 1),
            Sketcher.Constraint("Vertical", 3),

            # Half stud offsets from origin
            Sketcher.Constraint("DistanceX", 0, SKETCH_GEOMETRY_VERTEX_START_INDEX, SKETCH_GEOMETRY_ORIGIN_INDEX,
                                SKETCH_GEOMETRY_VERTEX_START_INDEX, DIMS_HALF_STUD_SPACING_OUTER),
            Sketcher.Constraint("DistanceY", 0, SKETCH_GEOMETRY_VERTEX_START_INDEX, SKETCH_GEOMETRY_ORIGIN_INDEX,
                                SKETCH_GEOMETRY_VERTEX_START_INDEX, DIMS_HALF_STUD_SPACING_OUTER),

            # Width
            Sketcher.Constraint("DistanceX", 0, SKETCH_GEOMETRY_VERTEX_START_INDEX, 0, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                (self.width - 1) * DIMS_STUD_SPACING_INNER + (2 * DIMS_HALF_STUD_SPACING_OUTER)),
            # Depth
            Sketcher.Constraint("DistanceY", 1, SKETCH_GEOMETRY_VERTEX_START_INDEX, 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                (self.depth - 1) * DIMS_STUD_SPACING_INNER + (2 * DIMS_HALF_STUD_SPACING_OUTER))
        ])

        body_pad = self.brick.newObject("PartDesign::Pad", "body_pad")
        body_pad.Type = PAD_TYPE_UP_TO_FACE
        body_pad.Profile = body_pad_sketch
        body_pad.UpToFace = (self.top_datum_plane, [""])

        self.doc.recompute()

        # body edge fillets

        edge_names = []
        for i in range(0, len(body_pad.Shape.Edges)):
            edge_names.append("Edge" + repr(i + 1))

        body_edge_fillets = self.brick.newObject("PartDesign::Fillet", "body_edge_fillets")
        body_edge_fillets.Radius = DIMS_EDGE_FILLET
        body_edge_fillets.Base = (body_pad, edge_names)

        self.doc.recompute()
        body_pad_sketch.ViewObject.Visibility = False

        # TODO: support modern tile where the bottom has a small outside pocket (and check if fillet is also required)

    def _render_body_pocket(self):
        Console.PrintMessage("_render_body_pocket()\n")

        # body pocket

        body_pocket_sketch = self.brick.newObject("Sketcher::SketchObject", "body_pocket_sketch")

        side_ribs = self.height > 2 and self.depth > 1 and self.width > 1

        geometries = []
        constraints = []

        if side_ribs:

            # complex rectangle with ribs
            # First horizontal => 1st half stud
            self._add_horizontal_sketch_segment(geometries, constraints,
                                                DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS
                                                - (DIMS_SIDE_RIB_WIDTH / 2),
                                                xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                False)

            # => N-1 studs
            for i in range(0, self.width - 1):
                self._add_horizontal_sketch_segment_with_rib(geometries, constraints,
                                                             DIMS_STUD_SPACING_INNER,
                                                             xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                             xy_plane_top_right_vector(),
                                                             xy_plane_bottom_right_vector(),
                                                             False)

            # => Last half stud
            self._add_horizontal_sketch_segment_with_rib(geometries, constraints,
                                                         DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS
                                                         + (DIMS_SIDE_RIB_WIDTH / 2),
                                                         xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                         xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                         False)

            # First vertical => 1st half stud
            self._add_vertical_sketch_segment(geometries, constraints,
                                              DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS
                                              - (DIMS_SIDE_RIB_WIDTH / 2),
                                              xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                              False)

            # => N-1 studs
            for i in range(0, self.depth - 1):
                self._add_vertical_sketch_segment_with_rib(geometries, constraints,
                                                           DIMS_STUD_SPACING_INNER,
                                                           xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                           xy_plane_bottom_right_vector(),
                                                           xy_plane_bottom_left_vector(),
                                                           False)

            # => Last half stud
            self._add_vertical_sketch_segment_with_rib(geometries, constraints,
                                                       DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS
                                                       + (DIMS_SIDE_RIB_WIDTH / 2),
                                                       xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                       xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector(),
                                                       False)

            # Second horizontal => 1st half stud
            self._add_horizontal_sketch_segment(geometries, constraints,
                                                DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS
                                                - (DIMS_SIDE_RIB_WIDTH / 2),
                                                xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                True)

            # => N-1 studs
            for i in range(0, self.width - 1):
                self._add_horizontal_sketch_segment_with_rib(geometries, constraints,
                                                             DIMS_STUD_SPACING_INNER,
                                                             xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                             xy_plane_top_right_vector(),
                                                             xy_plane_bottom_right_vector(),
                                                             True)

            # => Last half stud
            self._add_horizontal_sketch_segment_with_rib(geometries, constraints,
                                                         DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS
                                                         + (DIMS_SIDE_RIB_WIDTH / 2),
                                                         xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                         xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                         True)

            # Second vertical => 1st half stud
            self._add_vertical_sketch_segment(geometries, constraints,
                                              DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS
                                              - (DIMS_SIDE_RIB_WIDTH / 2),
                                              xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                              True)

            # => N-1 studs
            for i in range(0, self.depth - 1):
                self._add_vertical_sketch_segment_with_rib(geometries, constraints,
                                                           DIMS_STUD_SPACING_INNER,
                                                           xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                           xy_plane_bottom_right_vector(),
                                                           xy_plane_bottom_left_vector(),
                                                           True)

            # => Last half stud
            self._add_vertical_sketch_segment_with_rib(geometries, constraints,
                                                       DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS
                                                       + (DIMS_SIDE_RIB_WIDTH / 2),
                                                       xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                       xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector(),
                                                       True)

            # Half stud offsets from origin (-1, 1 chooses the origin point)
            constraints.append(Sketcher.Constraint("DistanceX", 0, SKETCH_GEOMETRY_VERTEX_START_INDEX, -1,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                   DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS))
            constraints.append(Sketcher.Constraint("DistanceY", 0, SKETCH_GEOMETRY_VERTEX_START_INDEX, -1,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                   DIMS_HALF_STUD_SPACING_OUTER - DIMS_RIBBED_SIDE_THICKNESS))
        else:

            # simple rectangle
            geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_top_right_vector()))
            constraints.append(Sketcher.Constraint("Horizontal", 0))

            geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_bottom_right_vector()))
            constraints.append(Sketcher.Constraint("Vertical", 1))
            constraints.append(Sketcher.Constraint("Coincident", 0, SKETCH_GEOMETRY_VERTEX_END_INDEX, 1,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX))

            geometries.append(Part.LineSegment(xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector()))
            constraints.append(Sketcher.Constraint("Horizontal", 2))
            constraints.append(Sketcher.Constraint("Coincident", 1, SKETCH_GEOMETRY_VERTEX_END_INDEX, 2,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX))

            geometries.append(Part.LineSegment(xy_plane_bottom_left_vector(), xy_plane_top_left_vector()))
            constraints.append(Sketcher.Constraint("Vertical", 3))
            constraints.append(Sketcher.Constraint("Coincident", 2, SKETCH_GEOMETRY_VERTEX_END_INDEX, 3,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX))

            # Complete the rectangle
            constraints.append(Sketcher.Constraint("Coincident", 3, SKETCH_GEOMETRY_VERTEX_END_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX))

            # Width
            constraints.append(Sketcher.Constraint("DistanceX", 0, SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                                   (self.width - 1) * DIMS_STUD_SPACING_INNER
                                                   + (2 * DIMS_HALF_STUD_SPACING_OUTER)
                                                   - (2 * DIMS_FLAT_SIDE_THICKNESS)))
            # Depth
            constraints.append(Sketcher.Constraint("DistanceY", 1, SKETCH_GEOMETRY_VERTEX_START_INDEX, 1,
                                                   SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                                   (self.depth - 1) * DIMS_STUD_SPACING_INNER
                                                   + (2 * DIMS_HALF_STUD_SPACING_OUTER)
                                                   - (2 * DIMS_FLAT_SIDE_THICKNESS)))

            # Half stud offsets from origin
            constraints.append(Sketcher.Constraint("DistanceX", 0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                   SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                   DIMS_HALF_STUD_SPACING_OUTER - DIMS_FLAT_SIDE_THICKNESS))
            constraints.append(Sketcher.Constraint("DistanceY", 0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                   SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                   DIMS_HALF_STUD_SPACING_OUTER - DIMS_FLAT_SIDE_THICKNESS))

        body_pocket_sketch.addGeometry(geometries, False)
        body_pocket_sketch.addConstraint(constraints)

        body_pocket = self.brick.newObject("PartDesign::Pocket", "body_pocket")
        body_pocket.Type = POCKET_TYPE_UP_TO_FACE
        body_pocket.Profile = body_pocket_sketch
        body_pocket.UpToFace = (self.top_inside_datum_plane, [""])
        body_pocket.Reversed = True

        self.doc.recompute()
        body_pocket_sketch.ViewObject.Visibility = False

    def _render_tube_ribs(self):
        Console.PrintMessage("_render_tube_ribs()\n")

        # TODO: determine a replacement for tube ribs if technic holes exist

        if self.width > 2:

            # front tube rubs pad

            front_tube_ribs_sketch = self.brick.newObject("Sketcher::SketchObject", "front_tube_ribs_sketch")
            front_tube_ribs_sketch.Support = (self.front_inside_datum_plane, '')
            front_tube_ribs_sketch.MapMode = 'FlatFace'

            # add top_inside_datum_plane to sketch as an edge so that it can be referenced
            # this will add a line geometry element to the sketch as item 0
            front_tube_ribs_sketch.addExternal(self.top_inside_datum_plane.Label, '')

            geometries = []
            constraints = []

            # choose correct tubes to render ribs on
            indices = []
            if self.width % 2 == 0:
                for i in range(2, self.width, 2):
                    indices.append(i)
            else:
                for i in range(((self.width - 1) // 2), 0, -2):
                    indices.append(i)
                for i in range(((self.width - 1) // 2) + 1, self.width, 2):
                    indices.append(i)
            for i in indices:
                self._add_rib_sketch(geometries, constraints, i,
                                     DIMS_TUBE_RIB_THICKNESS, DIMS_TUBE_RIB_BOTTOM_OFFSET,
                                     xz_plane_bottom_left_vector(), xz_plane_bottom_right_vector(),
                                     xz_plane_bottom_right_vector(), xz_plane_top_right_vector())

            front_tube_ribs_sketch.addGeometry(geometries, False)
            front_tube_ribs_sketch.addConstraint(constraints)

            front_tube_ribs_pad = self.brick.newObject("PartDesign::Pad", "front_tube_ribs_pad")
            front_tube_ribs_pad.Type = PAD_TYPE_UP_TO_FACE
            front_tube_ribs_pad.UpToFace = (self.back_inside_datum_plane, [""])
            front_tube_ribs_pad.Profile = front_tube_ribs_sketch
            front_tube_ribs_pad.Reversed = 1

            self.doc.recompute()
            front_tube_ribs_sketch.ViewObject.Visibility = False

        if self.depth > 2:

            # side tube rubs pad

            side_tube_ribs_sketch = self.brick.newObject("Sketcher::SketchObject", "side_tube_ribs_sketch")
            side_tube_ribs_sketch.Support = (self.left_inside_datum_plane, '')
            side_tube_ribs_sketch.MapMode = 'FlatFace'

            # add top_inside_datum_plane to sketch as an edge so that it can be referenced
            # this will add a line geometry element to the sketch as item 0
            side_tube_ribs_sketch.addExternal(self.top_inside_datum_plane.Label, '')

            geometries = []
            constraints = []

            # choose correct tubes to render ribs on
            indices = []
            if self.depth % 2 == 0:
                for i in range(2, self.depth, 2):
                    indices.append(i)
            else:
                for i in range(((self.depth - 1) // 2), 0, -2):
                    indices.append(i)
                for i in range(((self.depth - 1) // 2) + 1, self.depth, 2):
                    indices.append(i)
            for i in indices:
                self._add_rib_sketch(geometries, constraints, i,
                                     DIMS_TUBE_RIB_THICKNESS, DIMS_TUBE_RIB_BOTTOM_OFFSET,
                                     yz_plane_bottom_left_vector(), yz_plane_bottom_right_vector(),
                                     yz_plane_bottom_right_vector(), yz_plane_top_right_vector())

            side_tube_ribs_sketch.addGeometry(geometries, False)
            side_tube_ribs_sketch.addConstraint(constraints)

            side_tube_ribs_pad = self.brick.newObject("PartDesign::Pad", "side_tube_ribs_pad")
            side_tube_ribs_pad.Type = PAD_TYPE_UP_TO_FACE
            side_tube_ribs_pad.UpToFace = (self.right_inside_datum_plane, [""])
            side_tube_ribs_pad.Profile = side_tube_ribs_sketch

            self.doc.recompute()
            side_tube_ribs_sketch.ViewObject.Visibility = False

    def _render_tubes(self):
        Console.PrintMessage("_render_tubes()\n")

        # tubes pad

        tubes_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "tubes_pad_sketch")
        tubes_pad_sketch.MapMode = 'ObjectXY'
        tubes_pad_sketch.Placement = Placement(Vector(0, 0, DIMS_STICK_AND_TUBE_BOTTOM_INSET),
                                               Rotation(Vector(0, 0, 1), 0))

        add_inner_circle_with_flats_to_sketch(tubes_pad_sketch, DIMS_TUBE_OUTER_RADIUS,
                                              DIMS_TUBE_INNER_RADIUS, DIMS_STUD_FLAT_THICKNESS, False,
                                              0.5 * DIMS_STUD_SPACING_INNER,
                                              0.5 * DIMS_STUD_SPACING_INNER)

        # create array if needed
        if self.width > 2 or self.depth > 2:
            geometry_indices = [range(0, len(tubes_pad_sketch.Geometry) - 1)]
            if self.width == 2 and self.depth > 2:
                tubes_pad_sketch.addRectangularArray(geometry_indices, Vector(0, DIMS_STUD_SPACING_INNER, 0), False,
                                                     self.depth - 1, self.width - 1, True)
            elif self.width > 2 and self.depth == 2:
                tubes_pad_sketch.addRectangularArray(geometry_indices, Vector(DIMS_STUD_SPACING_INNER, 0, 0), False,
                                                     self.width - 1, self.depth - 1, True)
            else:
                tubes_pad_sketch.addRectangularArray(geometry_indices, Vector(0, DIMS_STUD_SPACING_INNER, 0), False,
                                                     self.depth - 1, self.width - 1, True)

        tubes_pad = self.brick.newObject("PartDesign::Pad", "tubes_pad")
        tubes_pad.Type = PAD_TYPE_UP_TO_FACE
        tubes_pad.UpToFace = (self.top_inside_datum_plane, [""])
        tubes_pad.Profile = tubes_pad_sketch

        self.doc.recompute()
        tubes_pad_sketch.ViewObject.Visibility = False

    def _render_stick_ribs(self):
        Console.PrintMessage("_render_stick_ribs()\n")

        # stick ribs pad

        stick_ribs_sketch = self.brick.newObject("Sketcher::SketchObject", "stick_ribs_sketch")
        if self.width > 1:
            stick_ribs_sketch.Support = (self.front_inside_datum_plane, '')
        else:
            stick_ribs_sketch.Support = (self.left_inside_datum_plane, '')
        stick_ribs_sketch.MapMode = 'FlatFace'

        # add top_inside_datum_plane to sketch as an edge so that it can be referenced
        # this will add a line geometry element to the sketch as item 0
        stick_ribs_sketch.addExternal(self.top_inside_datum_plane.Label, '')

        geometries = []
        constraints = []

        # choose correct sticks to render ribs on
        indices = []
        if self.width > 1:
            studs = self.width
        else:
            studs = self.depth

        # for stud count between from 2 to 4 each stick has rib
        if studs < 5:
            for i in range(1, studs):
                indices.append(i)
        # otherwise every second
        else:
            if studs % 2 == 0:
                for i in range(2, studs, 2):
                    indices.append(i)
            else:
                for i in range(((studs - 1) // 2), 0, -2):
                    indices.append(i)
                for i in range(((studs - 1) // 2) + 1, studs, 2):
                    indices.append(i)

        for i in indices:
            self._add_rib_sketch(geometries, constraints, i,
                                 DIMS_STICK_RIB_THICKNESS, DIMS_STICK_RIB_BOTTOM_OFFSET,
                                 xz_plane_bottom_left_vector(), xz_plane_bottom_right_vector(),
                                 xz_plane_bottom_right_vector(), xz_plane_top_right_vector())

        stick_ribs_sketch.addGeometry(geometries, False)
        stick_ribs_sketch.addConstraint(constraints)

        stick_ribs_pad = self.brick.newObject("PartDesign::Pad", "stick_ribs_pad")
        stick_ribs_pad.Type = PAD_TYPE_UP_TO_FACE
        if self.width > 1:
            stick_ribs_pad.UpToFace = (self.back_inside_datum_plane, [""])
        else:
            stick_ribs_pad.UpToFace = (self.right_inside_datum_plane, [""])
        stick_ribs_pad.Profile = stick_ribs_sketch
        if self.width > 1:
            stick_ribs_pad.Reversed = 1

        self.doc.recompute()
        stick_ribs_sketch.ViewObject.Visibility = False

    def _render_sticks(self):
        Console.PrintMessage("_render_sticks()\n")

        # sticks pad

        sticks_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "sticks_pad_sketch")
        sticks_pad_sketch.MapMode = 'ObjectXY'
        sticks_pad_sketch.Placement = Placement(Vector(0, 0, DIMS_STICK_AND_TUBE_BOTTOM_INSET),
                                                Rotation(Vector(0, 0, 1), 0))

        geometries = []
        constraints = []

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", 0, DIMS_STICK_OUTER_RADIUS))

        # Half stud offsets from origin
        if self.width > 1:
            constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0.5 * DIMS_STUD_SPACING_INNER))
            constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0))
        else:
            constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0))
            constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0.5 * DIMS_STUD_SPACING_INNER))

        sticks_pad_sketch.addGeometry(geometries, False)
        sticks_pad_sketch.addConstraint(constraints)

        if self.width > 1:
            sticks_pad_sketch.addRectangularArray([0], Vector(DIMS_STUD_SPACING_INNER, 0, 0), False,
                                                  self.width - 1, 1, True)
        else:
            sticks_pad_sketch.addRectangularArray([0], Vector(0, DIMS_STUD_SPACING_INNER, 0), False,
                                                  self.depth - 1, 1, True)

        sticks_pad = self.brick.newObject("PartDesign::Pad", "sticks_pad")
        sticks_pad.Type = PAD_TYPE_UP_TO_FACE
        sticks_pad.UpToFace = (self.top_inside_datum_plane, [""])
        sticks_pad.Profile = sticks_pad_sketch

        self.doc.recompute()
        sticks_pad_sketch.ViewObject.Visibility = False

        # sticks pocket

        sticks_pocket_sketch = self.brick.newObject("Sketcher::SketchObject", "sticks_pocket_sketch")
        sticks_pocket_sketch.Support = (self.top_inside_datum_plane, '')
        sticks_pocket_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", 0, DIMS_STICK_INNER_RADIUS))

        # Half stud offsets from origin
        if self.width > 1:
            constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                                   0.5 * DIMS_STUD_SPACING_INNER))
            constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0))
        else:
            constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, 0))
            constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, 0,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                                   0.5 * DIMS_STUD_SPACING_INNER))

        sticks_pocket_sketch.addGeometry(geometries, False)
        sticks_pocket_sketch.addConstraint(constraints)

        if self.width > 1:
            sticks_pocket_sketch.addRectangularArray([0], Vector(DIMS_STUD_SPACING_INNER, 0, 0), False,
                                                     self.width - 1, 1, True)
        if self.depth > 1:
            sticks_pocket_sketch.addRectangularArray([0], Vector(0, DIMS_STUD_SPACING_INNER, 0), False,
                                                     self.depth - 1, 1, True)

        sticks_pocket = self.brick.newObject("PartDesign::Pocket", "sticks_pocket")
        sticks_pocket.Type = POCKET_TYPE_THROUGH_ALL
        sticks_pocket.Profile = sticks_pocket_sketch

        self.doc.recompute()
        sticks_pocket_sketch.ViewObject.Visibility = False

    def _render_tubes_or_sticks(self):
        Console.PrintMessage("_render_tubes_or_sticks()\n")

        tubes = self.depth > 1 and self.width > 1
        tube_ribs = tubes and self.height > 1 and (self.depth > 2 or self.width > 2)
        sticks = not tubes and (self.depth > 1 or self.width > 1)
        stick_ribs = sticks and self.height > 1 and not self.hole_style == HoleStyle.HOLE

        if tube_ribs:
            self._render_tube_ribs()

        if tubes:
            self._render_tubes()

        if stick_ribs:
            self._render_stick_ribs()

        if sticks:
            self._render_sticks()

    def render(self, context):
        Console.PrintMessage("render\n")

        self.width = context.width
        self.depth = context.depth
        self.height = context.height

        self.hole_style = context.hole_style
        self.holes_offset = context.holes_offset

        self.doc = context.doc
        self.brick = context.brick

        self.top_datum_plane = context.top_datum_plane
        self.top_inside_datum_plane = context.top_inside_datum_plane
        self.front_inside_datum_plane = context.front_inside_datum_plane
        self.back_inside_datum_plane = context.back_inside_datum_plane
        self.left_inside_datum_plane = context.left_inside_datum_plane
        self.right_inside_datum_plane = context.right_inside_datum_plane

        self._render_body_pad_and_fillets()

        # TODO: support side rib variation for modern 2x1 tile and technic bricks with non-offset holes
        # TODO: 0.25 fillet on inner corners
        self._render_body_pocket()

        # TODO: determine a replacement for internal ribs if side studs exist with holes
        self._render_tubes_or_sticks()
