# coding: UTF-8

from FreeCAD import Console
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

    @staticmethod
    def _add_side_stud_outer_pad_sketch(geometries, constraints, offset):
        Console.PrintMessage("_add_side_stud_outer_pad_sketch({0})\n".format(offset))

        segment_count = len(geometries)

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", segment_count, DIMS_STUD_OUTER_RADIUS))
        constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, offset))
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, DIMS_SIDE_FEATURE_CENTRE_HEIGHT))

        # add a smaller inner circle
        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", segment_count + 1, DIMS_STUD_INNER_RADIUS))
        constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count + 1, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, offset))
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count + 1, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               DIMS_SIDE_FEATURE_CENTRE_HEIGHT))

    @staticmethod
    def _add_side_stud_inside_pocket_sketch(geometries, constraints, offset):
        Console.PrintMessage("_add_side_stud_inside_pocket_sketch({0})\n".format(offset))

        segment_count = len(geometries)

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", segment_count, DIMS_STUD_INNER_RADIUS))
        constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, offset))
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, DIMS_SIDE_FEATURE_CENTRE_HEIGHT))

    def _render_side_studs_outside(self, label, plane, count, inverted):
        Console.PrintMessage("render_side_studs_outside({0},{1})\n".format(label, count))

        # side studs outside pad

        side_studs_outside_pad_sketch = self.brick.newObject("Sketcher::SketchObject",
                                                             label + "_side_studs_outside_pad_sketch")
        side_studs_outside_pad_sketch.Support = (plane, '')
        side_studs_outside_pad_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        for i in range(0, count):
            self._add_side_stud_outer_pad_sketch(geometries, constraints, i * DIMS_STUD_WIDTH_INNER)

        side_studs_outside_pad_sketch.addGeometry(geometries, False)
        side_studs_outside_pad_sketch.addConstraint(constraints)

        side_studs_outside_pad = self.brick.newObject("PartDesign::Pad", label + "_side_studs_outside_pad")
        side_studs_outside_pad.Type = PAD_TYPE_DIMENSION
        side_studs_outside_pad.Profile = side_studs_outside_pad_sketch
        side_studs_outside_pad.Length = DIMS_STUD_HEIGHT
        side_studs_outside_pad.Reversed = False if inverted else True

        self.doc.recompute()

        # determine the stud outer edges

        face_names = []
        for i in range(0, len(side_studs_outside_pad.Shape.Faces)):
            f = side_studs_outside_pad.Shape.Faces[i]
            # desired faces have two edges, both circles
            if len(f.Edges) == 2:
                if len(f.Edges[0].Vertexes) == 1 and len(f.Edges[1].Vertexes) == 1:
                    n1 = f.normalAt(0, 0)
                    n2 = plane.Shape.normalAt(0, 0)
                    n2 = n2 if inverted else n2.negative()
                    if n1.isEqual(n2, 1e-7):
                        face_names.append("Face" + repr(i + 1))

        # side studs fillet

        # TODO: determine if the inner edge of open or hole studs should be filleted
        side_stud_fillets = self.brick.newObject("PartDesign::Fillet", label + "_side_stud_fillets")
        side_stud_fillets.Radius = DIMS_EDGE_FILLET
        side_stud_fillets.Base = (side_studs_outside_pad, face_names)

        self.doc.recompute()
        side_studs_outside_pad_sketch.ViewObject.Visibility = False

    def _render_side_studs_inside(self, label, plane, count, inverted):
        Console.PrintMessage("render_side_studs_inside({0},{1})\n".format(label, count))

        # side studs pocket

        side_studs_inside_pocket_sketch = self.brick.newObject("Sketcher::SketchObject",
                                                               label + "_side_studs_inside_pocket_sketch")
        side_studs_inside_pocket_sketch.Support = (plane, '')
        side_studs_inside_pocket_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        for i in range(0, count):
            self._add_side_stud_inside_pocket_sketch(geometries, constraints, i * DIMS_STUD_WIDTH_INNER)

        side_studs_inside_pocket_sketch.addGeometry(geometries, False)
        side_studs_inside_pocket_sketch.addConstraint(constraints)

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
