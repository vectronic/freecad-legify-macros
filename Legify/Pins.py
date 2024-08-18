# coding: UTF-8

from FreeCAD import Console, Placement, Rotation, Vector
from Legify.Common import *
import Part
import Sketcher


class PinsRenderer:

    def __init__(self):
        Console.PrintMessage("PinsRenderer\n")

        self.doc = None
        self.brick = None

        self.width = None
        self.depth = None
        self.style = None
        self.front = None
        self.back = None
        self.left = None
        self.right = None
        self.pins_offset = None

        self.front_datum_plane = None
        self.back_datum_plane = None
        self.left_datum_plane = None
        self.right_datum_plane = None

    def _render_linear_pattern(self, label, features, count):
        Console.PrintMessage("_render_linear_pattern({}, {})\n".format(label, count))

        # do not use self.brick.newObject("PartDesign::LinearPattern", label + "_pin_linear_pattern") here as the
        # brick.Tip will not be updated
        pin_linear_pattern = self.doc.addObject("PartDesign::LinearPattern", label + "_pin_linear_pattern")

        pin_linear_pattern.Originals = features
        pin_linear_pattern.Direction = (features[0].Profile[0], ['N_Axis'])
        pin_linear_pattern.Length = DIMS_STUD_SPACING * (count - 1)
        pin_linear_pattern.Occurrences = count
        if label == 'back' or label == 'left':
            pin_linear_pattern.Reversed = True
        self.brick.addObject(pin_linear_pattern)

        self.doc.recompute()

    def _render_pins(self, label, base_plane, backwards, count):
        Console.PrintMessage("_render_pins({},{},{})\n".format(label, backwards, count))

        pin_base_datum_point = self.brick.newObject('PartDesign::Point',
                                                    'pin_base_{}_datum_point'.format(label))
        pin_base_datum_point.AttachmentSupport = [(base_plane, '')]
        pin_base_datum_point.MapMode = 'ObjectOrigin'
        pin_base_datum_point.ViewObject.Visibility = False
        if self.pins_offset:
            pin_base_datum_point.AttachmentOffset = Placement(Vector(DIMS_STUD_SPACING / 2,
                                                                     DIMS_TECHNIC_HOLE_CENTRE_HEIGHT, 0),
                                                              Rotation(0, 0, 0))
        else:
            pin_base_datum_point.AttachmentOffset = Placement(Vector(0, DIMS_TECHNIC_HOLE_CENTRE_HEIGHT, 0),
                                                              Rotation(0, 0, 0))

        pin_tip_offset = DIMS_PIN_LENGTH
        if backwards:
            pin_tip_offset *= -1

        pin_tip_datum_point = self.brick.newObject('PartDesign::Point',
                                                   'pin_tip_{}_datum_point'.format(label))
        pin_tip_datum_point.AttachmentSupport = [(base_plane, '')]
        pin_tip_datum_point.MapMode = 'ObjectOrigin'
        pin_tip_datum_point.ViewObject.Visibility = False
        if self.pins_offset:
            pin_tip_datum_point.AttachmentOffset = Placement(Vector(DIMS_STUD_SPACING / 2,
                                                                    DIMS_TECHNIC_HOLE_CENTRE_HEIGHT, pin_tip_offset),
                                                             Rotation(0, 0, 0))
        else:
            pin_tip_datum_point.AttachmentOffset = Placement(Vector(0, DIMS_TECHNIC_HOLE_CENTRE_HEIGHT, pin_tip_offset),
                                                             Rotation(0, 0, 0))

        pin_datum_line = self.brick.newObject('PartDesign::Line', 'pin_{}_datum_line'.format(label))
        pin_datum_line.AttachmentSupport = [(pin_base_datum_point, ''), (pin_tip_datum_point, '')]
        pin_datum_line.MapMode = 'TwoPointLine'
        pin_datum_line.ViewObject.Visibility = False

        pin_features = render_pin(label, pin_datum_line, self.brick, self.doc)

        if count > 1:
            self._render_linear_pattern(label, pin_features, count)

    def _render_axles(self, label, backwards, count):
        Console.PrintMessage("_render_axles({},{},{})\n".format(label, backwards, count))
        # TODO: implement axle pin

    def render(self, context):
        Console.PrintMessage("render\n")

        self.doc = context.doc
        self.brick = context.brick

        self.width = context.width
        self.depth = context.depth
        self.style = context.pins_style
        self.front = context.pins_front
        self.back = context.pins_back
        self.left = context.pins_left
        self.right = context.pins_right
        self.pins_offset = context.pins_offset

        self.front_datum_plane = context.front_datum_plane
        self.back_datum_plane = context.back_datum_plane
        self.left_datum_plane = context.left_datum_plane
        self.right_datum_plane = context.right_datum_plane

        if self.front or self.back:
            count = self.width
        else:
            count = self.depth

        if self.pins_offset:
            count = count - 1

        if self.style == PinStyle.PIN:
            if self.front:
                self._render_pins("front", self.front_datum_plane, False, count)
            if self.back:
                self._render_pins("back", self.back_datum_plane, True, count)
            if self.left:
                self._render_pins("left", self.left_datum_plane, True, count)
            if self.right:
                self._render_pins("right", self.right_datum_plane, False, count)
        else:
            if self.front:
                self._render_axles("front", False, count)
            if self.back:
                self._render_axles("back", True, count)
            if self.left:
                self._render_axles("left", False, count)
            if self.right:
                self._render_axles("right", True, count)
