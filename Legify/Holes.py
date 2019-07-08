# coding: UTF-8

from FreeCAD import Console, Placement, Rotation, Vector
import Part
import Sketcher
from Legify.Common import *


class HolesRenderer:

    def __init__(self):
        Console.PrintMessage("HolesRenderer\n")

        self.doc = None
        self.brick = None

        self.width = None
        self.depth = None
        self.style = None
        self.offset = None

        self.front_datum_plane = None
        self.xz_plane = None

    @staticmethod
    def _add_round_hole_sketch(geometries, constraints, offset, radius):
        Console.PrintMessage("_add_round_hole_pad_sketch({0}, {1})\n".format(offset, radius))

        segment_count = len(geometries)

        geometries.append(Part.Circle())
        constraints.append(Sketcher.Constraint("Radius", segment_count, radius))
        constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, offset))
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, DIMS_TECHNIC_HOLE_CENTRE_HEIGHT))

    @staticmethod
    def _add_axle_hole_sketch(geometries, constraints, offset):
        Console.PrintMessage("_add_axle_hole_pad_sketch({0})\n".format(offset))

        segment_count = len(geometries)

        # TODO: determine axle cross-section
        # geometries.append(Part.Circle())
        # constraints.append(Sketcher.Constraint("Radius", segment_count, radius))
        # constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
        #                                        SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
        #                                        SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, offset))
        # constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
        #                                        SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
        #                                        SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, DIMS_SIDE_FEATURE_CENTRE_HEIGHT))

    def _render_holes(self):
        Console.PrintMessage("render_holes()\n")

        hole_count = self.width if self.offset else (self.width - 1)
        hole_offset = 0 if self.offset else (DIMS_STUD_SPACING_INNER / 2)

        # holes pad

        # TODO: check cross-section of tubes meeting inside of body

        holes_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "holes_pad_sketch")
        holes_pad_sketch.Support = (self.front_datum_plane, '')
        holes_pad_sketch.MapMode = 'FlatFace'
        holes_pad_sketch.AttachmentOffset = Placement(Vector(0, 0, -1 * DIMS_SIDE_THICKNESS), Rotation(0, 0, 0))

        geometries = []
        constraints = []

        for i in range(0, hole_count):
            self._add_round_hole_sketch(geometries, constraints, hole_offset + (i * DIMS_STUD_SPACING_INNER),
                                        DIMS_TECHNIC_HOLE_OUTER_RADIUS)

        holes_pad_sketch.addGeometry(geometries, False)
        holes_pad_sketch.addConstraint(constraints)

        holes_pad = self.brick.newObject("PartDesign::Pad", "holes_pad")
        holes_pad.Type = PAD_TYPE_TO_LAST
        holes_pad.Profile = holes_pad_sketch

        holes_pad.Reversed = True
        self.doc.recompute()
        holes_pad_sketch.ViewObject.Visibility = False

        # holes pocket

        holes_pocket_sketch = self.brick.newObject("Sketcher::SketchObject", "holes_pocket_sketch")
        holes_pocket_sketch.Support = (self.front_datum_plane, '')
        holes_pocket_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        for i in range(0, hole_count):
            if self.style == HoleStyle.HOLE:
                self._add_round_hole_sketch(geometries, constraints, hole_offset + (i * DIMS_STUD_SPACING_INNER),
                                            DIMS_TECHNIC_HOLE_INNER_RADIUS)
            else:
                self._add_axle_hole_sketch(geometries, constraints, hole_offset + (i * DIMS_STUD_SPACING_INNER))

        holes_pocket_sketch.addGeometry(geometries, False)
        holes_pocket_sketch.addConstraint(constraints)

        holes_pocket = self.brick.newObject("PartDesign::Pocket", "holes_pocket")
        holes_pocket.Type = POCKET_TYPE_THROUGH_ALL
        holes_pocket.Profile = holes_pocket_sketch

        self.doc.recompute()
        holes_pocket_sketch.ViewObject.Visibility = False

        if self.style == HoleStyle.HOLE:

            # counterbore pocket

            holes_counterbore_pocket_sketch = self.brick.newObject("Sketcher::SketchObject",
                                                                   "holes_counterbore_pocket_sketch")
            holes_counterbore_pocket_sketch.Support = (self.front_datum_plane, '')
            holes_counterbore_pocket_sketch.MapMode = 'FlatFace'

            geometries = []
            constraints = []

            for i in range(0, hole_count):
                self._add_round_hole_sketch(geometries, constraints, hole_offset + (i * DIMS_STUD_SPACING_INNER),
                                            DIMS_TECHNIC_HOLE_COUNTERBORE_RADIUS)

            holes_counterbore_pocket_sketch.addGeometry(geometries, False)
            holes_counterbore_pocket_sketch.addConstraint(constraints)

            holes_counterbore_pocket = self.brick.newObject("PartDesign::Pocket", "holes_counterbore_pocket")
            holes_counterbore_pocket.Type = POCKET_TYPE_DIMENSION
            holes_counterbore_pocket.Profile = holes_counterbore_pocket_sketch
            holes_counterbore_pocket.Length = DIMS_TECHNIC_HOLE_COUNTERBORE_DEPTH

            self.doc.recompute()

            # counterbore mirror

            holes_counterbore_mirror = self.brick.newObject("PartDesign::Mirrored", "Mirrored")
            holes_counterbore_mirror.Originals = [holes_counterbore_pocket]
            holes_counterbore_mirror.MirrorPlane = (self.xz_plane, [""])
            self.brick.Tip = holes_counterbore_mirror

            self.doc.recompute()

            # TODO: fillet the outer hole of counterbore
            # NOTE: looks like no filleting required on lower hole of counterbore

            # determine the stud inner edges

            # face_names = []
            # for i in range(0, len(side_studs_outside_pad.Shape.Faces)):
            #     f = side_studs_outside_pad.Shape.Faces[i]
            #     # desired faces have two edges, both circles
            #     if len(f.Edges) == 2:
            #         if len(f.Edges[0].Vertexes) == 1 and len(f.Edges[1].Vertexes) == 1:
            #             n1 = f.normalAt(0, 0)
            #             n2 = plane.Shape.normalAt(0, 0)
            #             n2 = n2 if inverted else n2.negative()
            #             # TODO: filter inner edge
            #             if n1.isEqual(n2, 1e-7):
            #                 face_names.append("Face" + repr(i + 1))
            #
            # # side studs inner fillet
            # side_stud_inner_fillets = self.brick.newObject("PartDesign::Fillet", label + "_side_stud_inner_fillets")
            # side_stud_inner_fillets.Radius = DIMS_EDGE_FILLET
            # side_stud_inner_fillets.Base = (side_studs_outside_pad, face_names)
            #
            # self.doc.recompute()
            holes_counterbore_pocket_sketch.ViewObject.Visibility = False

    def render(self, context):
        Console.PrintMessage("render\n")

        self.doc = context.doc
        self.brick = context.brick

        self.width = context.width
        self.depth = context.depth
        self.style = context.hole_style
        self.offset = context.holes_offset

        self.front_datum_plane = context.front_datum_plane
        self.xz_plane = context.xz_plane

        self._render_holes()
