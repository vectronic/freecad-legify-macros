# coding: UTF-8

from FreeCAD import Console, Placement, Rotation, Vector, activeDocument
from Legify.Body import *
from Legify.Holes import *
from Legify.Pins import *
from Legify.SideStuds import *
from Legify.TopStuds import *


class BrickContext:

    def __init__(self):
        self.width = None
        self.depth = None
        self.height = None

        self.top_studs_style = None
        self.top_studs_width_count = None
        self.top_studs_depth_count = None

        self.side_studs_style = None
        self.side_studs_front = None
        self.side_studs_back = None
        self.side_studs_left = None
        self.side_studs_right = None

        self.pins_style = None
        self.pins_front = None
        self.pins_back = None
        self.pins_left = None
        self.pins_right = None
        self.pins_offset = None

        self.hole_style = None
        self.holes_offset = None

        self.top_datum_plane = None
        self.left_datum_plane = None
        self.right_datum_plane = None
        self.front_datum_plane = None
        self.back_datum_plane = None

        self.top_inside_datum_plane = None
        self.front_inside_datum_plane = None
        self.back_inside_datum_plane = None
        self.left_inside_datum_plane = None
        self.right_inside_datum_plane = None

        self.doc = None
        self.brick = None


class BrickRenderer:

    def __init__(self, dimensions, top_studs, side_studs, pins, holes):

        try:

            self._parse_dimensions(dimensions)
            self._parse_top_studs(top_studs)
            self._parse_side_studs(side_studs)
            self._parse_pins(pins)
            self._parse_holes(holes)

        except Exception as inst:
            Console.PrintError(inst)

    def _parse_dimensions(self, dimensions):

        width = int(dimensions["width"])
        depth = int(dimensions["depth"])
        height = int(dimensions["height"])

        if depth < 1 or depth > 20:
            raise Exception("dimensions[\"depth\"] must be: 1..20")
        if width < 1 or width > 20:
            raise Exception("dimensions[\"width\"] must be: 1..20")
        if height < 1 or height > 3:
            raise Exception("dimensions[\"height\"] must be: 1..3")

        self.width = width
        self.depth = depth
        self.height = height

        Console.PrintMessage("Dimensions: {0}x{1}x{2}\n"
                             .format(self.width, self.depth, self.height))

    def _parse_top_studs(self, top_studs):

        style = top_studs["style"]

        if style not in (TopStudStyle.NONE, TopStudStyle.CLOSED, TopStudStyle.OPEN):
            raise Exception("top_studs[\"style\"] must be: TopStudStyle.NONE|TopStudStyle.CLOSED|TopStudStyle.OPEN")

        self.top_studs_style = style

        if self.top_studs_style == TopStudStyle.NONE:

            Console.PrintMessage("Top Studs: NONE\n")

        else:

            width_count = int(top_studs["width_count"])
            depth_count = int(top_studs["depth_count"])

            if width_count < 1 or width_count > self.width:
                raise Exception("top_studs[\"width_count\"] must be: 1..dimensions[\"width\"]")

            if depth_count < 1 or depth_count > self.depth:
                raise Exception("top_studs[\"depth_count\"] must be: 1..dimensions[\"depth\"]")

            self.top_studs_width_count = width_count
            self.top_studs_depth_count = depth_count

            Console.PrintMessage("Top Studs: {0} {1}x{2}\n".format(
                "CLOSED" if self.top_studs_style == TopStudStyle.CLOSED else "OPEN",
                self.top_studs_width_count,
                self.top_studs_depth_count))

    def _parse_side_studs(self, side_studs):

        style = side_studs["style"]

        if style not in (SideStudStyle.NONE, SideStudStyle.OPEN, SideStudStyle.HOLE):
            raise Exception("side_studs[\"style\"] must be: "
                            "SideStudStyle.NONE|SideStudStyle.OPEN|SideStudStyle.HOLE")

        if style != SideStudStyle.NONE and self.height < 3:
            Console.PrintMessage("side_studs[\"style\"] set to SideStudStyle.NONE as "
                                 "dimensions[\"width\"] < 3\n")
            style = SideStudStyle.NONE

        front = bool(side_studs["front"])
        back = bool(side_studs["back"])
        left = bool(side_studs["left"])
        right = bool(side_studs["right"])

        if style != SideStudStyle.NONE and not front and not back and not left and not right:

            Console.PrintMessage("side_studs[\"style\"] set to SideStudStyle.NONE as "
                                 "none of Front, Back, Left, Right are True\n")
            style = SideStudStyle.NONE

        self.side_studs_style = style

        if self.side_studs_style == SideStudStyle.NONE:

            Console.PrintMessage("Side Studs: NONE\n")

        else:

            self.side_studs_front = front
            self.side_studs_back = back
            self.side_studs_left = left
            self.side_studs_right = right

            Console.PrintMessage("Side Studs: {0} {1}{2}{3}{4}\n".format(
                "OPEN" if self.side_studs_style == SideStudStyle.OPEN else "HOLE",
                "FRONT " if self.side_studs_front else "",
                "BACK" if self.side_studs_back else "",
                "LEFT " if self.side_studs_left else "",
                "RIGHT " if self.side_studs_right else ""))

    def _parse_pins(self, pins):

        style = pins["style"]

        if style not in (PinStyle.NONE, PinStyle.PIN, PinStyle.AXLE):
            raise Exception("pins[\"style\"] must be: PinStyle.NONE|PinStyle.PIN|PinStyle.AXLE")

        if style != PinStyle.NONE and self.height < 3:
            Console.PrintMessage("pins[\"style\"] set to PinStyle.NONE as "
                                 "dimensions[\"width\"] < 3\n")
            style = PinStyle.NONE

        front = bool(pins["front"])
        back = bool(pins["back"])
        left = bool(pins["left"])
        right = bool(pins["right"])

        if style != PinStyle.NONE and self.side_studs_style != SideStudStyle.NONE:

            if front and self.side_studs_front:
                Console.PrintMessage("pins[\"front\"] set to False as "
                                     "side_studs[\"style\"] != SideStudStyle.NONE and "
                                     "side_studs[\"front\"] == True\n")
                front = False

            if back and self.side_studs_back:
                Console.PrintMessage("pins[\"back\"] set to False as "
                                     "side_studs[\"style\"] != SideStudStyle.NONE and "
                                     "side_studs[\"back\"] == True\n")
                back = False

            if left and self.side_studs_left:

                Console.PrintMessage("pins[\"left\"] set to False as "
                                     "side_studs[\"style\"] != SideStudStyle.NONE and "
                                     "side_studs[\"left\"] == True\n")
                left = False

            if right and self.side_studs_right:
                Console.PrintMessage("pins[\"right\"] set to False as "
                                     "side_studs[\"style\"] != SideStudStyle.NONE and "
                                     "side_studs[\"right\"] == True\n")
                right = False

        if style != PinStyle.NONE and not front and not back and not left and not right:

            Console.PrintMessage("pins[\"style\"] set to PinStyle.NONE as "
                                 "none of Front, Back, Left, Right are True\n")
            style = PinStyle.NONE

        offset = bool(pins["offset"])

        if offset and (left or right) and self.width == 1:

            Console.PrintMessage("pins[\"offset\"] set to False as "
                                 "Left or Right are True and dimensions[\"width\"] == 1\n")
            style = PinStyle.NONE

        if offset and (front or back) and self.depth == 1:

            Console.PrintMessage("pins[\"offset\"] set to False as "
                                 "Front or Back are True and dimensions[\"depth\"] == 1\n")
            style = PinStyle.NONE

        self.pins_style = style

        if self.pins_style == PinStyle.NONE:

            Console.PrintMessage("Pins: NONE\n")

        else:

            self.pins_front = front
            self.pins_back = back
            self.pins_left = left
            self.pins_right = right

            self.pins_offset = offset

            Console.PrintMessage("Pins: {0} {1}{2}{3}{4}{5}\n".format(
                "NONE" if self.pins_style == PinStyle.NONE else "PIN" if self.pins_style == PinStyle.PIN else "AXLE",
                "FRONT " if self.pins_front else "",
                "BACK " if self.pins_back else "",
                "LEFT " if self.pins_left else "",
                "RIGHT " if self.pins_right else "",
                "OFFSET" if self.pins_offset else ""))

    def _parse_holes(self, holes):

        style = holes["style"]

        if style not in (HoleStyle.NONE, HoleStyle.HOLE, HoleStyle.AXLE):
            raise Exception("holes[\"style\"] must be: HoleStyle.NONE|HoleStyle.HOLE|HoleStyle.AXLE")

        if style != HoleStyle.NONE and self.height < 3:
            Console.PrintMessage("holes[\"style\"] set to HoleStyle.NONE as "
                                 "dimensions[\"width\"] < 3\n")
            style = HoleStyle.NONE

        if style != HoleStyle.NONE and self.side_studs_style != SideStudStyle.NONE:

            if self.side_studs_left or self.side_studs_right:

                Console.PrintMessage("holes[\"style\"] set to HoleStyle.NONE as "
                                     "side_studs[\"style\"] != SideStudStyle.NONE and "
                                     "side_studs[\"left\"] == True or side_studs[\"right\"] == True\n")
                style = HoleStyle.NONE

        if style != HoleStyle.NONE and self.pins_style != PinStyle.NONE:

            if self.pins_left or self.pins_right:

                Console.PrintMessage("holes[\"style\"] set to HoleStyle.NONE as "
                                     "pins[\"style\"] != PinStyle.NONE and "
                                     "pins[\"left\"] == True or pins[\"right\"] == True\n")
                style = HoleStyle.NONE

        offset = bool(holes["offset"])

        if offset and self.width == 1:
            Console.PrintMessage("holes[\"offset\"] set to False as "
                                 "dimensions[\"width\"] == 1\n")
            offset = False

        self.hole_style = style

        if self.hole_style == HoleStyle.NONE:

            Console.PrintMessage("Holes: NONE\n")

        else:

            self.holes_offset = offset

            Console.PrintMessage("Holes: {0} {1}\n".format(
                "NONE" if self.hole_style == HoleStyle.NONE else "HOLE"
                if self.hole_style == HoleStyle.HOLE else "AXLE",
                "OFFSET" if self.holes_offset else ""))

    def _create_datum_planes(self, context):
        Console.PrintMessage("_create_datum_planes()\n")

        # Create top datum plane
        top_datum_plane = context.brick.newObject("PartDesign::Plane", "top_datum_plane")
        top_datum_plane.MapReversed = False
        top_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_XY_PLANE_INDEX], '')]
        top_datum_plane.MapMode = 'FlatFace'
        top_datum_plane.AttachmentOffset = Placement(Vector(0, 0, (self.height * DIMS_PLATE_HEIGHT)), Rotation(0, 0, 0))
        top_datum_plane.ViewObject.Visibility = False
        context.top_datum_plane = top_datum_plane

        # Create front datum plane
        front_datum_plane = context.brick.newObject("PartDesign::Plane", "front_datum_plane")
        front_datum_plane.MapReversed = False
        front_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_XZ_PLANE_INDEX], '')]
        front_datum_plane.MapMode = 'FlatFace'
        front_datum_plane.AttachmentOffset = Placement(Vector(0, 0, DIMS_HALF_STUD_WIDTH_OUTER), Rotation(0, 0, 0))
        front_datum_plane.ViewObject.Visibility = False
        context.front_datum_plane = front_datum_plane

        # Create back datum plane
        back_datum_plane = context.brick.newObject("PartDesign::Plane", "back_datum_plane")
        back_datum_plane.MapReversed = False
        back_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_XZ_PLANE_INDEX], '')]
        back_datum_plane.MapMode = 'FlatFace'
        back_datum_plane.AttachmentOffset = Placement(
            Vector(0, 0, -1 * (DIMS_HALF_STUD_WIDTH_OUTER + (DIMS_STUD_WIDTH_INNER * (context.depth - 1)))),
            Rotation(0, 0, 0))
        back_datum_plane.ViewObject.Visibility = False
        context.back_datum_plane = back_datum_plane

        # Create left datum plane
        left_datum_plane = context.brick.newObject("PartDesign::Plane", "left_datum_plane")
        left_datum_plane.MapReversed = False
        left_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_YZ_PLANE_INDEX], '')]
        left_datum_plane.MapMode = 'FlatFace'
        left_datum_plane.AttachmentOffset = Placement(Vector(0, 0, -1 * DIMS_HALF_STUD_WIDTH_OUTER), Rotation(0, 0, 0))
        left_datum_plane.ViewObject.Visibility = False
        context.left_datum_plane = left_datum_plane

        # Create right datum plane
        right_datum_plane = context.brick.newObject("PartDesign::Plane", "right_datum_plane")
        right_datum_plane.MapReversed = False
        right_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_YZ_PLANE_INDEX], '')]
        right_datum_plane.MapMode = 'FlatFace'
        right_datum_plane.AttachmentOffset = Placement(
            Vector(0, 0, DIMS_HALF_STUD_WIDTH_OUTER + (DIMS_STUD_WIDTH_INNER * (context.width - 1))), Rotation(0, 0, 0))
        right_datum_plane.ViewObject.Visibility = False
        context.right_datum_plane = right_datum_plane

        # Create top inside datum plane
        top_inside_datum_plane = context.brick.newObject("PartDesign::Plane", "top_inside_datum_plane")
        top_inside_datum_plane.MapReversed = False
        top_inside_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_XY_PLANE_INDEX], '')]
        top_inside_datum_plane.MapMode = 'FlatFace'
        top_inside_datum_plane.AttachmentOffset = Placement(
            Vector(0, 0, (self.height * DIMS_PLATE_HEIGHT) - DIMS_TOP_THICKNESS), Rotation(0, 0, 0))
        top_inside_datum_plane.ViewObject.Visibility = False
        context.top_inside_datum_plane = top_inside_datum_plane

        # Create front inside datum plane
        front_inside_datum_plane = context.brick.newObject("PartDesign::Plane", "front_inside_datum_plane")
        front_inside_datum_plane.MapReversed = False
        front_inside_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_XZ_PLANE_INDEX], '')]
        front_inside_datum_plane.MapMode = 'FlatFace'
        front_inside_datum_plane.AttachmentOffset = Placement(
            Vector(0, 0, DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS), Rotation(0, 0, 0))
        front_inside_datum_plane.ViewObject.Visibility = False
        context.front_inside_datum_plane = front_inside_datum_plane

        # Create back inside datum plane
        back_inside_datum_plane = context.brick.newObject("PartDesign::Plane", "back_inside_datum_plane")
        back_inside_datum_plane.MapReversed = False
        back_inside_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_XZ_PLANE_INDEX], '')]
        back_inside_datum_plane.MapMode = 'FlatFace'
        back_inside_datum_plane.AttachmentOffset = Placement(
            Vector(0, 0, -1 * ((self.depth - 1) * DIMS_STUD_WIDTH_INNER +
                   (DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS))), Rotation(0, 0, 0))
        back_inside_datum_plane.ViewObject.Visibility = False
        context.back_inside_datum_plane = back_inside_datum_plane

        # Create left inside datum plane
        left_inside_datum_plane = context.brick.newObject("PartDesign::Plane", "left_inside_datum_plane")
        left_inside_datum_plane.MapReversed = False
        left_inside_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_YZ_PLANE_INDEX], '')]
        left_inside_datum_plane.MapMode = 'FlatFace'
        left_inside_datum_plane.AttachmentOffset = Placement(
            Vector(0, 0, -1 * (DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS)), Rotation(0, 0, 0))
        left_inside_datum_plane.ViewObject.Visibility = False
        context.left_inside_datum_plane = left_inside_datum_plane

        # Create right inside datum plane
        right_inside_datum_plane = context.brick.newObject("PartDesign::Plane", "right_inside_datum_plane")
        right_inside_datum_plane.MapReversed = False
        right_inside_datum_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_YZ_PLANE_INDEX], '')]
        right_inside_datum_plane.MapMode = 'FlatFace'
        right_inside_datum_plane.AttachmentOffset = Placement(
            Vector(0, 0, (self.width - 1) * DIMS_STUD_WIDTH_INNER +
                   (DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS)), Rotation(0, 0, 0))
        right_inside_datum_plane.ViewObject.Visibility = False
        context.right_inside_datum_plane = right_inside_datum_plane

    def render(self):

        context = BrickContext()

        try:
            context.width = self.width
            context.depth = self.depth
            context.height = self.height

            context.top_studs_style = self.top_studs_style
            if self.top_studs_style != TopStudStyle.NONE:
                context.top_studs_width_count = self.top_studs_width_count
                context.top_studs_depth_count = self.top_studs_depth_count

            context.side_studs_style = self.side_studs_style
            if self.side_studs_style != SideStudStyle.NONE:
                context.side_studs_front = self.side_studs_front
                context.side_studs_back = self.side_studs_back
                context.side_studs_left = self.side_studs_left
                context.side_studs_right = self.side_studs_right

            context.pins_style = self.pins_style
            if self.pins_style != PinStyle.NONE:
                context.pins_front = self.pins_front
                context.pins_back = self.pins_back
                context.pins_left = self.pins_left
                context.pins_right = self.pins_right
                context.pins_offset = self.pins_offset

            context.hole_style = self.hole_style
            if self.hole_style != HoleStyle.NONE:
                context.holes_offset = self.holes_offset

            context.doc = activeDocument()
            context.brick = context.doc.addObject("PartDesign::Body", "brick")

            self._create_datum_planes(context)

            BodyRenderer().render(context)

            if self.top_studs_style != TopStudStyle.NONE:
                TopStudsRenderer().render(context)

            if self.side_studs_style != SideStudStyle.NONE:
                SideStudsRenderer().render(context)

            if self.pins_style != PinStyle.NONE:
                PinsRenderer().render(context)

            if self.hole_style != HoleStyle.NONE:
                HolesRenderer().render(context)

            context.brick.Tip.ViewObject.Visibility = True

        except Exception as inst:
            Console.PrintError(inst)
        finally:
            del context
