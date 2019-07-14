# coding: UTF-8

from FreeCAD import Console, Vector
import Part
import Sketcher
from Legify.Common import *


class TopStudsRenderer:

    def __init__(self):
        Console.PrintMessage("TopStudsRenderer\n")

        self.doc = None
        self.brick = None

        self.width = None
        self.depth = None
        self.style = None
        self.width_count = None
        self.depth_count = None

        self.top_datum_plane = None
        self.top_inside_datum_plane = None

    def _render_top_studs_outside(self, initial_width_offset, initial_depth_offset, style):
        Console.PrintMessage("render_top_studs_outside({0},{1},{2})\n".format(
            initial_width_offset, initial_depth_offset, style))

        # top studs outside pad

        top_studs_outside_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "top_studs_outside_pad_sketch")
        top_studs_outside_pad_sketch.Support = (self.top_datum_plane, '')
        top_studs_outside_pad_sketch.MapMode = 'FlatFace'

        if style == TopStudStyle.OPEN:

            add_inner_circle_with_flats_to_sketch(top_studs_outside_pad_sketch, DIMS_STUD_OUTER_RADIUS,
                                                  DIMS_STUD_INNER_RADIUS, DIMS_STUD_FLAT_THICKNESS, False,
                                                  initial_width_offset, initial_depth_offset)
        else:
            add_circle_to_sketch(top_studs_outside_pad_sketch, DIMS_STUD_OUTER_RADIUS, initial_width_offset,
                                 initial_depth_offset)

        # create array if needed
        if self.width_count > 1 or self.depth_count > 1:
            geometry_indices = [range(0, len(top_studs_outside_pad_sketch.Geometry) - 1)]
            if self.width_count == 1 and self.depth_count > 1:
                top_studs_outside_pad_sketch.addRectangularArray(geometry_indices,
                                                                 Vector(0, DIMS_STUD_SPACING_INNER, 0), False,
                                                                 self.depth_count, self.width_count, True)
            elif self.width_count > 1 and self.depth_count == 1:
                top_studs_outside_pad_sketch.addRectangularArray(geometry_indices,
                                                                 Vector(DIMS_STUD_SPACING_INNER, 0, 0), False,
                                                                 self.width_count, self.depth_count, True)
            else:
                top_studs_outside_pad_sketch.addRectangularArray(geometry_indices,
                                                                 Vector(0, DIMS_STUD_SPACING_INNER, 0), False,
                                                                 self.depth_count, self.width_count, True)

        top_studs_outside_pad = self.brick.newObject("PartDesign::Pad", "top_studs_outside_pad")
        top_studs_outside_pad.Type = PAD_TYPE_DIMENSION
        top_studs_outside_pad.Profile = top_studs_outside_pad_sketch
        top_studs_outside_pad.Length = DIMS_STUD_HEIGHT

        self.doc.recompute()

        # determine the stud outer edges
        edge_names = get_circle_edge_names(self.top_datum_plane, True, DIMS_STUD_HEIGHT, top_studs_outside_pad,
                                           DIMS_STUD_OUTER_RADIUS)

        # top studs outer edge fillet
        top_stud_outer_fillets = self.brick.newObject("PartDesign::Fillet", "top_stud_outer_fillets")
        top_stud_outer_fillets.Radius = DIMS_STUD_FILLET
        top_stud_outer_fillets.Base = (top_studs_outside_pad, edge_names)

        self.doc.recompute()
        top_studs_outside_pad_sketch.ViewObject.Visibility = False

    def _render_top_studs_inside(self, initial_width_offset, initial_depth_offset):
        Console.PrintMessage("render_top_studs_inside({0},{1})\n".format(initial_width_offset, initial_depth_offset))

        # top studs inside pocket

        top_studs_inside_pocket_sketch = self.brick\
            .newObject("Sketcher::SketchObject", "top_studs_inside_pocket_sketch")
        top_studs_inside_pocket_sketch.Support = (self.top_inside_datum_plane, '')
        top_studs_inside_pocket_sketch.MapMode = 'FlatFace'

        add_circle_to_sketch(top_studs_inside_pocket_sketch, DIMS_STUD_INSIDE_HOLE_RADIUS,
                             initial_width_offset, initial_depth_offset)

        # create array if needed
        if self.width > 1 or self.depth > 1:
            geometry_indices = [range(0, len(top_studs_inside_pocket_sketch.Geometry) - 1)]
            if self.width == 1 and self.depth > 1:
                top_studs_inside_pocket_sketch.addRectangularArray(geometry_indices,
                                                                   Vector(0, DIMS_STUD_SPACING_INNER, 0), False,
                                                                   self.depth, self.width, True)
            elif self.width > 1 and self.depth == 1:
                top_studs_inside_pocket_sketch.addRectangularArray(geometry_indices,
                                                                   Vector(DIMS_STUD_SPACING_INNER, 0, 0), False,
                                                                   self.width, self.depth, True)
            else:
                top_studs_inside_pocket_sketch.addRectangularArray(geometry_indices,
                                                                   Vector(0, DIMS_STUD_SPACING_INNER, 0), False,
                                                                   self.depth, self.width, True)

        top_studs_inside_pocket = self.brick.newObject("PartDesign::Pocket", "top_studs_inside_pocket")
        top_studs_inside_pocket.Type = POCKET_TYPE_DIMENSION
        top_studs_inside_pocket.Profile = top_studs_inside_pocket_sketch
        top_studs_inside_pocket.Reversed = True
        top_studs_inside_pocket.Length = DIMS_TOP_THICKNESS + DIMS_STUD_INSIDE_HOLE_TOP_OFFSET

        self.doc.recompute()
        top_studs_inside_pocket_sketch.ViewObject.Visibility = False

    def render(self, context):
        Console.PrintMessage("render\n")

        self.doc = context.doc
        self.brick = context.brick

        self.width = context.width
        self.depth = context.depth
        self.style = context.top_studs_style
        self.width_count = context.top_studs_width_count
        self.depth_count = context.top_studs_depth_count

        self.top_datum_plane = context.top_datum_plane
        self.top_inside_datum_plane = context.top_inside_datum_plane

        initial_width_offset = (self.width - self.width_count) * DIMS_STUD_SPACING_INNER / 2
        initial_depth_offset = (self.depth - self.depth_count) * DIMS_STUD_SPACING_INNER / 2

        self._render_top_studs_outside(initial_width_offset, initial_depth_offset, self.style)

        # Only render inner pocket if closed studs AND studs are not offset
        if self.style == TopStudStyle.CLOSED and initial_width_offset == 0 and initial_depth_offset == 0:
            self._render_top_studs_inside(initial_width_offset, initial_depth_offset)
