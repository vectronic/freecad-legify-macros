# coding: UTF-8

from FreeCAD import Console, Vector
import Part
import Sketcher
from Legify.Common import *


class SideStudsRenderer:

    def __init__(self):
        Console.PrintMessage("SideStudsRenderer\n")

        self.doc = None
        self.brick = None

        self.width = None
        self.depth = None
        self.style = None
        self.front = None
        self.back = None
        self.left = None
        self.right = None

        self.front_datum_plane = None
        self.back_datum_plane = None
        self.left_datum_plane = None
        self.right_datum_plane = None

    def _render_side_studs_outside(self, label, plane, count, inverted):
        Console.PrintMessage("render_side_studs_outside({0},{1})\n".format(label, count))

        # side studs outside pad

        side_studs_outside_pad_sketch = self.brick.newObject("Sketcher::SketchObject",
                                                             label + "_side_studs_outside_pad_sketch")
        side_studs_outside_pad_sketch.Support = (plane, '')
        side_studs_outside_pad_sketch.MapMode = 'FlatFace'

        add_inner_circle_with_flats_to_sketch(side_studs_outside_pad_sketch, DIMS_STUD_OUTER_RADIUS,
                                              DIMS_STUD_INNER_RADIUS, DIMS_STUD_FLAT_THICKNESS, False,
                                              0, DIMS_SIDE_STUD_CENTRE_HEIGHT)

        # create array if needed
        if count > 1:
            geometry_indices = [range(0, len(side_studs_outside_pad_sketch.Geometry) - 1)]
            side_studs_outside_pad_sketch.addRectangularArray(geometry_indices,
                                                              Vector(DIMS_STUD_SPACING_INNER, 0, 0), False,
                                                              count, 1, True)

        side_studs_outside_pad = self.brick.newObject("PartDesign::Pad", label + "_side_studs_outside_pad")
        side_studs_outside_pad.Type = PAD_TYPE_DIMENSION
        side_studs_outside_pad.Profile = side_studs_outside_pad_sketch
        side_studs_outside_pad.Length = DIMS_STUD_HEIGHT
        side_studs_outside_pad.Reversed = False if inverted else True

        self.doc.recompute()

        # determine the stud outer edges
        edge_names = get_circle_edge_names(plane, inverted, DIMS_STUD_HEIGHT, side_studs_outside_pad,
                                           DIMS_STUD_OUTER_RADIUS)

        # side studs outer fillet
        side_stud_outer_fillets = self.brick.newObject("PartDesign::Fillet", label + "_side_stud_outer_fillets")
        side_stud_outer_fillets.Radius = DIMS_STUD_FILLET
        side_stud_outer_fillets.Base = (side_studs_outside_pad, edge_names)

        self.doc.recompute()
        side_studs_outside_pad_sketch.ViewObject.Visibility = False

    def _render_side_studs_inside(self, label, plane, count, inverted):
        Console.PrintMessage("render_side_studs_inside({0},{1})\n".format(label, count))

        # side studs pocket

        side_studs_inside_pocket_sketch = self.brick.newObject("Sketcher::SketchObject",
                                                               label + "_side_studs_inside_pocket_sketch")
        side_studs_inside_pocket_sketch.Support = (plane, '')
        side_studs_inside_pocket_sketch.MapMode = 'FlatFace'

        add_inner_circle_with_flats_to_sketch(side_studs_inside_pocket_sketch, DIMS_STUD_OUTER_RADIUS,
                                              DIMS_STUD_INNER_RADIUS, DIMS_STUD_FLAT_THICKNESS, True,
                                              0, DIMS_SIDE_STUD_CENTRE_HEIGHT)

        # create array if needed
        if count > 1:
            geometry_indices = [range(0, len(side_studs_inside_pocket_sketch.Geometry) - 1)]
            side_studs_inside_pocket_sketch.addRectangularArray(geometry_indices,
                                                                Vector(DIMS_STUD_SPACING_INNER, 0, 0), False,
                                                                count, 1, True)

        side_studs_inside_pocket = self.brick.newObject("PartDesign::Pocket", label + "_side_studs_inside_pocket")
        side_studs_inside_pocket.Type = POCKET_TYPE_DIMENSION
        side_studs_inside_pocket.Profile = side_studs_inside_pocket_sketch
        side_studs_inside_pocket.Reversed = inverted
        side_studs_inside_pocket.Length = DIMS_SIDE_THICKNESS + DIMS_STUD_INSIDE_HOLE_TOP_OFFSET

        self.doc.recompute()
        side_studs_inside_pocket_sketch.ViewObject.Visibility = False

    def render(self, context):
        Console.PrintMessage("render\n")

        self.doc = context.doc
        self.brick = context.brick

        self.width = context.width
        self.depth = context.depth
        self.style = context.side_studs_style
        self.front = context.side_studs_front
        self.back = context.side_studs_back
        self.left = context.side_studs_left
        self.right = context.side_studs_right

        self.front_datum_plane = context.front_datum_plane
        self.back_datum_plane = context.back_datum_plane
        self.left_datum_plane = context.left_datum_plane
        self.right_datum_plane = context.right_datum_plane

        if self.front:
            self._render_side_studs_outside("front", self.front_datum_plane, self.width, True)
            if self.style == SideStudStyle.HOLE:
                self._render_side_studs_inside("front", self.front_datum_plane, self.width, False)

        if self.back:
            self._render_side_studs_outside("back", self.back_datum_plane, self.width, False)
            if self.style == SideStudStyle.HOLE:
                self._render_side_studs_inside("back", self.back_datum_plane, self.width, True)

        if self.left:
            self._render_side_studs_outside("left", self.left_datum_plane, self.depth, False)
            if self.style == SideStudStyle.HOLE:
                self._render_side_studs_inside("left", self.left_datum_plane, self.depth, True)

        if self.right:
            self._render_side_studs_outside("right", self.right_datum_plane, self.depth, True)
            if self.style == SideStudStyle.HOLE:
                self._render_side_studs_inside("right", self.right_datum_plane, self.depth, False)
