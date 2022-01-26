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

    def _render_pin_revolution(self, label, datum_point, revolution_sketch_plane, backwards):
        Console.PrintMessage("_render_pin_revolution({},{})\n".format(label, backwards))

        pin_revolution_sketch = self.brick.newObject("Sketcher::SketchObject", label + "_pin_revolution_sketch")
        pin_revolution_sketch.Support = (revolution_sketch_plane, '')
        pin_revolution_sketch.MapMode = 'FlatFace'
        pin_revolution_sketch.MapReversed = backwards
        pin_revolution_sketch.addExternal(datum_point.Label, '')

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
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               DIMS_TECHNIC_HOLE_CENTRE_HEIGHT))

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
                                               5, SKETCH_GEOMETRY_VERTEX_END_INDEX,
                                               DIMS_TECHNIC_HOLE_CENTRE_HEIGHT + DIMS_PIN_INNER_RADIUS))

        # constrain profile and construction line to datum point

        constraints.append(Sketcher.Constraint('DistanceX',
                                               0, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               SKETCH_GEOMETRY_FIRST_EXTERNAL_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, 0))
        constraints.append(Sketcher.Constraint('DistanceX',
                                               1, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                               SKETCH_GEOMETRY_FIRST_EXTERNAL_INDEX,
                                               SKETCH_GEOMETRY_VERTEX_START_INDEX, 0))

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
        if self.pins_offset:
            distance_x += DIMS_STUD_SPACING / 2

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
        if self.pins_offset:
            if rotation < 180:
                constraints.append(Sketcher.Constraint('DistanceX',
                                                       SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                       0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                                       DIMS_STUD_SPACING / 2))
            else:
                constraints.append(Sketcher.Constraint('DistanceX',
                                                       0, SKETCH_GEOMETRY_VERTEX_CENTRE_INDEX,
                                                       SKETCH_GEOMETRY_ORIGIN_INDEX, SKETCH_GEOMETRY_VERTEX_START_INDEX,
                                                       DIMS_STUD_SPACING / 2))
        else:
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

    def _render_pins(self, label, datum_point, revolution_sketch_plane, base_plane, revolution_backwards,
                     flange_backwards, rotation, count):
        Console.PrintMessage("_render_pins({},{},{},{})\n".format(label, revolution_backwards, flange_backwards, count))

        pin_revolution = self._render_pin_revolution(label, datum_point, revolution_sketch_plane, revolution_backwards)

        pin_flange = self._render_pin_flange(label, base_plane, flange_backwards)

        pin_notch_pocket = self._render_pin_notch(label, datum_point, rotation)

        if count > 1:
            self._render_linear_pattern(label, [pin_revolution, pin_flange, pin_notch_pocket], count)

    def _render_axles(self, label, revolution_sketch_plane, backwards, count):
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
            if self.pins_offset:
                revolution_sketch_plane = context.brick.newObject("PartDesign::Plane",
                                                                  "pin_profile_front_sketch_plane")
                revolution_sketch_plane.MapReversed = False
                revolution_sketch_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_YZ_PLANE_INDEX], '')]
                revolution_sketch_plane.MapMode = 'FlatFace'
                revolution_sketch_plane.AttachmentOffset = Placement(Vector(0, 0, DIMS_STUD_SPACING / 2),
                                                                     Rotation(0, 0, 0))
                revolution_sketch_plane.ViewObject.Visibility = False

                count = self.width - 1
            else:
                revolution_sketch_plane = self.yz_plane

                count = self.width

            if self.front:
                if self.style == PinStyle.PIN:
                    notch_datum_point = context.brick.newObject('PartDesign::Point',
                                                                'pin_notch_front_datum_point')
                    notch_datum_point.Support = [(self.front_datum_plane, '')]
                    notch_datum_point.MapMode = 'ObjectOrigin'
                    notch_datum_point.ViewObject.Visibility = False

                    self._render_pins("front", notch_datum_point, revolution_sketch_plane, self.front_datum_plane,
                                      False, False, 0, count)
                else:
                    self._render_axles("front", revolution_sketch_plane, False, count)

            if self.back:
                if self.style == PinStyle.PIN:
                    notch_datum_point = context.brick.newObject('PartDesign::Point',
                                                                'pin_notch_back_datum_point')
                    notch_datum_point.Support = [(self.back_datum_plane, '')]
                    notch_datum_point.MapMode = 'ObjectOrigin'
                    notch_datum_point.ViewObject.Visibility = False

                    self._render_pins("back", notch_datum_point, revolution_sketch_plane, self.back_datum_plane,
                                      True, True, 180, count)
                else:
                    self._render_axles("back", revolution_sketch_plane, True, count)

        if self.left or self.right:
            if self.pins_offset:
                revolution_sketch_plane = context.brick.newObject("PartDesign::Plane",
                                                                  "pin_profile_left_sketch_plane")
                revolution_sketch_plane.MapReversed = False
                revolution_sketch_plane.Support = [(context.brick.Origin.OriginFeatures[ORIGIN_XZ_PLANE_INDEX], '')]
                revolution_sketch_plane.MapMode = 'FlatFace'
                revolution_sketch_plane.AttachmentOffset = Placement(
                    Vector(0, 0, -1 * (DIMS_STUD_SPACING / 2)), Rotation(0, 0, 0))
                revolution_sketch_plane.ViewObject.Visibility = False

                count = self.depth - 1
            else:
                revolution_sketch_plane = self.xz_plane

                count = self.depth

            if self.left:
                if self.style == PinStyle.PIN:
                    notch_datum_point = context.brick.newObject('PartDesign::Point',
                                                                'pin_notch_left_datum_point')
                    notch_datum_point.Support = [(self.left_datum_plane, '')]
                    notch_datum_point.MapMode = 'ObjectOrigin'
                    notch_datum_point.ViewObject.Visibility = False

                    self._render_pins("left", notch_datum_point, revolution_sketch_plane, self.left_datum_plane,
                                      False, True, 270, count)
                else:
                    self._render_axles("left", revolution_sketch_plane, False, count)

            if self.right:
                if self.style == PinStyle.PIN:
                    notch_datum_point = context.brick.newObject('PartDesign::Point',
                                                                'pin_notch_right_datum_point')
                    notch_datum_point.Support = [(self.right_datum_plane, '')]
                    notch_datum_point.MapMode = 'ObjectOrigin'
                    notch_datum_point.ViewObject.Visibility = False

                    self._render_pins("right", notch_datum_point, revolution_sketch_plane, self.right_datum_plane,
                                      True, False, 90, count)
                else:
                    self._render_axles("right", revolution_sketch_plane, True, count)
