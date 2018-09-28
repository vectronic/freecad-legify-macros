# coding: UTF-8

from FreeCAD import Console
import Part
import Sketcher
from Legify.Common import *


class TopStudsRenderer(object):

    def __init__(self, brick_width, brick_depth, top_stud_style, top_studs_width_count, top_studs_depth_count):
        Console.PrintMessage("TopStudsRenderer\n")

        self.doc = FreeCAD.activeDocument()
        self.brick = self.doc.brick

        self.width = brick_width
        self.depth = brick_depth
        self.style = top_stud_style
        self.width_count = top_studs_width_count
        self.depth_count = top_studs_depth_count

    @staticmethod
    def _add_stud_outer_pad_sketch(geometries, constraints, width_offset, depth_offset):
        Console.PrintMessage("_add_stud_outer_pad_sketch({0},{1})\n".format(width_offset, depth_offset))

        segment_count = len(geometries)

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", segment_count, DIMS_STUD_OUTER_RADIUS))
        # -1, 1 chooses the origin point
        constraints.append(Sketcher.Constraint("DistanceX", -1, 1, segment_count, 3, width_offset))
        # -1, 1 chooses the origin point
        constraints.append(Sketcher.Constraint("DistanceY", -1, 1, segment_count, 3, depth_offset))

    @staticmethod
    def _add_stud_inside_pocket_sketch(geometries, constraints, width_offset, depth_offset):
        Console.PrintMessage("_add_stud_inside_pocket_sketch({0},{1})\n".format(width_offset, depth_offset))

        segment_count = len(geometries)

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", segment_count, DIMS_STUD_INSIDE_HOLE_RADIUS))
        # -1, 1 chooses the origin point
        constraints.append(Sketcher.Constraint("DistanceX", -1, 1, segment_count, 3, width_offset))
        # -1, 1 chooses the origin point
        constraints.append(Sketcher.Constraint("DistanceY", -1, 1, segment_count, 3, depth_offset))

    def _render_studs_outside(self, initial_width_offset, initial_depth_offset):
        Console.PrintMessage("render_studs_outside({0},{1})\n".format(initial_width_offset, initial_depth_offset))

        top_studs_outside_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "top_studs_outside_pad_sketch")
        top_studs_outside_pad_sketch.Support = (self.doc.top_datum_plane, '')
        top_studs_outside_pad_sketch.MapMode = 'FlatFace'

        xy_plane_z = self.doc.top_datum_plane.Placement.Base.z

        geometries = []
        constraints = []

        for i in range(0, self.width_count):
            for j in range(0, self.depth_count):
                self._add_stud_outer_pad_sketch(geometries, constraints,
                                                initial_width_offset + i * DIMS_STUD_WIDTH_INNER,
                                                initial_depth_offset + j * DIMS_STUD_WIDTH_INNER)

        top_studs_outside_pad_sketch.addGeometry(geometries, False)
        top_studs_outside_pad_sketch.addConstraint(constraints)

        # perform the pad
        top_studs_outside_pad = self.brick.newObject("PartDesign::Pad", "top_studs_outside_pad")
        top_studs_outside_pad.Profile = top_studs_outside_pad_sketch
        top_studs_outside_pad.Length = DIMS_STUD_HEIGHT

        self.doc.recompute()

        top_studs_outside_pad_sketch.ViewObject.Visibility = False

        # determine the stud top edges
        edge_names = []
        for i in range(0, len(top_studs_outside_pad.Shape.Edges)):
            e = top_studs_outside_pad.Shape.Edges[i]
            if len(e.Vertexes) == 1:
                v = e.Vertexes[0]
                if v.Point.z == xy_plane_z + DIMS_STUD_HEIGHT:
                    edge_names.append("Edge" + repr(i + 1))

        # fillet the studs
        body_edge_fillets = self.brick.newObject("PartDesign::Fillet", "top_stud_fillets")
        body_edge_fillets.Radius = DIMS_EDGE_FILLET
        body_edge_fillets.Base = (top_studs_outside_pad, edge_names)

        self.doc.recompute()

    def _render_studs_inside(self, initial_width_offset, initial_depth_offset):
        Console.PrintMessage("render_studs_inside({0},{1})\n".format(initial_width_offset, initial_depth_offset))

        top_studs_inside_pocket_sketch = self.brick.newObject("Sketcher::SketchObject", "top_studs_inside_pocket_sketch")
        top_studs_inside_pocket_sketch.Support = (self.doc.top_inside_datum_plane, '')
        top_studs_inside_pocket_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        for i in range(0, self.width_count):
            for j in range(0, self.depth_count):
                self._add_stud_inside_pocket_sketch(geometries, constraints,
                                                    initial_width_offset + i * DIMS_STUD_WIDTH_INNER,
                                                    initial_depth_offset + j * DIMS_STUD_WIDTH_INNER)

        top_studs_inside_pocket_sketch.addGeometry(geometries, False)
        top_studs_inside_pocket_sketch.addConstraint(constraints)

        # perform the pad
        top_studs_inside_pocket = self.brick.newObject("PartDesign::Pocket", "top_studs_inside_pocket")
        top_studs_inside_pocket.Profile = top_studs_inside_pocket_sketch
        top_studs_inside_pocket.Reversed = True
        # Need to specify Dimension instead of UpToFace because of the following issue:
        # https://freecadweb.org/tracker/view.php?id=3177
        # https://forum.freecadweb.org/viewtopic.php?f=8&t=24238
        top_studs_inside_pocket.Length = DIMS_TOP_THICKNESS + DIMS_STUD_INSIDE_HOLE_TOP_OFFSET

        top_studs_inside_pocket_sketch.ViewObject.Visibility = False

        self.doc.recompute()

    # TODO: render inner and outer for open style stud
    # TODO: check if inner pocket when offset over tube
    def render(self):
        Console.PrintMessage("render\n")

        initial_width_offset = (self.width - self.width_count) * DIMS_STUD_WIDTH_INNER / 2
        initial_depth_offset = (self.depth - self.depth_count) * DIMS_STUD_WIDTH_INNER / 2

        self._render_studs_outside(initial_width_offset, initial_depth_offset)

        self._render_studs_inside(initial_width_offset, initial_depth_offset)
