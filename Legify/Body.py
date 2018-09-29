# coding: UTF-8

from FreeCAD import Console
import Part
import Sketcher
from Legify.Common import *


class BodyRenderer(object):

    def __init__(self, brick_width, brick_depth, brick_height, hole_style, holes_offset):
        Console.PrintMessage("BodyRenderer\n")

        self.brick_width = brick_width
        self.brick_depth = brick_depth
        self.brick_height = brick_height

        self.hole_style = hole_style
        self.holes_offset = holes_offset

        self.doc = FreeCAD.activeDocument()
        self.brick = self.doc.brick

    @staticmethod
    def _add_horizontal_sketch_segment(geometries, constraints, length, hor_vec_start, hor_vec_end, reverse):
        Console.PrintMessage("_add_horizontal_sketch_segment({0},{1})\n".format(length, reverse))

        segment_count = len(geometries)

        geometries.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count))
        if segment_count > 0:
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, 2, segment_count, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count, 1, segment_count, 2,
                                               (-1 if reverse else 1) * length))

    @staticmethod
    def _add_vertical_sketch_segment(geometries, constraints, length, ver_vec_start, ver_vec_end, reverse):
        Console.PrintMessage("_add_vertical_sketch_segment({0},{1})\n".format(length, reverse))

        segment_count = len(geometries)

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count))
        if segment_count > 0:
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, 2, segment_count, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count, 1, segment_count, 2,
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
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, 2, segment_count, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count, 1, segment_count, 2,
                                               (-1 if reverse else 1) * DIMS_SIDE_RIB_DEPTH))

        geometries.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count, 2, segment_count + 1, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 1, 1, segment_count + 1, 2,
                                               (-1 if reverse else 1) * DIMS_SIDE_RIB_WIDTH))

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 2))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 1, 2, segment_count + 2, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 2, 1, segment_count + 2, 2,
                                               (1 if reverse else -1) * DIMS_SIDE_RIB_DEPTH))

        geometries.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 3))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 2, 2, segment_count + 3, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 3, 1, segment_count + 3, 2,
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
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, 2, segment_count, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count, 1, segment_count, 2,
                                               (1 if reverse else -1) * DIMS_SIDE_RIB_DEPTH))

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count, 2, segment_count + 1, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 1, 1, segment_count + 1, 2,
                                               (-1 if reverse else 1) * DIMS_SIDE_RIB_WIDTH))

        geometries.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 2))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 1, 2, segment_count + 2, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 2, 1, segment_count + 2, 2,
                                               (-1 if reverse else 1) * DIMS_SIDE_RIB_DEPTH))

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 3))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 2, 2, segment_count + 3, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 3, 1, segment_count + 3, 2,
                                               (-1 if reverse else 1) * (length - DIMS_SIDE_RIB_WIDTH)))

    @staticmethod
    def _add_rib_sketch(geometries, constraints, tube_index, rib_thickness, bottom_offset,
                        hor_vec_start, hor_vec_end, ver_vec_start, ver_vec_end):
        Console.PrintMessage("_add_rib_sketch({0})\n".format(tube_index))

        segment_count = len(geometries)

        # offset from origin for this rib
        rib_x_offset = (tube_index - 1) * DIMS_STUD_WIDTH_INNER + (DIMS_STUD_WIDTH_INNER - rib_thickness) / 2

        fillet_radius = rib_thickness / 2

        # Fillet on top of rib
        geometries.append(Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(rib_x_offset + fillet_radius,
                                       (bottom_offset + fillet_radius), 0),
                        FreeCAD.Vector(0, 0, 1), fillet_radius), math.pi, 2 * math.pi))

        # Position of rib on brick from origin point (arc first point)
        # Half stud offsets from origin (-1, 1 chooses the origin point)
        constraints.append(Sketcher.Constraint("DistanceX", -1, 1, segment_count, 1, rib_x_offset))
        constraints.append(Sketcher.Constraint("DistanceY", -1, 1, segment_count, 1, (bottom_offset + fillet_radius)))

        # Arc centre
        # Half stud offsets from origin (-1, 1 chooses the origin point)
        constraints.append(Sketcher.Constraint("DistanceY", -1, 1, segment_count, 3, (bottom_offset + fillet_radius)))

        # Arc second point
        constraints.append(Sketcher.Constraint("DistanceX", segment_count, 1, segment_count, 2, rib_thickness))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count, 1, segment_count, 2, 0))

        geometries.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count, 2, segment_count + 1, 1))

        # Render up until top_inside_datum_plane - already added as a line geometry element to the sketch
        # This external geometry is indexed from -3 descending! https://forum.freecadweb.org/viewtopic.php?t=24211
        constraints.append(Sketcher.Constraint("PointOnObject", segment_count + 1, 2, -3))

        geometries.append(Part.LineSegment(hor_vec_end, hor_vec_start))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 2))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 1, 2, segment_count + 2, 1))

        geometries.append(Part.LineSegment(ver_vec_end, ver_vec_start))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 3))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 2, 2, segment_count + 3, 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 3, 2, segment_count, 1))

    @staticmethod
    def _add_tube_circle_sketch(geometries, constraints):
        Console.PrintMessage("_add_tube_circle_sketch()\n")

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", 0, DIMS_TUBE_OUTER_RADIUS))
        # -1, 1 chooses the origin point
        constraints.append(Sketcher.Constraint("DistanceX", -1, 1, 0, 3, 0.5 * DIMS_STUD_WIDTH_INNER))
        # -1, 1 chooses the origin point
        constraints.append(Sketcher.Constraint("DistanceY", -1, 1, 0, 3, 0.5 * DIMS_STUD_WIDTH_INNER))

    def _render_body_pad_and_fillets(self):
        Console.PrintMessage("_render_body_pad_and_edge_fillets()\n")

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
            Sketcher.Constraint("Coincident", 0, 2, 1, 1),
            Sketcher.Constraint("Coincident", 1, 2, 2, 1),
            Sketcher.Constraint("Coincident", 2, 2, 3, 1),
            Sketcher.Constraint("Coincident", 3, 2, 0, 1),
            Sketcher.Constraint("Horizontal", 0),
            Sketcher.Constraint("Horizontal", 2),
            Sketcher.Constraint("Vertical", 1),
            Sketcher.Constraint("Vertical", 3),

            # Half stud offsets from origin (-1, 1 chooses the origin point)
            Sketcher.Constraint("DistanceX", 0, 1, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER),
            Sketcher.Constraint("DistanceY", 0, 1, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER),

            # Width
            Sketcher.Constraint("DistanceX", 0, 1, 0, 2, (self.brick_width - 1) * DIMS_STUD_WIDTH_INNER
                                + (2 * DIMS_HALF_STUD_WIDTH_OUTER)),
            # Depth
            Sketcher.Constraint("DistanceY", 1, 1, 1, 2, (self.brick_depth - 1) * DIMS_STUD_WIDTH_INNER
                                + (2 * DIMS_HALF_STUD_WIDTH_OUTER))
        ])

        # perform the pad
        body_pad = self.brick.newObject("PartDesign::Pad", "body_pad")
        body_pad.Profile = body_pad_sketch

        # Need to specify Dimension instead of UpToFace because of the following issue:
        # https://freecadweb.org/tracker/view.php?id=3177
        # https://forum.freecadweb.org/viewtopic.php?f=8&t=24238
        # body_pad.Type = 3
        # body_pad.UpToFace = (self.doc.top_datum_plane, [""])
        body_pad.Length = self.brick_height * DIMS_PLATE_HEIGHT

        body_pad_sketch.ViewObject.Visibility = False
        self.doc.recompute()

        # edge fillets
        edge_names = []
        for i in range(0, len(body_pad.Shape.Edges)):
            edge_names.append("Edge" + repr(i + 1))

        body_edge_fillets = self.brick.newObject("PartDesign::Fillet", "body_edge_fillets")
        body_edge_fillets.Radius = DIMS_EDGE_FILLET
        body_edge_fillets.Base = (body_pad, edge_names)

        self.doc.recompute()

        # TODO: support modern tile with bottom outside pocket (is fillet also required?)

    def _render_body_pocket(self):
        Console.PrintMessage("_render_body_pocket()\n")

        body_pocket_sketch = self.brick.newObject("Sketcher::SketchObject", "body_pocket_sketch")

        # TODO: support modern 2x1 tile and dual technic hole brick with rib variation and no tube/stick
        ribs = self.brick_height == 3 and self.brick_depth > 1 and self.brick_width > 1

        geometries = []
        constraints = []

        if ribs:

            # complex rectangle with ribs
            # First horizontal => 1st half stud
            self._add_horizontal_sketch_segment(geometries, constraints,
                                                DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS
                                                - (DIMS_SIDE_RIB_WIDTH / 2),
                                                xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                False)

            # => N-1 studs
            for i in range(0, self.brick_width - 1):
                self._add_horizontal_sketch_segment_with_rib(geometries, constraints,
                                                             DIMS_STUD_WIDTH_INNER,
                                                             xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                             xy_plane_top_right_vector(),
                                                             xy_plane_bottom_right_vector(),
                                                             False)

            # => Last half stud
            self._add_horizontal_sketch_segment_with_rib(geometries, constraints,
                                                         DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS
                                                         + (DIMS_SIDE_RIB_WIDTH / 2),
                                                         xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                         xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                         False)

            # First vertical => 1st half stud
            self._add_vertical_sketch_segment(geometries, constraints,
                                              DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS
                                              - (DIMS_SIDE_RIB_WIDTH / 2),
                                              xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                              False)

            # => N-1 studs
            for i in range(0, self.brick_depth - 1):
                self._add_vertical_sketch_segment_with_rib(geometries, constraints,
                                                           DIMS_STUD_WIDTH_INNER,
                                                           xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                           xy_plane_bottom_right_vector(),
                                                           xy_plane_bottom_left_vector(),
                                                           False)

            # => Last half stud
            self._add_vertical_sketch_segment_with_rib(geometries, constraints,
                                                       DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS
                                                       + (DIMS_SIDE_RIB_WIDTH / 2),
                                                       xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                       xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector(),
                                                       False)

            # Second horizontal => 1st half stud
            self._add_horizontal_sketch_segment(geometries, constraints,
                                                DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS
                                                - (DIMS_SIDE_RIB_WIDTH / 2),
                                                xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                True)

            # => N-1 studs
            for i in range(0, self.brick_width - 1):
                self._add_horizontal_sketch_segment_with_rib(geometries, constraints,
                                                             DIMS_STUD_WIDTH_INNER,
                                                             xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                             xy_plane_top_right_vector(),
                                                             xy_plane_bottom_right_vector(),
                                                             True)

            # => Last half stud
            self._add_horizontal_sketch_segment_with_rib(geometries, constraints,
                                                         DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS
                                                         + (DIMS_SIDE_RIB_WIDTH / 2),
                                                         xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                         xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                         True)

            # Second vertical => 1st half stud
            self._add_vertical_sketch_segment(geometries, constraints,
                                              DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS
                                              - (DIMS_SIDE_RIB_WIDTH / 2),
                                              xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                              True)

            # => N-1 studs
            for i in range(0, self.brick_depth - 1):
                self._add_vertical_sketch_segment_with_rib(geometries, constraints,
                                                           DIMS_STUD_WIDTH_INNER,
                                                           xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                           xy_plane_bottom_right_vector(),
                                                           xy_plane_bottom_left_vector(),
                                                           True)

            # => Last half stud
            self._add_vertical_sketch_segment_with_rib(geometries, constraints,
                                                       DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS
                                                       + (DIMS_SIDE_RIB_WIDTH / 2),
                                                       xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                       xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector(),
                                                       True)

            # Half stud offsets from origin (-1, 1 chooses the origin point)
            constraints.append(Sketcher.Constraint("DistanceX", 0, 1, -1, 1,
                                                   DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS))
            constraints.append(Sketcher.Constraint("DistanceY", 0, 1, -1, 1,
                                                   DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS))
        else:

            # simple rectangle
            geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_top_right_vector()))
            constraints.append(Sketcher.Constraint("Horizontal", 0))

            geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_bottom_right_vector()))
            constraints.append(Sketcher.Constraint("Vertical", 1))
            constraints.append(Sketcher.Constraint("Coincident", 0, 2, 1, 1))

            geometries.append(Part.LineSegment(xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector()))
            constraints.append(Sketcher.Constraint("Horizontal", 2))
            constraints.append(Sketcher.Constraint("Coincident", 1, 2, 2, 1))

            geometries.append(Part.LineSegment(xy_plane_bottom_left_vector(), xy_plane_top_left_vector()))
            constraints.append(Sketcher.Constraint("Vertical", 3))
            constraints.append(Sketcher.Constraint("Coincident", 2, 2, 3, 1))

            # Complete the rectangle
            constraints.append(Sketcher.Constraint("Coincident", 3, 2, 0, 1))

            # Width
            constraints.append(Sketcher.Constraint("DistanceX", 0, 1, 0, 2,
                                                   (self.brick_width - 1) * DIMS_STUD_WIDTH_INNER
                                                   + (2 * DIMS_HALF_STUD_WIDTH_OUTER)
                                                   - (2 * DIMS_SIDE_THICKNESS)))
            # Depth
            constraints.append(Sketcher.Constraint("DistanceY", 1, 1, 1, 2,
                                                   (self.brick_depth - 1) * DIMS_STUD_WIDTH_INNER
                                                   + (2 * DIMS_HALF_STUD_WIDTH_OUTER)
                                                   - (2 * DIMS_SIDE_THICKNESS)))

            # Half stud offsets from origin (-1, 1 chooses the origin point)
            constraints.append(Sketcher.Constraint("DistanceX", 0, 1, -1, 1,
                                                   DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS))
            constraints.append(Sketcher.Constraint("DistanceY", 0, 1, -1, 1,
                                                   DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS))

        body_pocket_sketch.addGeometry(geometries, False)
        body_pocket_sketch.addConstraint(constraints)

        # perform the pocket
        body_pocket = self.brick.newObject("PartDesign::Pocket", "body_pocket")
        body_pocket.Profile = body_pocket_sketch
        body_pocket.Type = 3
        body_pocket.UpToFace = (self.doc.top_inside_datum_plane, [""])
        body_pocket.Reversed = True

        body_pocket_sketch.ViewObject.Visibility = False
        self.doc.recompute()

    def _render_tube_ribs(self):
        Console.PrintMessage("_render_tube_ribs()\n")

        if self.brick_width > 2:
            front_tube_ribs_sketch = self.brick.newObject("Sketcher::SketchObject", "front_tube_ribs_sketch")
            front_tube_ribs_sketch.Support = (self.doc.front_inside_datum_plane, '')
            front_tube_ribs_sketch.MapMode = 'FlatFace'

            # add top_inside_datum_plane to sketch as an edge so that it can be referenced
            # this will add a line geometry element to the sketch as item 0
            front_tube_ribs_sketch.addExternal(self.doc.top_inside_datum_plane.Label, '')

            geometries = []
            constraints = []

            # choose correct tubes to render ribs on
            indices = []
            if self.brick_width % 2 == 0:
                for i in range(2, self.brick_width, 2):
                    indices.append(i)
            else:
                for i in range(((self.brick_width - 1) / 2), 0, -2):
                    indices.append(i)
                for i in range(((self.brick_width - 1) / 2) + 1, self.brick_width, 2):
                    indices.append(i)
            for i in indices:
                self._add_rib_sketch(geometries, constraints, i,
                                     DIMS_TUBE_RIB_THICKNESS, DIMS_TUBE_RIB_BOTTOM_OFFSET,
                                     xz_plane_bottom_left_vector(), xz_plane_bottom_right_vector(),
                                     xz_plane_bottom_right_vector(), xz_plane_top_right_vector())

            front_tube_ribs_sketch.addGeometry(geometries, False)
            front_tube_ribs_sketch.addConstraint(constraints)
            self.doc.recompute()

            # perform the pad
            front_tube_ribs_pad = self.brick.newObject("PartDesign::Pad", "front_tube_ribs_pad")
            front_tube_ribs_pad.Profile = front_tube_ribs_sketch
            front_tube_ribs_pad.Reversed = 1
            # Need to specify Dimension instead of UpToFace because of the following issue:
            # https://freecadweb.org/tracker/view.php?id=3177
            # https://forum.freecadweb.org/viewtopic.php?f=8&t=24238
            front_tube_ribs_pad.Length = (self.brick_depth - 1) * DIMS_STUD_WIDTH_INNER + \
                                         (2 * DIMS_HALF_STUD_WIDTH_OUTER) - (2 * DIMS_SIDE_THICKNESS)

            front_tube_ribs_sketch.ViewObject.Visibility = False

        if self.brick_depth > 2:
            side_tube_ribs_sketch = self.brick.newObject("Sketcher::SketchObject", "side_tube_ribs_sketch")
            side_tube_ribs_sketch.Support = (self.doc.side_inside_datum_plane, '')
            side_tube_ribs_sketch.MapMode = 'FlatFace'

            # add top_inside_datum_plane to sketch as an edge so that it can be referenced
            # this will add a line geometry element to the sketch as item 0
            side_tube_ribs_sketch.addExternal(self.doc.top_inside_datum_plane.Label, '')

            geometries = []
            constraints = []

            # choose correct tubes to render ribs on
            indices = []
            if self.brick_depth % 2 == 0:
                for i in range(2, self.brick_depth, 2):
                    indices.append(i)
            else:
                for i in range(((self.brick_depth - 1) / 2), 0, -2):
                        indices.append(i)
                for i in range(((self.brick_depth - 1) / 2) + 1, self.brick_depth, 2):
                    indices.append(i)
            for i in indices:
                self._add_rib_sketch(geometries, constraints, i,
                                     DIMS_TUBE_RIB_THICKNESS, DIMS_TUBE_RIB_BOTTOM_OFFSET,
                                     yz_plane_bottom_left_vector(), yz_plane_bottom_right_vector(),
                                     yz_plane_bottom_right_vector(), yz_plane_top_right_vector())

            side_tube_ribs_sketch.addGeometry(geometries, False)
            side_tube_ribs_sketch.addConstraint(constraints)
            self.doc.recompute()

            # perform the pad
            side_tube_ribs_pad = self.brick.newObject("PartDesign::Pad", "side_tube_ribs_pad")
            side_tube_ribs_pad.Profile = side_tube_ribs_sketch
            # Need to specify Dimension instead of UpToFace because of the following issue:
            # https://freecadweb.org/tracker/view.php?id=3177
            # https://forum.freecadweb.org/viewtopic.php?f=8&t=24238
            side_tube_ribs_pad.Length = (self.brick_width - 1) * DIMS_STUD_WIDTH_INNER + \
                                        (2 * DIMS_HALF_STUD_WIDTH_OUTER) - (2 * DIMS_SIDE_THICKNESS)

            side_tube_ribs_sketch.ViewObject.Visibility = False

        self.doc.recompute()

    def _render_tubes(self):
        Console.PrintMessage("_render_tubes()\n")

        # tubes pad

        tubes_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "tubes_pad_sketch")
        tubes_pad_sketch.Support = (self.doc.top_inside_datum_plane, '')
        tubes_pad_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        # Outer circle
        self._add_tube_circle_sketch(geometries, constraints)

        tubes_pad_sketch.addGeometry(geometries, False)
        tubes_pad_sketch.addConstraint(constraints)
        self.doc.recompute()

        # create array if needed
        if self.brick_width > 2 or self.brick_depth > 2:
            geometries = [0]
            if self.brick_width == 2 and self.brick_depth > 2:
                tubes_pad_sketch.addRectangularArray(geometries, FreeCAD.Vector(0, DIMS_STUD_WIDTH_INNER, 0), False,
                                                     self.brick_depth - 1, self.brick_width - 1, True)
            elif self.brick_width > 2 and self.brick_depth == 2:
                tubes_pad_sketch.addRectangularArray(geometries, FreeCAD.Vector(DIMS_STUD_WIDTH_INNER, 0, 0), False,
                                                     self.brick_width - 1, self.brick_depth - 1, True)
            else:
                tubes_pad_sketch.addRectangularArray(geometries, FreeCAD.Vector(0, DIMS_STUD_WIDTH_INNER, 0), False,
                                                     self.brick_depth - 1, self.brick_width - 1, True)

        # perform the pad
        tubes_pad = self.brick.newObject("PartDesign::Pad", "tubes_pad")
        tubes_pad.Profile = tubes_pad_sketch
        tubes_pad.Reversed = 1

        # Need to specify Dimension instead of UpToFace because of the following issue:
        # https://freecadweb.org/tracker/view.php?id=3177
        # https://forum.freecadweb.org/viewtopic.php?f=8&t=24238
        # tubes_pad.Type = 3
        # tubes_pad.UpToFace = (self.doc.XY_Plane, [""])
        # tubes_pad.Offset = -1 * DIMS_STICK_AND_TUBE_BOTTOM_OFFSET
        tubes_pad.Length = ((self.brick_height * DIMS_PLATE_HEIGHT)
                            - DIMS_TOP_THICKNESS - DIMS_STICK_AND_TUBE_BOTTOM_OFFSET)

        tubes_pad_sketch.ViewObject.Visibility = False
        self.doc.recompute()

        # tubes pocket

        tubes_pocket_sketch = self.brick.newObject("Sketcher::SketchObject", "tubes_pocket_sketch")
        tubes_pocket_sketch.Support = (self.doc.top_inside_datum_plane, '')
        tubes_pocket_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        # Outer circle for construction
        self._add_tube_circle_sketch(geometries, constraints)

        # Tangent construction line
        geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_bottom_right_vector()))
        constraints.append(Sketcher.Constraint('Angle', 1, -45 * math.pi / 180))
        constraints.append(Sketcher.Constraint('Tangent', 1, 0))
        constraints.append(Sketcher.Constraint('PointOnObject', 1, 2, 0))
        # -1, 1 chooses the origin point
        constraints.append(Sketcher.Constraint("DistanceX", 1, 1, 1, 2, 1))

        # Four Line Segments
        x1 = (DIMS_STUD_WIDTH_INNER / 2) - 2
        x2 = (DIMS_STUD_WIDTH_INNER / 2) - 1
        x3 = (DIMS_STUD_WIDTH_INNER / 2) + 1
        x4 = (DIMS_STUD_WIDTH_INNER / 2) + 2
        y1 = (DIMS_STUD_WIDTH_INNER / 2) - 2
        y2 = (DIMS_STUD_WIDTH_INNER / 2) - 1
        y3 = (DIMS_STUD_WIDTH_INNER / 2) + 1
        y4 = (DIMS_STUD_WIDTH_INNER / 2) + 2

        geometries.append(Part.LineSegment(FreeCAD.Vector(x2, y1, 0), FreeCAD.Vector(x1, y2, 0)))
        geometries.append(Part.LineSegment(FreeCAD.Vector(x1, y3, 0), FreeCAD.Vector(x2, y4, 0)))
        geometries.append(Part.LineSegment(FreeCAD.Vector(x3, y4, 0), FreeCAD.Vector(x4, y3, 0)))
        geometries.append(Part.LineSegment(FreeCAD.Vector(x4, y2, 0), FreeCAD.Vector(x3, y1, 0)))

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
        geometries.append(Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(4, 4, 0), FreeCAD.Vector(0, 0, 1), DIMS_TUBE_INNER_RADIUS), rad1, rad2))
        geometries.append(Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(4, 4, 0), FreeCAD.Vector(0, 0, 1), DIMS_TUBE_INNER_RADIUS), rad3, rad4))
        geometries.append(Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(4, 4, 0), FreeCAD.Vector(0, 0, 1), DIMS_TUBE_INNER_RADIUS), rad5, rad6))
        geometries.append(Part.ArcOfCircle(
            Part.Circle(FreeCAD.Vector(4, 4, 0), FreeCAD.Vector(0, 0, 1), DIMS_TUBE_INNER_RADIUS), rad7, rad8))

        # All arcs centred
        constraints.append(Sketcher.Constraint('Coincident', 6, 3, 0, 3))
        constraints.append(Sketcher.Constraint('Coincident', 7, 3, 0, 3))
        constraints.append(Sketcher.Constraint('Coincident', 8, 3, 0, 3))
        constraints.append(Sketcher.Constraint('Coincident', 9, 3, 0, 3))

        # All equal radius arcs
        constraints.append(Sketcher.Constraint('Radius', 6, DIMS_TUBE_INNER_RADIUS))
        constraints.append(Sketcher.Constraint('Equal', 6, 7))
        constraints.append(Sketcher.Constraint('Equal', 6, 8))
        constraints.append(Sketcher.Constraint('Equal', 6, 9))

        # Link arcs to segments
        constraints.append(Sketcher.Constraint('Coincident', 2, 2, 6, 2))
        constraints.append(Sketcher.Constraint('Coincident', 6, 1, 3, 1))
        constraints.append(Sketcher.Constraint('Coincident', 3, 2, 7, 2))
        constraints.append(Sketcher.Constraint('Coincident', 7, 1, 4, 1))
        constraints.append(Sketcher.Constraint('Coincident', 4, 2, 8, 2))
        constraints.append(Sketcher.Constraint('Coincident', 8, 1, 5, 1))
        constraints.append(Sketcher.Constraint('Coincident', 5, 2, 9, 2))
        constraints.append(Sketcher.Constraint('Coincident', 9, 1, 2, 1))

        # The critical measurement: distance to tangent construction line
        constraints.append(Sketcher.Constraint('Distance', 1, 2, 2, DIMS_TUBE_FLAT_THICKNESS))

        tubes_pocket_sketch.addGeometry(geometries, False)
        tubes_pocket_sketch.addConstraint(constraints)
        self.doc.recompute()

        # Set circle as a construction line
        tubes_pocket_sketch.toggleConstruction(0)

        # Set tangent line as a construction line
        tubes_pocket_sketch.toggleConstruction(1)

        # create array if needed
        if self.brick_width > 2 or self.brick_depth > 2:
            geometries = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            if self.brick_width == 2 and self.brick_depth > 2:
                tubes_pocket_sketch.addRectangularArray(geometries, FreeCAD.Vector(0, DIMS_STUD_WIDTH_INNER, 0), False,
                                                        self.brick_depth - 1, self.brick_width - 1, True)
            elif self.brick_width > 2 and self.brick_depth == 2:
                tubes_pocket_sketch.addRectangularArray(geometries, FreeCAD.Vector(DIMS_STUD_WIDTH_INNER, 0, 0), False,
                                                        self.brick_width - 1, self.brick_depth - 1, True)
            else:
                tubes_pocket_sketch.addRectangularArray(geometries, FreeCAD.Vector(0, DIMS_STUD_WIDTH_INNER, 0), False,
                                                        self.brick_depth - 1, self.brick_width - 1, True)

        # perform the pocket
        tubes_pocket = self.brick.newObject("PartDesign::Pocket", "tubes_pocket")
        tubes_pocket.Profile = tubes_pocket_sketch

        # Need to specify Dimension instead of UpToFace because of the following issue:
        # https://freecadweb.org/tracker/view.php?id=3177
        # https://forum.freecadweb.org/viewtopic.php?f=8&t=24238
        # tubes_pocket.Type = 3
        # tubes_pocket.UpToFace = (self.doc.XY_Plane, [""])
        # tubes_pocket.Offset = -1 * DIMS_STICK_AND_TUBE_BOTTOM_OFFSET
        tubes_pocket.Length = ((self.brick_height * DIMS_PLATE_HEIGHT)
                               - DIMS_TOP_THICKNESS - DIMS_STICK_AND_TUBE_BOTTOM_OFFSET)

        tubes_pocket_sketch.ViewObject.Visibility = False
        self.doc.recompute()

    def _render_stick_ribs(self):
        Console.PrintMessage("_render_stick_ribs()\n")

        stick_ribs_sketch = self.brick.newObject("Sketcher::SketchObject", "stick_ribs_sketch")
        if self.brick_width > 2:
            stick_ribs_sketch.Support = (self.doc.front_inside_datum_plane, '')
        else:
            stick_ribs_sketch.Support = (self.doc.side_inside_datum_plane, '')
        stick_ribs_sketch.MapMode = 'FlatFace'

        # add top_inside_datum_plane to sketch as an edge so that it can be referenced
        # this will add a line geometry element to the sketch as item 0
        stick_ribs_sketch.addExternal(self.doc.top_inside_datum_plane.Label, '')

        geometries = []
        constraints = []

        # choose correct sticks to render ribs on
        indices = []
        if self.brick_width > 1:
            studs = self.brick_width
        else:
            studs = self.brick_depth

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
                for i in range(((studs - 1) / 2), 0, -2):
                    indices.append(i)
                for i in range(((studs - 1) / 2) + 1, studs, 2):
                    indices.append(i)

        for i in indices:
            self._add_rib_sketch(geometries, constraints, i,
                                 DIMS_STICK_RIB_THICKNESS, DIMS_STICK_RIB_BOTTOM_OFFSET,
                                 xz_plane_bottom_left_vector(), xz_plane_bottom_right_vector(),
                                 xz_plane_bottom_right_vector(), xz_plane_top_right_vector())

        stick_ribs_sketch.addGeometry(geometries, False)
        stick_ribs_sketch.addConstraint(constraints)
        self.doc.recompute()

        # perform the pad
        stick_ribs_pad = self.brick.newObject("PartDesign::Pad", "stick_ribs_pad")
        stick_ribs_pad.Profile = stick_ribs_sketch
        if self.brick_width > 2:
            stick_ribs_pad.Reversed = 1
        # Need to specify Dimension instead of UpToFace because of the following issue:
        # https://freecadweb.org/tracker/view.php?id=3177
        # https://forum.freecadweb.org/viewtopic.php?f=8&t=24238
        stick_ribs_pad.Length = (2 * DIMS_HALF_STUD_WIDTH_OUTER) - (2 * DIMS_SIDE_THICKNESS)

        stick_ribs_sketch.ViewObject.Visibility = False

        self.doc.recompute()

    def _render_sticks(self, hollow_sticks):
        Console.PrintMessage("_render_sticks({0})\n".format(hollow_sticks))

        sticks_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "sticks_pad_sketch")
        sticks_pad_sketch.Support = (self.doc.top_inside_datum_plane, '')
        sticks_pad_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", 0, DIMS_STICK_OUTER_RADIUS))
        # Half stud offsets from origin (-1, 1 chooses the origin point)
        if self.brick_width > 1:
            constraints.append(Sketcher.Constraint("DistanceX", -1, 1, 0, 3, 0.5 * DIMS_STUD_WIDTH_INNER))
            constraints.append(Sketcher.Constraint("DistanceY", -1, 1, 0, 3, 0))
        else:
            constraints.append(Sketcher.Constraint("DistanceX", -1, 1, 0, 3, 0))
            constraints.append(Sketcher.Constraint("DistanceY", -1, 1, 0, 3, 0.5 * DIMS_STUD_WIDTH_INNER))

        sticks_pad_sketch.addGeometry(geometries, False)
        sticks_pad_sketch.addConstraint(constraints)
        self.doc.recompute()

        if self.brick_width > 1:
            sticks_pad_sketch.addRectangularArray([0], FreeCAD.Vector(DIMS_STUD_WIDTH_INNER, 0, 0), False,
                                                  self.brick_width - 1, 1, True)
        else:
            sticks_pad_sketch.addRectangularArray([0], FreeCAD.Vector(0, DIMS_STUD_WIDTH_INNER, 0), False,
                                                  self.brick_depth - 1, 1, True)

        # perform the pad
        sticks_pad = self.brick.newObject("PartDesign::Pad", "sticks_pad")
        sticks_pad.Profile = sticks_pad_sketch
        sticks_pad.Reversed = 1
        # Need to specify Dimension instead of UpToFace because of the following issue:
        # https://freecadweb.org/tracker/view.php?id=3177
        # https://forum.freecadweb.org/viewtopic.php?f=8&t=24238
        # sticks_pad.Type = 3
        # sticks_pad.UpToFace = (self.doc.XY_Plane, [""])
        # sticks_pad.Offset = -1 * DIMS_STICK_AND_TUBE_BOTTOM_OFFSET
        sticks_pad.Length = ((self.brick_height * DIMS_PLATE_HEIGHT)
                             - DIMS_TOP_THICKNESS - DIMS_STICK_AND_TUBE_BOTTOM_OFFSET)

        sticks_pad_sketch.ViewObject.Visibility = False

        if hollow_sticks:
            sticks_pocket_sketch = self.brick.newObject("Sketcher::SketchObject", "sticks_pocket_sketch")
            sticks_pocket_sketch.Support = (self.doc.top_inside_datum_plane, '')
            sticks_pocket_sketch.MapMode = 'FlatFace'

            geometries = []
            constraints = []

            geometries.append(Part.Circle())
            constraints.append(Sketcher.Constraint("Radius", 0, DIMS_STICK_INNER_RADIUS))
            # Half stud offsets from origin (-1, 1 chooses the origin point)
            if self.brick_width > 1:
                constraints.append(Sketcher.Constraint("DistanceX", -1, 1, 0, 3, 0.5 * DIMS_STUD_WIDTH_INNER))
                constraints.append(Sketcher.Constraint("DistanceY", -1, 1, 0, 3, 0))
            else:
                constraints.append(Sketcher.Constraint("DistanceX", -1, 1, 0, 3, 0))
                constraints.append(Sketcher.Constraint("DistanceY", -1, 1, 0, 3, 0.5 * DIMS_STUD_WIDTH_INNER))

            sticks_pocket_sketch.addGeometry(geometries, False)
            sticks_pocket_sketch.addConstraint(constraints)
            self.doc.recompute()

            if self.brick_width > 1:
                sticks_pocket_sketch.addRectangularArray([0], FreeCAD.Vector(DIMS_STUD_WIDTH_INNER, 0, 0), False,
                                                         self.brick_width - 1, 1, True)
            if self.brick_depth > 1:
                sticks_pocket_sketch.addRectangularArray([0], FreeCAD.Vector(0, DIMS_STUD_WIDTH_INNER, 0), False,
                                                         self.brick_depth - 1, 1, True)

            # perform the pocket
            sticks_pocket = self.brick.newObject("PartDesign::Pocket", "sticks_pocket")
            sticks_pocket.Profile = sticks_pocket_sketch
            # Need to specify Dimension instead of UpToFace because of the following issue:
            # https://freecadweb.org/tracker/view.php?id=3177
            # https://forum.freecadweb.org/viewtopic.php?f=8&t=24238
            # sticks_pad.Type = 3
            # sticks_pad.UpToFace = (self.doc.XY_Plane, [""])
            # sticks_pad.Offset = -1 * DIMS_STICK_AND_TUBE_BOTTOM_OFFSET
            sticks_pocket.Length = ((self.brick_height * DIMS_PLATE_HEIGHT)
                                    - DIMS_TOP_THICKNESS - DIMS_STICK_AND_TUBE_BOTTOM_OFFSET)

            sticks_pocket_sketch.ViewObject.Visibility = False

        self.doc.recompute()

    def _render_tubes_or_sticks(self):
        Console.PrintMessage("_render_tubes_or_sticks()\n")

        tubes = self.brick_depth > 1 and self.brick_width > 1
        tube_ribs = tubes and self.brick_height > 1 and (self.brick_depth > 2 or self.brick_width > 2)
        sticks = not tubes and (self.brick_depth > 1 or self.brick_width > 1) and not (
                    self.hole_style == HoleStyle.HOLE and self.holes_offset)
        stick_ribs = sticks and self.brick_height > 1 and not self.hole_style == HoleStyle.HOLE
        hollow_sticks = sticks and self.brick_height == 1

        if tube_ribs:
            self._render_tube_ribs()

        if tubes:
            self._render_tubes()

        if stick_ribs:
            self._render_stick_ribs()

        if sticks:
            self._render_sticks(hollow_sticks)

    def render(self):
        Console.PrintMessage("render\n")

        self._render_body_pad_and_fillets()

        self._render_body_pocket()

        self._render_tubes_or_sticks()
