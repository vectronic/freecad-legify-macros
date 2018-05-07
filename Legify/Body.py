# coding: UTF-8

import FreeCAD
import Part
import Sketcher
from Legify.Common import *


class BodyRenderer(object):

    def __init__(self, width, depth, height):
        FreeCAD.Console.PrintMessage("BodyRenderer\n")

        self.brick_width = width
        self.brick_depth = depth
        self.brick_height = height

    @staticmethod
    def _render_pocket_rib_horizontal(segments, constraints, start_segment_length, end_segment_length,
                                      hor_vec_start, hor_vec_end,
                                      ver_vec_start, ver_vec_end,
                                      reverse):
        FreeCAD.Console.PrintMessage("_render_pocket_rib_horizontal({0},{1})\n"
                                     .format(start_segment_length, end_segment_length))

        segment_count = len(segments)

        segments.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count))
        if segment_count > 0:
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, 2, segment_count, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count, 1, segment_count, 2,
                                               (-1 if reverse else 1) * (start_segment_length -
                                                                         (DIMS_FULL_HEIGHT_SIDE_RIB_WIDTH / 2))))

        segments.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count, 2, segment_count + 1, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 1, 1, segment_count + 1, 2,
                                               (-1 if reverse else 1) * DIMS_FULL_HEIGHT_SIDE_RIB_DEPTH))

        segments.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 2))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 1, 2, segment_count + 2, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 2, 1, segment_count + 2, 2,
                                               (-1 if reverse else 1) * DIMS_FULL_HEIGHT_SIDE_RIB_WIDTH))

        segments.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 3))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 2, 2, segment_count + 3, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 3, 1, segment_count + 3, 2,
                                               (1 if reverse else -1) * DIMS_FULL_HEIGHT_SIDE_RIB_DEPTH))

        segments.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 4))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 3, 2, segment_count + 4, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 4, 1, segment_count + 4, 2,
                                               (-1 if reverse else 1) * (end_segment_length -
                                                                         (DIMS_FULL_HEIGHT_SIDE_RIB_WIDTH / 2))))

    @staticmethod
    def _render_pocket_rib_vertical(segments, constraints, start_segment_length, end_segment_length,
                                    ver_vec_start, ver_vec_end,
                                    hor_vec_start, hor_vec_end,
                                    reverse):
        FreeCAD.Console.PrintMessage("_render_pocket_rib_vertical({0},{1})\n"
                                     .format(start_segment_length, end_segment_length))

        segment_count = len(segments)

        segments.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count))
        if segment_count > 0:
            constraints.append(Sketcher.Constraint("Coincident", segment_count - 1, 2, segment_count, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count, 1, segment_count, 2,
                                               (-1 if reverse else 1) * (start_segment_length -
                                                                         (DIMS_FULL_HEIGHT_SIDE_RIB_WIDTH / 2))))

        segments.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count, 2, segment_count + 1, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 1, 1, segment_count + 1, 2,
                                               (1 if reverse else -1) * DIMS_FULL_HEIGHT_SIDE_RIB_DEPTH))

        segments.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 2))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 1, 2, segment_count + 2, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 2, 1, segment_count + 2, 2,
                                               (-1 if reverse else 1) * DIMS_FULL_HEIGHT_SIDE_RIB_WIDTH))

        segments.append(Part.LineSegment(hor_vec_start, hor_vec_end))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 3))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 2, 2, segment_count + 3, 1))
        constraints.append(Sketcher.Constraint("DistanceX", segment_count + 3, 1, segment_count + 3, 2,
                                               (-1 if reverse else 1) * DIMS_FULL_HEIGHT_SIDE_RIB_DEPTH))

        segments.append(Part.LineSegment(ver_vec_start, ver_vec_end))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 4))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 3, 2, segment_count + 4, 1))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count + 4, 1, segment_count + 4, 2,
                                               (-1 if reverse else 1) * (end_segment_length -
                                                                         (DIMS_FULL_HEIGHT_SIDE_RIB_WIDTH / 2))))

    def render(self):
        FreeCAD.Console.PrintMessage("render\n")

        doc = FreeCAD.activeDocument()

        body = doc.addObject("PartDesign::Body", "body")

        body_pad_sketch = body.newObject("Sketcher::SketchObject", "body_pad_sketch")

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

            # Half stud offsets from origin
            # -1, 1 chooses the origin point
            Sketcher.Constraint("DistanceX", 0, 1, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER),
            # -1, 1 chooses the origin point
            Sketcher.Constraint("DistanceY", 0, 1, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER),

            # Depth
            Sketcher.Constraint("DistanceX", 0, 1, 0, 2, (self.brick_depth - 1) * DIMS_STUD_WIDTH_INNER
                                + (2 * DIMS_HALF_STUD_WIDTH_OUTER)),
            # Width
            Sketcher.Constraint("DistanceY", 1, 1, 1, 2, (self.brick_width - 1) * DIMS_STUD_WIDTH_INNER
                                + (2 * DIMS_HALF_STUD_WIDTH_OUTER))

        ])

        # Height
        body_pad = body.newObject("PartDesign::Pad", "body_pad")
        body_pad.Profile = body_pad_sketch
        body_pad.Length = self.brick_height * DIMS_PLATE_HEIGHT

        body_pad_sketch.ViewObject.Visibility = False
        body_pad.ViewObject.Visibility = False
        doc.recompute()

        # Render edge fillets
        edge_names = []
        for i in range(0, len(body_pad.Shape.Edges)):
            edge_names.append("Edge" + repr(i + 1))

        body_edge_fillets = body.newObject("PartDesign::Fillet", "body_edge_fillets")
        body_edge_fillets.Radius = 0.1
        body_edge_fillets.Base = (body_pad, edge_names)

        body_edge_fillets.ViewObject.Visibility = False
        doc.recompute()

        # render pocket
        body_pocket_sketch = body.newObject("Sketcher::SketchObject", "body_pocket_sketch")

        # TODO: support 2x1 tile with center stud rib variation
        ribs = self.brick_height == 3 and self.brick_depth > 1 and self.brick_width > 1

        segments = []
        constraints = []

        if ribs:

            # complex rectangle with ribs

            # First horizontal
            # => 1st stud
            self._render_pocket_rib_horizontal(segments, constraints,
                                               DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS,
                                               DIMS_STUD_WIDTH_INNER / 2,
                                               xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                               xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                               False)

            # => 2nd to N-1 stud
            if self.brick_width > 2:
                for i in range(1, self.brick_width - 1):
                    self._render_pocket_rib_horizontal(segments, constraints,
                                                       DIMS_STUD_WIDTH_INNER / 2,
                                                       DIMS_STUD_WIDTH_INNER / 2,
                                                       xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                                       xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                       False)

            # => Nth stud
            self._render_pocket_rib_horizontal(segments, constraints,
                                               DIMS_STUD_WIDTH_INNER / 2,
                                               DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS,
                                               xy_plane_top_left_vector(), xy_plane_top_right_vector(),
                                               xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                               False)

            # First vertical
            # => 1st stud
            self._render_pocket_rib_vertical(segments, constraints,
                                             DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS,
                                             DIMS_STUD_WIDTH_INNER / 2,
                                             xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                             xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector(),
                                             False)

            # => 2nd to N-1 stud
            if self.brick_depth > 2:
                for i in range(1, self.brick_depth - 1):
                    self._render_pocket_rib_vertical(segments, constraints,
                                                     DIMS_STUD_WIDTH_INNER / 2,
                                                     DIMS_STUD_WIDTH_INNER / 2,
                                                     xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                                     xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector(),
                                                     False)

            # => Nth stud
            self._render_pocket_rib_vertical(segments, constraints,
                                             DIMS_STUD_WIDTH_INNER / 2,
                                             DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS,
                                             xy_plane_top_right_vector(), xy_plane_bottom_right_vector(),
                                             xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector(),
                                             False)

            # Second horizontal
            # => 1st stud
            self._render_pocket_rib_horizontal(segments, constraints,
                                               DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS,
                                               DIMS_STUD_WIDTH_INNER / 2,
                                               xy_plane_top_right_vector(), xy_plane_top_left_vector(),
                                               xy_plane_bottom_right_vector(), xy_plane_top_right_vector(),
                                               True)

            # => 2nd to N-1 stud
            if self.brick_width > 2:
                for i in range(1, self.brick_width - 1):
                    self._render_pocket_rib_horizontal(segments, constraints,
                                                       DIMS_STUD_WIDTH_INNER / 2,
                                                       DIMS_STUD_WIDTH_INNER / 2,
                                                       xy_plane_top_right_vector(), xy_plane_top_left_vector(),
                                                       xy_plane_bottom_right_vector(), xy_plane_top_right_vector(),
                                                       True)

            # => Nth stud
            self._render_pocket_rib_horizontal(segments, constraints,
                                               DIMS_STUD_WIDTH_INNER / 2,
                                               DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS,
                                               xy_plane_top_right_vector(), xy_plane_top_left_vector(),
                                               xy_plane_bottom_right_vector(), xy_plane_top_right_vector(),
                                               True)

            # Second vertical
            # => 1st stud
            self._render_pocket_rib_vertical(segments, constraints,
                                             DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS,
                                             DIMS_STUD_WIDTH_INNER / 2,
                                             xy_plane_bottom_right_vector(), xy_plane_top_right_vector(),
                                             xy_plane_bottom_left_vector(), xy_plane_bottom_right_vector(),
                                             True)

            # => 2nd to N-1 stud
            if self.brick_depth > 2:
                for i in range(1, self.brick_depth - 1):
                    self._render_pocket_rib_vertical(segments, constraints,
                                                     DIMS_STUD_WIDTH_INNER / 2,
                                                     DIMS_STUD_WIDTH_INNER / 2,
                                                     xy_plane_bottom_right_vector(), xy_plane_top_right_vector(),
                                                     xy_plane_bottom_left_vector(), xy_plane_bottom_right_vector(),
                                                     True)

            # => Nth stud
            self._render_pocket_rib_vertical(segments, constraints,
                                             DIMS_STUD_WIDTH_INNER / 2,
                                             DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS,
                                             xy_plane_bottom_right_vector(), xy_plane_top_right_vector(),
                                             xy_plane_bottom_left_vector(), xy_plane_bottom_right_vector(),
                                             True)

            # Half stud offsets from origin
            # -1, 1 chooses the origin point
            constraints.append(Sketcher.Constraint("DistanceX", 0, 1, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER
                                                   - DIMS_SIDE_THICKNESS))
            # -1, 1 chooses the origin point
            constraints.append(Sketcher.Constraint("DistanceY", 0, 1, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER
                                                   - DIMS_SIDE_THICKNESS))

        else:

            # simple rectangle

            segments.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_top_right_vector()))
            constraints.append(Sketcher.Constraint("Horizontal", 0))

            segments.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_bottom_right_vector()))
            constraints.append(Sketcher.Constraint("Vertical", 1))
            constraints.append(Sketcher.Constraint("Coincident", 0, 2, 1, 1))

            segments.append(Part.LineSegment(xy_plane_bottom_right_vector(), xy_plane_bottom_left_vector()))
            constraints.append(Sketcher.Constraint("Horizontal", 2))
            constraints.append(Sketcher.Constraint("Coincident", 1, 2, 2, 1))

            segments.append(Part.LineSegment(xy_plane_bottom_left_vector(), xy_plane_top_left_vector()))
            constraints.append(Sketcher.Constraint("Vertical", 3))
            constraints.append(Sketcher.Constraint("Coincident", 2, 2, 3, 1))

            # Complete the rectangle
            constraints.append(Sketcher.Constraint("Coincident", 3, 2, 0, 1))

            # Half stud offsets from origin
            # -1, 1 chooses the origin point
            # -1, 1 chooses the origin point
            constraints.append(Sketcher.Constraint("DistanceX", 0, 1, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER
                                                   - DIMS_SIDE_THICKNESS))
            constraints.append(Sketcher.Constraint("DistanceY", 0, 1, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER
                                                   - DIMS_SIDE_THICKNESS))

            # Depth
            constraints.append(Sketcher.Constraint("DistanceX", 0, 1, 0, 2,
                                                   (self.brick_depth - 1) * DIMS_STUD_WIDTH_INNER
                                                   + (2 * DIMS_HALF_STUD_WIDTH_OUTER)
                                                   - (2 * DIMS_SIDE_THICKNESS)))

            # Width
            constraints.append(Sketcher.Constraint("DistanceY", 1, 1, 1, 2,
                                                   (self.brick_width - 1) * DIMS_STUD_WIDTH_INNER
                                                   + (2 * DIMS_HALF_STUD_WIDTH_OUTER)
                                                   - (2 * DIMS_SIDE_THICKNESS)))

        body_pocket_sketch.addGeometry(segments, False)
        body_pocket_sketch.addConstraint(constraints)

        body_pocket = body.newObject("PartDesign::Pocket", "body_pocket")
        body_pocket.Profile = body_pocket_sketch
        body_pocket.Reversed = True
        body_pocket.Length = (self.brick_height * DIMS_PLATE_HEIGHT) - DIMS_TOP_THICKNESS

        body_pocket_sketch.ViewObject.Visibility = False
        doc.recompute()

        # TODO: support tube variations

        # TODO: support tube rib variations

        # TODO: support bottom fillet (for tiles only)
