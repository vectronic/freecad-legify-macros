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
        self.right = None
        self.pins_offset = None

        self.xy_plane = None
        self.yz_plane = None
        self.xz_plane = None
        self.front_datum_plane = None
        self.back_datum_plane = None
        self.left_datum_plane = None
        self.right_datum_plane = None

    def _render_pin_revolution(self, label, datum_point, base_plane, backwards):
        Console.PrintMessage("_render_pin_revolution({},{})\n".format(label, backwards))

        pin_revolution_sketch = self.brick.newObject("Sketcher::SketchObject", label + "_pin_revolution_sketch")
        pin_revolution_sketch.Support = [(base_plane, ''), (datum_point, '')]
        pin_revolution_sketch.MapMode = 'TangentPlane'
        pin_revolution_sketch.AttachmentOffset = Placement(Vector(0, 0, 0), Rotation(0, 90, 0))
        pin_revolution_sketch.MapReversed = backwards

        geometries = []
        constraints = []

        # construction line for rotation

        geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_top_left_vector()))
        constraints.append(Sketcher.Constraint("Horizontal", 0))

        # lines for profile

        geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_top_left_vector()))
        constraints.append(Sketcher.Constraint('Horizontal', 1))

        geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_bottom_left_vector()))
        constraints.append(Sketcher.Constraint('Vertical', 2))

        geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_top_left_vector()))
        constraints.append(Sketcher.Constraint('Horizontal', 3))

        geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_bottom_left_vector()))
        constraints.append(Sketcher.Constraint('Vertical', 4))

        geometries.append(Part.LineSegment(xy_plane_top_right_vector(), xy_plane_top_left_vector()))
        constraints.append(Sketcher.Constraint('Horizontal', 5))

        geometries.append(Part.LineSegment(xy_plane_top_left_vector(), xy_plane_bottom_left_vector()))
        constraints.append(Sketcher.Constraint('Vertical', 6))

        # constraints for profile

        constraints.append(Sketcher.Constraint("Coincident", 1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               2, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("Coincident", 2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               3, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("Coincident", 3, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               4, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("Coincident", 4, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               5, SKETCH_GEOMETRY_VERTEX_END_INDEX))
        constraints.append(Sketcher.Constraint("Coincident", 5, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               6, SKETCH_GEOMETRY_VERTEX_END_INDEX))
        constraints.append(Sketcher.Constraint("Coincident", 6, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               1, SKETCH_GEOMETRY_VERTEX_START_INDEX))

        constraints.append(Sketcher.Constraint('DistanceX',
                                               0, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               DIMS_PIN_LENGTH))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX, 0))

        # constraints for profile and construction line

        constraints.append(Sketcher.Constraint('DistanceX',
                                               1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               1, SKETCH_GEOMETRY_VERTEX_START_INDEX, DIMS_PIN_COLLAR_DEPTH))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               4, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               4, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               DIMS_PIN_OUTER_RADIUS - DIMS_PIN_INNER_RADIUS))
        constraints.append(Sketcher.Constraint('DistanceX',
                                               5, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               5, SKETCH_GEOMETRY_VERTEX_START_INDEX, DIMS_PIN_LENGTH))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               6, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               6, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               DIMS_PIN_COLLAR_RADIUS - DIMS_PIN_INNER_RADIUS))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               5, SKETCH_GEOMETRY_VERTEX_END_INDEX, DIMS_PIN_INNER_RADIUS))

        # constrain profile and construction line to datum point

        constraints.append(Sketcher.Constraint('DistanceX',
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX, 0))
        constraints.append(Sketcher.Constraint('DistanceX',
                                               1, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX, 0))

        pin_revolution_sketch.addGeometry(geometries, False)
        pin_revolution_sketch.addConstraint(constraints)

        # Set construction lines
        pin_revolution_sketch.toggleConstruction(0)

        self.doc.recompute()

        pin_revolution = self.brick.newObject("PartDesign::Revolution", label + "_pin_revolution")
        pin_revolution.Angle = 360
        pin_revolution.Profile = pin_revolution_sketch
        pin_revolution.ReferenceAxis = (pin_revolution_sketch, ['Axis0'])

        self.doc.recompute()
        pin_revolution_sketch.ViewObject.Visibility = False

        return pin_revolution

    def _render_pin_flange(self, label, base_plane, backwards):
        Console.PrintMessage("_render_pin_flange({},{})\n".format(label, backwards))

        # path for additive pipe

        pin_pipe_path_sketch = self.brick.newObject("Sketcher::SketchObject", label + "_pin_pipe_path_sketch")
        pin_pipe_path_sketch.Support = (base_plane, '')
        pin_pipe_path_sketch.MapMode = 'FlatFace'
        pin_pipe_path_sketch.MapReversed = backwards
        # note 0.005 adjustment to prevent seemingly a bug in freecad rendering
        pin_pipe_path_sketch.AttachmentOffset = Placement(Vector(0, 0,
                                                                 DIMS_PIN_LENGTH - (DIMS_PIN_FLANGE_DEPTH / 2) - 0.005),
                                                          Rotation(0, 0, 0))

        geometries = []
        constraints = []

        geometries.append(Part.Ellipse(Vector(DIMS_PIN_OUTER_RADIUS, 0, 0),
                                       Vector(0, -1 * (DIMS_PIN_OUTER_RADIUS - DIMS_PIN_FLANGE_HEIGHT), 0),
                                       Vector(0, 0, 0)))

        pin_pipe_path_sketch.addGeometry(geometries, False)
        pin_pipe_path_sketch.exposeInternalGeometry(0)

        # constrain ellipse position

        distance_x = 0
        if self.pins_offset:
            distance_x += DIMS_STUD_SPACING / 2
        if backwards:
            distance_x = -1 * distance_x

        constraints.append(Sketcher.Constraint('DistanceX',
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               distance_x))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               DIMS_TECHNIC_HOLE_CENTRE_HEIGHT))

        # constrain ellipse shape

        constraints.append(Sketcher.Constraint('Horizontal', 1))
        constraints.append(Sketcher.Constraint('Distance', 1, 2 * DIMS_PIN_OUTER_RADIUS))
        constraints.append(Sketcher.Constraint('Distance', 2, 2 * (DIMS_PIN_OUTER_RADIUS - DIMS_PIN_FLANGE_HEIGHT)))

        pin_pipe_path_sketch.addConstraint(constraints)

        self.doc.recompute()

        # profile for additive pipe

        pin_pipe_profile_sketch = self.brick.newObject("Sketcher::SketchObject",
                                                       label + "_pin_pipe_profile_sketch")
        pin_pipe_profile_sketch.Support = [(pin_pipe_path_sketch, 'Edge1')]
        pin_pipe_profile_sketch.MapMode = 'ObjectXZ'
        pin_pipe_profile_sketch.MapReversed = backwards

        geometries = []
        constraints = []

        geometries.append(Part.Ellipse(Vector(0, DIMS_PIN_FLANGE_DEPTH / 2, 0),
                                       Vector(-1 * DIMS_PIN_FLANGE_HEIGHT, 0, 0),
                                       Vector(0, 0, 0)))

        pin_pipe_profile_sketch.addGeometry(geometries, False)
        pin_pipe_profile_sketch.exposeInternalGeometry(0)

        # constrain ellipse position

        constraints.append(Sketcher.Constraint('DistanceX',
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               DIMS_PIN_OUTER_RADIUS))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               0))

        # constrain ellipse shape

        constraints.append(Sketcher.Constraint('Horizontal', 2))
        constraints.append(Sketcher.Constraint('Distance', 1, DIMS_PIN_FLANGE_DEPTH))
        constraints.append(Sketcher.Constraint('Distance', 2, DIMS_PIN_FLANGE_HEIGHT * 2))

        pin_pipe_profile_sketch.addConstraint(constraints)

        self.doc.recompute()

        # additive pipe for pin flange

        pin_pipe = self.brick.newObject("PartDesign::AdditivePipe", label + "_pin_pipe")
        pin_pipe.Profile = pin_pipe_profile_sketch
        pin_pipe.Spine = pin_pipe_path_sketch

        self.doc.recompute()

        pin_pipe_path_sketch.ViewObject.Visibility = False
        pin_pipe_profile_sketch.ViewObject.Visibility = False

        return pin_pipe

    def _render_pin_notch(self, label, datum_point, rotation):
        Console.PrintMessage("_render_pin_notch({},{})\n".format(label, rotation))

        # sketch for notch

        pin_notch_sketch = self.brick.newObject("Sketcher::SketchObject", label + "_pin_notch_sketch")
        pin_notch_sketch.Support = [(datum_point, '')]
        pin_notch_sketch.MapMode = 'Translate'
        pin_notch_sketch.AttachmentOffset = Placement(Vector(0, 0, -1 * DIMS_TECHNIC_HOLE_CENTRE_HEIGHT),
                                                      Rotation(Vector(0, 0, 0), 0))
        pin_notch_sketch.Placement = Placement(Vector(0, 0, 0), Rotation(Vector(0, 0, 1), rotation))
        pin_notch_sketch.addExternal(datum_point.Label, '')

        geometries = []
        constraints = []

        # need to position primitives roughly to ensure constraints can be solved
        y_datum = datum_point.Placement.Base.y

        geometries.append(Part.ArcOfCircle(Part.Circle(Vector(0, y_datum, 0), Vector(0, 0, 1),
                                                       DIMS_PIN_NOTCH_WIDTH / 2), 0, math.pi))
        geometries.append(Part.ArcOfCircle(Part.Circle(Vector(1, y_datum - DIMS_PIN_LENGTH, 0),
                                                       Vector(0, 0, 1), DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS),
                                           -1 * math.pi, -1 * (math.pi / 2)))
        geometries.append(Part.ArcOfCircle(Part.Circle(Vector(-1, y_datum - DIMS_PIN_LENGTH, 0),
                                                       Vector(0, 0, 1), DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS),
                                           -1 * (math.pi / 2), 0))

        geometries.append(Part.LineSegment(Vector(-1, y_datum, 0), Vector(-1, y_datum - DIMS_PIN_LENGTH, 0)))
        geometries.append(Part.LineSegment(Vector(1, y_datum, 0), Vector(1, y_datum - DIMS_PIN_LENGTH, 0)))
        geometries.append(Part.LineSegment(Vector(-1, y_datum - DIMS_PIN_LENGTH - 1, 0),
                                           Vector(1, y_datum - DIMS_PIN_LENGTH - 1, 0)))

        # connect and position notch shape

        constraints.append(Sketcher.Constraint('Radius', 0, DIMS_PIN_NOTCH_WIDTH / 2))
        constraints.append(Sketcher.Constraint('Radius', 1, DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))
        constraints.append(Sketcher.Constraint('Radius', 2, DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))

        constraints.append(Sketcher.Constraint("Horizontal", 5))
        constraints.append(Sketcher.Constraint("Vertical", 3))
        constraints.append(Sketcher.Constraint("Vertical", 4))

        constraints.append(Sketcher.Constraint('Distance', 5,
                                               DIMS_PIN_NOTCH_WIDTH + (2 * DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS)))

        distance_x = (DIMS_PIN_NOTCH_WIDTH / 2) + DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS

        if rotation < 180:
            constraints.append(Sketcher.Constraint('DistanceX',
                                                   SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                   5, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                                   distance_x))
        else:
            constraints.append(Sketcher.Constraint('DistanceX',
                                                   5, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                   SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                   distance_x))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               5, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               SKETCH_GEOMETRY_FIRST_EXTERNAL_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               DIMS_PIN_LENGTH))
        constraints.append(Sketcher.Constraint('DistanceX',
                                               SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               0))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                               SKETCH_GEOMETRY_FIRST_EXTERNAL_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               DIMS_PIN_LENGTH - DIMS_PIN_NOTCH_DEPTH))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               SKETCH_GEOMETRY_FIRST_EXTERNAL_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               DIMS_PIN_LENGTH - DIMS_PIN_NOTCH_DEPTH))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               0, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               SKETCH_GEOMETRY_FIRST_EXTERNAL_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               DIMS_PIN_LENGTH - DIMS_PIN_NOTCH_DEPTH))
        constraints.append(Sketcher.Constraint("Coincident",
                                               5, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               2, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("Coincident",
                                               5, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               1, SKETCH_GEOMETRY_VERTEX_END_INDEX))
        constraints.append(Sketcher.Constraint("Coincident",
                                               1, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               4, SKETCH_GEOMETRY_VERTEX_END_INDEX))
        constraints.append(Sketcher.Constraint("Coincident",
                                               2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               3, SKETCH_GEOMETRY_VERTEX_END_INDEX))
        constraints.append(Sketcher.Constraint("Coincident",
                                               0, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               3, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint("Coincident",
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               4, SKETCH_GEOMETRY_VERTEX_START_INDEX))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               2, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               2, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))
        constraints.append(Sketcher.Constraint('DistanceY',
                                               1, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               1, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               DIMS_PIN_NOTCH_OPENING_FILLET_RADIUS))

        pin_notch_sketch.addGeometry(geometries, False)
        pin_notch_sketch.addConstraint(constraints)

        self.doc.recompute()

        # pocket for notch

        pin_notch_pocket = self.brick.newObject("PartDesign::Pocket", label + "_pin_notch_pocket")
        pin_notch_pocket.Type = PAD_TYPE_THROUGH_ALL
        pin_notch_pocket.Profile = pin_notch_sketch
        pin_notch_pocket.Reversed = True

        self.doc.recompute()

        pin_notch_sketch.ViewObject.Visibility = False

        return pin_notch_pocket

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

    def _render_pins(self, label, base_plane, backwards, rotation, count):
        Console.PrintMessage("_render_pins({},{},{})\n".format(label, backwards, count))

        pin_centre_datum_point = self.brick.newObject('PartDesign::Point',
                                                      'pin_centre_{}_datum_point'.format(label))
        pin_centre_datum_point.Support = [(base_plane, '')]
        pin_centre_datum_point.MapMode = 'ObjectOrigin'
        pin_centre_datum_point.ViewObject.Visibility = False
        if self.pins_offset:
            pin_centre_datum_point.AttachmentOffset = Placement(Vector(DIMS_STUD_SPACING / 2,
                                                                       DIMS_TECHNIC_HOLE_CENTRE_HEIGHT, 0),
                                                                Rotation(0, 0, 0))
        else:
            pin_centre_datum_point.AttachmentOffset = Placement(Vector(0, DIMS_TECHNIC_HOLE_CENTRE_HEIGHT,
                                                                       0),
                                                                Rotation(0, 0, 0))

        pin_revolution = self._render_pin_revolution(label, pin_centre_datum_point, base_plane, backwards)

        pin_flange = self._render_pin_flange(label, base_plane, backwards)

        pin_notch_pocket = self._render_pin_notch(label, pin_centre_datum_point, rotation)

        if count > 1:
            self._render_linear_pattern(label, [pin_revolution, pin_flange, pin_notch_pocket], count)

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
        self.right = context.pins_right
        self.pins_offset = context.pins_offset

        self.xy_plane = context.xy_plane
        self.yz_plane = context.yz_plane
        self.xz_plane = context.xz_plane
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
                self._render_pins("front", self.front_datum_plane, False, 0, count)
            if self.back:
                self._render_pins("back", self.back_datum_plane, True, 180, count)
            if self.left:
                self._render_pins("left", self.left_datum_plane, True, 270, count)
            if self.right:
                self._render_pins("right", self.right_datum_plane, False, 90, count)
        else:
            if self.front:
                self._render_axles("front", False, count)
            if self.back:
                self._render_axles("back", True, count)
            if self.left:
                self._render_axles("left", False, count)
            if self.right:
                self._render_axles("right", True, count)
