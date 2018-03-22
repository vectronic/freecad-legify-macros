# coding: UTF-8

import FreeCAD
import Part
import Sketcher
from Legify.Common import *


class BodyRenderer(object):

    def __init__(self, width, length, height):
        FreeCAD.Console.PrintMessage("BodyRenderer\n")

        self.brick_width = width
        self.brick_length = length
        self.brick_height = height

    def render(self):
        FreeCAD.Console.PrintMessage("render\n")

        doc = FreeCAD.activeDocument()

        body = doc.addObject("PartDesign::Body", "body")

        body_pad_sketch = body.newObject("Sketcher::SketchObject", "body_pad_sketch")

        body_pad_sketch.addGeometry([

            # Rectangle geometry
            Part.LineSegment(FreeCAD.Vector(-1, 1, 0), FreeCAD.Vector(1, 1, 0)),
            Part.LineSegment(FreeCAD.Vector(1, 1, 0), FreeCAD.Vector(1, -1, 0)),
            Part.LineSegment(FreeCAD.Vector(1, -1, 0), FreeCAD.Vector(-1, -1, 0)),
            Part.LineSegment(FreeCAD.Vector(-1, -1, 0), FreeCAD.Vector(-1, 1, 0))
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
            Sketcher.Constraint("DistanceX", 2, 2, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER),
            Sketcher.Constraint("DistanceY", 2, 2, -1, 1, DIMS_HALF_STUD_WIDTH_OUTER),

            # Width
            Sketcher.Constraint("DistanceY", 2, 2, 0, 1, (self.brick_width - 1) * DIMS_STUD_WIDTH_INNER
                                + (2 * DIMS_HALF_STUD_WIDTH_OUTER)),

            # Length
            Sketcher.Constraint("DistanceX", 0, 1, 0, 2, (self.brick_length - 1) * DIMS_STUD_WIDTH_INNER
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
        body_edge_fillets.Base = (FreeCAD.ActiveDocument.body_pad, edge_names)

        body_edge_fillets.ViewObject.Visibility = False
        doc.recompute()

        # render pocket
        body_pocket_sketch = body.newObject("Sketcher::SketchObject", "body_pocket_sketch")

        # Add body sketch edge references
        for i in range(0, len(body_pad_sketch.Shape.Edges)):
            body_pocket_sketch.addExternal("body_pad_sketch", "Edge" + repr(i + 1))

        body_pocket_sketch.addGeometry([

            # Rectangle geometry
            # TODO: lines - base on centre point, parallel start lines and 90 degree angles
            # TODO: check rib variations
            Part.LineSegment(FreeCAD.Vector(-1, 1, 0), FreeCAD.Vector(1, 1, 0)),
            Part.LineSegment(FreeCAD.Vector(1, 1, 0), FreeCAD.Vector(1, -1, 0)),
            Part.LineSegment(FreeCAD.Vector(1, -1, 0), FreeCAD.Vector(-1, -1, 0)),
            Part.LineSegment(FreeCAD.Vector(-1, -1, 0), FreeCAD.Vector(-1, 1, 0))
        ], False)

        body_pocket_sketch.addConstraint([

            # Rectangle constraints
            # TODO: add constraints - base on centre point, parallel start lines and 90 degree angles
            # TODO: check rib variations
            #     # Sketcher.Constraint("Coincident", 0, 2, 1, 1),
            #     # Sketcher.Constraint("Coincident", 1, 2, 2, 1),
            #     # Sketcher.Constraint("Coincident", 2, 2, 3, 1),
            #     # Sketcher.Constraint("Coincident", 3, 2, 0, 1),
            #     # Sketcher.Constraint("Horizontal", 0),
            #     # Sketcher.Constraint("Horizontal", 2),
            #     # Sketcher.Constraint("Vertical", 1),
            #     # Sketcher.Constraint("Vertical", 3),
        ])

        body_pocket = body.newObject("PartDesign::Pocket", "body_pocket")
        body_pocket.Profile = body_pocket_sketch
        body_pocket.Reversed = True
        body_pocket.Length = (self.brick_height * DIMS_PLATE_HEIGHT) - DIMS_TOP_THICKNESS

        body_pocket_sketch.ViewObject.Visibility = False
        doc.recompute()

        # TODO: check tube variations and render

        # TODO: check tube support variations and render

        # TODO: check bottom fillet (for tiles only) and render
