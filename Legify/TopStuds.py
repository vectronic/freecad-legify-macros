# coding: UTF-8

from FreeCAD import Console
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

    @staticmethod
    def _add_top_stud_outer_pad_sketch(geometries, constraints, width_offset, depth_offset, style):
        Console.PrintMessage("_add_top_stud_outer_pad_sketch({0},{1},{2})\n".format(width_offset, depth_offset, style))

        segment_count = len(geometries)

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", segment_count, DIMS_STUD_OUTER_RADIUS))
        constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, width_offset))
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, depth_offset))

        if style == TopStudStyle.OPEN:
            # add a smaller inner circle if open studs
            geometries.append(Part.Circle())
            constraints.append(Sketcher.Constraint("Radius", segment_count + 1, DIMS_STUD_INNER_RADIUS))
            constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count + 1,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, width_offset))
            constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                                   SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count + 1,
                                                   SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, depth_offset))

    @staticmethod
    def _add_top_stud_inside_pocket_sketch(geometries, constraints, width_offset, depth_offset):
        Console.PrintMessage("_add_top_stud_inside_pocket_sketch({0},{1})\n".format(width_offset, depth_offset))

        segment_count = len(geometries)

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", segment_count, DIMS_STUD_INSIDE_HOLE_RADIUS))
        constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, width_offset))
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, depth_offset))

    def _render_top_studs_outside(self, initial_width_offset, initial_depth_offset, style):
        Console.PrintMessage("render_top_studs_outside({0},{1},{2})\n".format(
            initial_width_offset, initial_depth_offset, style))

        top_studs_outside_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "top_studs_outside_pad_sketch")
        top_studs_outside_pad_sketch.Support = (self.top_datum_plane, '')
        top_studs_outside_pad_sketch.MapMode = 'FlatFace'

        xy_plane_z = self.top_datum_plane.Placement.Base.z

        geometries = []
        constraints = []

        for i in range(0, self.width_count):
            for j in range(0, self.depth_count):
                self._add_top_stud_outer_pad_sketch(geometries, constraints,
                                                    initial_width_offset + i * DIMS_STUD_WIDTH_INNER,
                                                    initial_depth_offset + j * DIMS_STUD_WIDTH_INNER,
                                                    style)

        top_studs_outside_pad_sketch.addGeometry(geometries, False)
        top_studs_outside_pad_sketch.addConstraint(constraints)

        # perform the pad
        top_studs_outside_pad = self.brick.newObject("PartDesign::Pad", "top_studs_outside_pad")
        top_studs_outside_pad.Profile = top_studs_outside_pad_sketch
        top_studs_outside_pad.Length = DIMS_STUD_HEIGHT

        self.doc.recompute()

        # determine the stud top edges
        edge_names = []
        for i in range(0, len(top_studs_outside_pad.Shape.Edges)):
            e = top_studs_outside_pad.Shape.Edges[i]
            # circles have only one vertex
            if len(e.Vertexes) == 1:
                v = e.Vertexes[0]
                if v.Point.z == xy_plane_z + DIMS_STUD_HEIGHT:
                    edge_names.append("Edge" + repr(i + 1))

        # fillet the studs
        # TODO: check if inner edge of open stud should be filleted (currently it is)
        top_stud_fillets = self.brick.newObject("PartDesign::Fillet", "top_stud_fillets")
        top_stud_fillets.Radius = DIMS_EDGE_FILLET
        top_stud_fillets.Base = (top_studs_outside_pad, edge_names)

        self.doc.recompute()
        top_studs_outside_pad_sketch.ViewObject.Visibility = False

    def _render_top_studs_inside(self, initial_width_offset, initial_depth_offset):
        Console.PrintMessage("render_top_studs_inside({0},{1})\n".format(initial_width_offset, initial_depth_offset))

        top_studs_inside_pocket_sketch = self.brick\
            .newObject("Sketcher::SketchObject", "top_studs_inside_pocket_sketch")
        top_studs_inside_pocket_sketch.Support = (self.top_inside_datum_plane, '')
        top_studs_inside_pocket_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        for i in range(0, self.width_count):
            for j in range(0, self.depth_count):
                self._add_top_stud_inside_pocket_sketch(geometries, constraints,
                                                        initial_width_offset + i * DIMS_STUD_WIDTH_INNER,
                                                        initial_depth_offset + j * DIMS_STUD_WIDTH_INNER)

        top_studs_inside_pocket_sketch.addGeometry(geometries, False)
        top_studs_inside_pocket_sketch.addConstraint(constraints)

        # perform the pocket
        top_studs_inside_pocket = self.brick.newObject("PartDesign::Pocket", "top_studs_inside_pocket")
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

        initial_width_offset = (self.width - self.width_count) * DIMS_STUD_WIDTH_INNER / 2
        initial_depth_offset = (self.depth - self.depth_count) * DIMS_STUD_WIDTH_INNER / 2

        self._render_top_studs_outside(initial_width_offset, initial_depth_offset, self.style)

        # Only render inner pocket if closed studs AND studs are not offset
        if self.style == TopStudStyle.CLOSED and initial_width_offset == 0 and initial_depth_offset == 0:
            self._render_top_studs_inside(initial_width_offset, initial_depth_offset)
