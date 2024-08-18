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
        self.front_inside_datum_plane = None
        self.back_inside_datum_plane = None
        self.depth_mirror_datum_plane = None
        self.top_inside_datum_plane = None

    @staticmethod
    def _add_technic_surround(geometries, constraints, hole_offset):
        Console.PrintMessage("_add_technic_surround_to_sketch({})\n".format(hole_offset))

        segment_count = len(geometries)

        # Rounded bottom side arc
        geometries.append(Part.ArcOfCircle(
            Part.Circle(Vector(hole_offset + DIMS_TECHNIC_HOLE_OUTER_RADIUS, DIMS_TECHNIC_HOLE_CENTRE_HEIGHT, 0),
                        Vector(0, 0, 1), DIMS_TECHNIC_HOLE_OUTER_RADIUS), math.pi, 2 * math.pi))

        # arc first point
        constraints.append(Sketcher.Constraint("DistanceX", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               hole_offset - DIMS_TECHNIC_HOLE_OUTER_RADIUS))
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, DIMS_TECHNIC_HOLE_CENTRE_HEIGHT))

        # Arc centre
        constraints.append(Sketcher.Constraint("DistanceY", SKETCH_GEOMETRY_ORIGIN_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, segment_count,
                                               SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX, DIMS_TECHNIC_HOLE_CENTRE_HEIGHT))

        # Arc second point
        constraints.append(Sketcher.Constraint("DistanceX", segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               2 * DIMS_TECHNIC_HOLE_OUTER_RADIUS))
        constraints.append(Sketcher.Constraint("DistanceY", segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX, 0))

        geometries.append(Part.LineSegment(xz_plane_bottom_right_vector(), xz_plane_top_right_vector()))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 1))
        constraints.append(Sketcher.Constraint("Coincident", segment_count, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 1, SKETCH_GEOMETRY_VERTEX_START_INDEX))

        # Render up until top_inside_datum_plane - already added as a line geometry element to the sketch
        constraints.append(Sketcher.Constraint("PointOnObject", segment_count + 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               SKETCH_GEOMETRY_FIRST_EXTERNAL_INDEX))

        geometries.append(Part.LineSegment(xz_plane_bottom_right_vector(), xz_plane_bottom_left_vector()))
        constraints.append(Sketcher.Constraint("Horizontal", segment_count + 2))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 2, SKETCH_GEOMETRY_VERTEX_START_INDEX))

        geometries.append(Part.LineSegment(xz_plane_top_right_vector(), xz_plane_bottom_right_vector()))
        constraints.append(Sketcher.Constraint("Vertical", segment_count + 3))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count + 3, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("Coincident", segment_count + 3, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               segment_count, SKETCH_GEOMETRY_VERTEX_START_INDEX))

    def _render_holes(self):
        Console.PrintMessage("render_holes()\n")

        hole_count = (self.width - 1) if self.offset else self.width
        hole_offset = (DIMS_STUD_SPACING / 2) if self.offset else 0

        # holes pad with cross-section meeting inside of body

        holes_pad_sketch = self.brick.newObject("Sketcher::SketchObject", "holes_pad_sketch")
        holes_pad_sketch.AttachmentSupport = (self.front_inside_datum_plane, '')
        holes_pad_sketch.MapMode = 'FlatFace'

        geometries = []
        constraints = []

        # add top_inside_datum_plane to sketch as an edge so that it can be referenced
        # this will add a line geometry element to the sketch as item 0
        holes_pad_sketch.addExternal(self.top_inside_datum_plane.Label, '')

        for i in range(0, hole_count):
            self._add_technic_surround(geometries, constraints, hole_offset + (i * DIMS_STUD_SPACING))

        holes_pad_sketch.addGeometry(geometries, False)
        holes_pad_sketch.addConstraint(constraints)

        holes_pad = self.brick.newObject("PartDesign::Pad", "holes_pad")
        holes_pad.Type = PAD_TYPE_UP_TO_FACE
        holes_pad.UpToFace = (self.back_inside_datum_plane, [""])
        holes_pad.Profile = holes_pad_sketch

        holes_pad.Reversed = True
        self.doc.recompute()
        holes_pad_sketch.ViewObject.Visibility = False

        # holes pocket

        holes_pocket_sketch = self.brick.newObject("Sketcher::SketchObject", "holes_pocket_sketch")
        holes_pocket_sketch.AttachmentSupport = (self.front_datum_plane, '')
        holes_pocket_sketch.MapMode = 'FlatFace'

        # TODO: if/else render axle cross-section
        # self._add_axle_hole_sketch(geometries, constraints, hole_offset + (i * DIMS_STUD_SPACING))
        add_circle_to_sketch(holes_pocket_sketch, DIMS_TECHNIC_HOLE_INNER_RADIUS, hole_offset,
                             DIMS_TECHNIC_HOLE_CENTRE_HEIGHT, False)
        self.doc.recompute()

        # create array if needed
        if hole_count > 1:
            geometry_indices = [range(0, len(holes_pocket_sketch.Geometry) - 1)]
            holes_pocket_sketch.addRectangularArray(geometry_indices,
                                                    Vector(DIMS_STUD_SPACING, 0, 0), False,
                                                    hole_count, 1, True)

        holes_pocket = self.brick.newObject("PartDesign::Pocket", "holes_pocket")
        holes_pocket.Type = POCKET_TYPE_THROUGH_ALL
        holes_pocket.Profile = holes_pocket_sketch

        self.doc.recompute()
        holes_pocket_sketch.ViewObject.Visibility = False

        if self.style == HoleStyle.HOLE:

            # counterbore pocket

            holes_counterbore_pocket_sketch = self.brick.newObject("Sketcher::SketchObject",
                                                                   "holes_counterbore_pocket_sketch")
            holes_counterbore_pocket_sketch.AttachmentSupport = (holes_pocket_sketch, '')
            holes_counterbore_pocket_sketch.MapMode = 'ObjectXY'

            add_circle_to_sketch(holes_counterbore_pocket_sketch, DIMS_TECHNIC_HOLE_COUNTERBORE_RADIUS, hole_offset,
                                 DIMS_TECHNIC_HOLE_CENTRE_HEIGHT, False)
            self.doc.recompute()

            # create array if needed
            if hole_count > 1:
                geometry_indices = [range(0, len(holes_pocket_sketch.Geometry) - 1)]
                holes_counterbore_pocket_sketch.addRectangularArray(geometry_indices,
                                                                    Vector(DIMS_STUD_SPACING, 0, 0), False,
                                                                    hole_count, 1, True)

            holes_counterbore_pocket = self.brick.newObject("PartDesign::Pocket", "holes_counterbore_pocket")
            holes_counterbore_pocket.Type = POCKET_TYPE_DIMENSION
            holes_counterbore_pocket.Profile = holes_counterbore_pocket_sketch
            holes_counterbore_pocket.Length = DIMS_TECHNIC_HOLE_COUNTERBORE_DEPTH

            self.doc.recompute()

            # counterbore mirror

            # do not use self.brick.newObject("PartDesign::Mirrored", "Mirrored") here as the
            # brick.Tip will not be updated
            holes_counterbore_mirror = self.doc.addObject("PartDesign::Mirrored", "Mirrored")
            holes_counterbore_mirror.Originals = [holes_counterbore_pocket]
            holes_counterbore_mirror.MirrorPlane = (self.depth_mirror_datum_plane, [""])
            self.brick.addObject(holes_counterbore_mirror)

            self.doc.recompute()

            # fillet the outer hole of counterbore
            # NOTE: looks like no filleting required on lower hole of counterbore

            edge_names = get_circle_edge_names(self.front_datum_plane, True, 0, holes_counterbore_mirror,
                                               DIMS_TECHNIC_HOLE_COUNTERBORE_RADIUS)

            edge_names.extend(get_circle_edge_names(self.front_datum_plane, False, DIMS_STUD_SPACING
                                                    + ((self.depth - 1) * DIMS_STUD_SPACING),
                                                    holes_counterbore_mirror, DIMS_TECHNIC_HOLE_COUNTERBORE_RADIUS))

            hole_counterbore_fillets = self.brick.newObject("PartDesign::Fillet", "hole_counterbore_fillets")
            hole_counterbore_fillets.Radius = DIMS_EDGE_FILLET
            hole_counterbore_fillets.Base = (holes_counterbore_mirror, edge_names)

            self.doc.recompute()

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
        self.front_inside_datum_plane = context.front_inside_datum_plane
        self.back_inside_datum_plane = context.back_inside_datum_plane
        self.depth_mirror_datum_plane = context.depth_mirror_datum_plane
        self.top_inside_datum_plane = context.top_inside_datum_plane

        self._render_holes()
