# coding: UTF-8

from FreeCAD import Console, Gui
from PySide import QtGui, QtCore
from Legify.Body import *
from Legify.Holes import *
from Legify.Pins import *
from Legify.SideStuds import *
from Legify.TopStuds import *


class BrickRenderer(object):

    def __init__(self, dimensions, top_studs, side_studs, pins, holes):

        try:
            self._parse_dimensions(dimensions)
            self._parse_top_studs(top_studs)
            self._parse_side_studs(side_studs)
            self._parse_pins(pins)
            self._parse_holes(holes)

            self.doc = FreeCAD.activeDocument()
            self.body = self.doc.addObject("PartDesign::Body", "body")

        except Exception as inst:
            Console.PrintError(inst)

    def _create_datum_planes(self):
        Console.PrintMessage("_create_datum_planes()\n")

        # Create top datum plane
        top_datum_plane = self.body.newObject("PartDesign::Plane", "top_datum_plane")
        top_datum_plane.MapReversed = False
        top_datum_plane.Support = [(self.doc.XY_Plane, '')]
        top_datum_plane.MapMode = 'FlatFace'
        top_datum_plane.AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(0, 0, (self.brick_height * DIMS_PLATE_HEIGHT)),
            FreeCAD.Rotation(0, 0, 0))
        top_datum_plane.ViewObject.Visibility = False

        # Create top inside datum plane
        top_inside_datum_plane = self.body.newObject("PartDesign::Plane", "top_inside_datum_plane")
        top_inside_datum_plane.MapReversed = False
        top_inside_datum_plane.Support = [(self.doc.XY_Plane, '')]
        top_inside_datum_plane.MapMode = 'FlatFace'
        top_inside_datum_plane.AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(0, 0, (self.brick_height * DIMS_PLATE_HEIGHT) - DIMS_TOP_THICKNESS),
            FreeCAD.Rotation(0, 0, 0))
        top_inside_datum_plane.ViewObject.Visibility = False

        # Create front inside datum plane
        front_inside_datum_plane = self.body.newObject("PartDesign::Plane", "front_inside_datum_plane")
        front_inside_datum_plane.MapReversed = False
        front_inside_datum_plane.Support = [(self.doc.XZ_Plane, '')]
        front_inside_datum_plane.MapMode = 'FlatFace'
        front_inside_datum_plane.AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(0, 0, DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS),
            FreeCAD.Rotation(0, 0, 0))
        front_inside_datum_plane.ViewObject.Visibility = False

        # Create side inside datum plane
        side_inside_datum_plane = self.body.newObject("PartDesign::Plane", "side_inside_datum_plane")
        side_inside_datum_plane.MapReversed = False
        side_inside_datum_plane.Support = [(self.doc.YZ_Plane, '')]
        side_inside_datum_plane.MapMode = 'FlatFace'
        side_inside_datum_plane.AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(0, 0, -1 * (DIMS_HALF_STUD_WIDTH_OUTER - DIMS_SIDE_THICKNESS)),
            FreeCAD.Rotation(0, 0, 0))
        side_inside_datum_plane.ViewObject.Visibility = False

    def render(self):

        try:
            self._create_datum_planes()

            BodyRenderer(self.brick_width, self.brick_depth, self.brick_height,
                         self.hole_style, False if self.hole_style == HoleStyle.NONE else self.holes_offset).render()

            if self.top_stud_style != TopStudStyle.NONE:
                TopStudsRenderer(self.brick_width, self.brick_depth, self.top_stud_style,
                                 self.top_studs_width_count, self.top_studs_width_offset,
                                 self.top_studs_depth_count, self.top_studs_depth_offset).render()

            if self.side_stud_style != SideStudStyle.NONE:
                SideStudsRenderer().render()

            if self.pin_style != PinStyle.NONE:
                PinsRenderer().render()

            if self.hole_style != HoleStyle.NONE:
                HolesRenderer().render()

            self.body.Tip.ViewObject.Visibility = True

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

        self.brick_width = width
        self.brick_depth = depth
        self.brick_height = height

        Console.PrintMessage("Dimensions: {0}x{1}x{2}\n"
                             .format(self.brick_width, self.brick_depth, self.brick_height))

    def _parse_top_studs(self, top_studs):

        style = top_studs["style"]

        if style not in (TopStudStyle.NONE, TopStudStyle.CLOSED, TopStudStyle.OPEN):
            raise Exception("top_studs[\"style\"] must be: TopStudStyle.NONE|TopStudStyle.CLOSED|TopStudStyle.OPEN")

        self.top_stud_style = style

        if self.top_stud_style == TopStudStyle.NONE:

            Console.PrintMessage("Top Studs: NONE\n")

        else:

            width_count = int(top_studs["width_count"])
            depth_count = int(top_studs["depth_count"])

            width_offset = bool(top_studs["width_offset"])
            depth_offset = bool(top_studs["depth_offset"])

            if width_offset and self.brick_width == 1:
                Console.PrintMessage("top_studs[\"width_offset\"] set to False as "
                                     "dimensions[\"width\"] == 1\n")
                width_offset = False

            if depth_offset and self.brick_depth == 1:
                Console.PrintMessage("top_studs[\"depth_offset\"] set to False as "
                                     "dimensions[\"depth\"] == 1\n")
                depth_offset = False

            if width_count < 1 or width_count > (self.brick_width - 1 if width_offset else self.brick_width):
                raise Exception("top_studs[\"width_count\"] must be: 1..dimensions[\"width\"] or "
                                "1..dimensions[\"width\"]-1 if top_studs[\"width_offset\"] == true")

            if depth_count < 1 or depth_count > (self.brick_depth - 1 if depth_offset else self.brick_depth):
                raise Exception("top_studs[\"depth_count\"] must be: 1..dimensions[\"depth\"] or "
                                "1..dimensions[\"depth\"]-1 if top_studs[\"depth_offset\"] == true")

            self.top_studs_width_count = width_count
            self.top_studs_depth_count = depth_count
            self.top_studs_width_offset = width_offset
            self.top_studs_depth_offset = depth_offset

            Console.PrintMessage("Top Studs: {0} {1}x{2} {3}{4}\n".format(
                "CLOSED" if self.top_stud_style == TopStudStyle.CLOSED else "OPEN",
                self.top_studs_width_count,
                self.top_studs_depth_count,
                "WIDTH_OFFSET" if self.top_studs_width_offset else "",
                "DEPTH_OFFSET " if self.top_studs_depth_offset else ""))

    def _parse_side_studs(self, side_studs):

        style = side_studs["style"]

        if style not in (SideStudStyle.NONE, SideStudStyle.CLOSED, SideStudStyle.OPEN, SideStudStyle.HOLE):
            raise Exception("side_studs[\"style\"] must be: "
                            "SideStudStyle.NONE|SideStudStyle.CLOSED|SideStudStyle.OPEN|SideStudStyle.HOLE")

        if style != SideStudStyle.NONE and self.brick_height < 3:
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

        self.side_stud_style = style

        if self.side_stud_style == SideStudStyle.NONE:

            Console.PrintMessage("Side Studs: NONE\n")

        else:

            self.side_studs_front = front
            self.side_studs_back = back
            self.side_studs_left = left
            self.side_studs_right = right

            Console.PrintMessage("Side Studs: {0} {1}{2}{3}{4}\n".format(
                "CLOSED" if self.side_stud_style == SideStudStyle.CLOSED else "OPEN"
                if self.side_stud_style == SideStudStyle.OPEN else "HOLE",
                "FRONT " if self.side_studs_front else "",
                "BACK" if self.side_studs_back else "",
                "LEFT " if self.side_studs_left else "",
                "RIGHT " if self.side_studs_right else ""))

    def _parse_pins(self, pins):

        style = pins["style"]

        if style not in (PinStyle.NONE, PinStyle.PIN, PinStyle.AXLE):
            raise Exception("pins[\"style\"] must be: PinStyle.NONE|PinStyle.PIN|PinStyle.AXLE")

        if style != PinStyle.NONE and self.brick_height < 3:
            Console.PrintMessage("pins[\"style\"] set to PinStyle.NONE as "
                                 "dimensions[\"width\"] < 3\n")
            style = PinStyle.NONE

        front = bool(pins["front"])
        back = bool(pins["back"])
        left = bool(pins["left"])
        right = bool(pins["right"])

        if style != PinStyle.NONE and self.side_stud_style != SideStudStyle.NONE:

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

        if offset and (left or right) and self.brick_width == 1:

            Console.PrintMessage("pins[\"offset\"] set to False as "
                                 "Left or Right are True and dimensions[\"width\"] == 1\n")
            style = PinStyle.NONE

        if offset and (front or back) and self.brick_depth == 1:

            Console.PrintMessage("pins[\"offset\"] set to False as "
                                 "Front or Back are True and dimensions[\"depth\"] == 1\n")
            style = PinStyle.NONE

        self.pin_style = style

        if self.pin_style == PinStyle.NONE:

            Console.PrintMessage("Pins: NONE\n")

        else:

            self.pins_front = front
            self.pins_back = back
            self.pins_left = left
            self.pins_right = right

            self.pins_offset = offset

            Console.PrintMessage("Pins: {0} {1}{2}{3}{4}{5}\n".format(
                "NONE" if self.pin_style == PinStyle.NONE else "PIN" if self.pin_style == PinStyle.PIN else "AXLE",
                "FRONT " if self.pins_front else "",
                "BACK " if self.pins_back else "",
                "LEFT " if self.pins_left else "",
                "RIGHT " if self.pins_right else "",
                "OFFSET" if self.pins_offset else ""))

    def _parse_holes(self, holes):

        style = holes["style"]

        if style not in (HoleStyle.NONE, HoleStyle.HOLE, HoleStyle.AXLE):
            raise Exception("holes[\"style\"] must be: HoleStyle.NONE|HoleStyle.HOLE|HoleStyle.AXLE")

        if style != HoleStyle.NONE and self.brick_height < 3:
            Console.PrintMessage("holes[\"style\"] set to HoleStyle.NONE as "
                                 "dimensions[\"width\"] < 3\n")
            style = HoleStyle.NONE

        if style != HoleStyle.NONE and self.side_stud_style != SideStudStyle.NONE:

            if self.side_studs_left or self.side_studs_right:

                Console.PrintMessage("holes[\"style\"] set to HoleStyle.NONE as "
                                     "side_studs[\"style\"] != SideStudStyle.NONE and "
                                     "side_studs[\"left\"] == True or side_studs[\"right\"] == True\n")
                style = HoleStyle.NONE

        if style != HoleStyle.NONE and self.pin_style != PinStyle.NONE:

            if self.pins_left or self.pins_right:

                Console.PrintMessage("holes[\"style\"] set to HoleStyle.NONE as "
                                     "pins[\"style\"] != PinStyle.NONE and "
                                     "pins[\"left\"] == True or pins[\"right\"] == True\n")
                style = HoleStyle.NONE

        offset = bool(holes["offset"])

        if offset and self.brick_width == 1:
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


class Dialog:

    def __init__(self):

        # Get fonts
        self.heading_font = QtGui.QLabel().font()
        self.heading_font.setBold(True)

        self.note_font = QtGui.QLabel().font()
        self.note_font.setPointSize(self.note_font.pointSize() - 3)

        self.normal_font = QtGui.QLabel().font()
        self.normal_font.setBold(False)

        # Construct dialog
        self.dialog = QtGui.QDialog()
        self.dialog.setModal(True)
        self.dialog.setWindowTitle("Legify Brick Macro")

        # Construct widgets
        box_layout = QtGui.QVBoxLayout(self.dialog)
        box_layout.addWidget(self._construct_dimensions_widgets())
        box_layout.addWidget(self._construct_top_studs_widgets())
        box_layout.addWidget(self._construct_side_studs_widgets())
        box_layout.addWidget(self._construct_pins_widgets())
        box_layout.addWidget(self._construct_holes_widgets())
        box_layout.addWidget(self._construct_button_widgets())

        # Show dialog
        self.dialog.show()
        self.dialog.exec_()

    def _construct_dimensions_widgets(self):

        dimensions_width_label = QtGui.QLabel("Width")
        dimensions_width_label.setAlignment(QtCore.Qt.AlignRight)
        dimensions_width_label.setMinimumWidth(100)

        dimensions_depth_label = QtGui.QLabel("Depth")
        dimensions_depth_label.setAlignment(QtCore.Qt.AlignRight)
        dimensions_depth_label.setMinimumWidth(100)

        dimensions_height_label = QtGui.QLabel("Height")
        dimensions_height_label.setAlignment(QtCore.Qt.AlignRight)
        dimensions_height_label.setMinimumWidth(100)

        dimensions_width_spinbox = QtGui.QSpinBox()
        dimensions_width_spinbox.setMinimum(1)
        dimensions_width_spinbox.setMaximum(20)
        dimensions_width_spinbox.setFont(self.normal_font)
        dimensions_width_spinbox.setMinimumWidth(70)

        dimensions_depth_spinbox = QtGui.QSpinBox()
        dimensions_depth_spinbox.setMinimum(1)
        dimensions_depth_spinbox.setMaximum(20)
        dimensions_depth_spinbox.setFont(self.normal_font)
        dimensions_depth_spinbox.setMinimumWidth(70)

        dimensions_height_spinbox = QtGui.QSpinBox()
        dimensions_height_spinbox.setMinimum(1)
        dimensions_height_spinbox.setMaximum(3)
        dimensions_height_spinbox.setFont(self.normal_font)
        dimensions_height_spinbox.setMinimumWidth(70)

        dimensions_width_note_label = QtGui.QLabel(u"ℹ")
        dimensions_width_note_label.setToolTip("1..20 studs")
        dimensions_width_note_label.setFont(self.note_font)
        dimensions_width_note_label.setMinimumWidth(25)

        dimensions_depth_note_label = QtGui.QLabel(u"ℹ")
        dimensions_depth_note_label.setToolTip("1..20 studs")
        dimensions_depth_note_label.setFont(self.note_font)
        dimensions_depth_note_label.setMinimumWidth(25)

        dimensions_height_note_label = QtGui.QLabel(u"ℹ")
        dimensions_height_note_label.setToolTip("1..3 plates")
        dimensions_height_note_label.setFont(self.note_font)
        dimensions_height_note_label.setMinimumWidth(25)

        dimensions_width_group = QtGui.QWidget()
        dimensions_width_group_layout = QtGui.QHBoxLayout(dimensions_width_group)
        dimensions_width_group_layout.setContentsMargins(0, 0, 0, 0)
        dimensions_width_group_layout.addWidget(dimensions_width_label)
        dimensions_width_group_layout.addWidget(dimensions_width_spinbox)
        dimensions_width_group_layout.addWidget(dimensions_width_note_label)
        dimensions_width_group_layout.addStretch(1)
        dimensions_width_group_layout.setAlignment(dimensions_width_label, QtCore.Qt.AlignVCenter)
        dimensions_width_group_layout.setAlignment(dimensions_width_spinbox, QtCore.Qt.AlignVCenter)
        dimensions_width_group_layout.setAlignment(dimensions_width_note_label, QtCore.Qt.AlignVCenter)

        dimensions_depth_group = QtGui.QWidget()
        dimensions_depth_group_layout = QtGui.QHBoxLayout(dimensions_depth_group)
        dimensions_depth_group_layout.setContentsMargins(0, 0, 0, 0)
        dimensions_depth_group_layout.addWidget(dimensions_depth_label)
        dimensions_depth_group_layout.addWidget(dimensions_depth_spinbox)
        dimensions_depth_group_layout.addWidget(dimensions_depth_note_label)
        dimensions_depth_group_layout.addStretch(1)
        dimensions_depth_group_layout.setAlignment(dimensions_depth_label, QtCore.Qt.AlignVCenter)
        dimensions_depth_group_layout.setAlignment(dimensions_depth_spinbox, QtCore.Qt.AlignVCenter)
        dimensions_depth_group_layout.setAlignment(dimensions_depth_note_label, QtCore.Qt.AlignVCenter)

        dimensions_height_group = QtGui.QWidget()
        dimensions_height_group_layout = QtGui.QHBoxLayout(dimensions_height_group)
        dimensions_height_group_layout.setContentsMargins(0, 0, 0, 0)
        dimensions_height_group_layout.addWidget(dimensions_height_label)
        dimensions_height_group_layout.addWidget(dimensions_height_spinbox)
        dimensions_height_group_layout.addWidget(dimensions_height_note_label)
        dimensions_height_group_layout.addStretch(1)
        dimensions_height_group_layout.setAlignment(dimensions_height_label, QtCore.Qt.AlignVCenter)
        dimensions_height_group_layout.setAlignment(dimensions_height_spinbox, QtCore.Qt.AlignVCenter)
        dimensions_height_group_layout.setAlignment(dimensions_height_note_label, QtCore.Qt.AlignVCenter)

        dimensions_group = QtGui.QGroupBox("Dimensions")
        dimensions_group.setFont(self.heading_font)

        dimensions_layout = QtGui.QVBoxLayout(dimensions_group)
        dimensions_layout.addWidget(dimensions_width_group)
        dimensions_layout.addWidget(dimensions_depth_group)
        dimensions_layout.addWidget(dimensions_height_group)

        # Maintain a reference to all form inputs
        self.brick_width_spinbox = dimensions_width_spinbox
        self.brick_depth_spinbox = dimensions_depth_spinbox
        self.brick_height_spinbox = dimensions_height_spinbox

        return dimensions_group

    def _construct_top_studs_widgets(self):

        top_studs_style_label = QtGui.QLabel("Style")
        top_studs_style_label.setAlignment(QtCore.Qt.AlignRight)
        top_studs_style_label.setMinimumWidth(100)

        top_studs_style_combobox = QtGui.QComboBox()
        top_studs_style_combobox.addItem("None", TopStudStyle.NONE)
        top_studs_style_combobox.addItem("Closed", TopStudStyle.CLOSED)
        top_studs_style_combobox.addItem("Open", TopStudStyle.OPEN)
        top_studs_style_combobox.setFont(self.normal_font)
        top_studs_style_combobox.setMinimumWidth(100)

        top_studs_width_count_label = QtGui.QLabel("Width Count")
        top_studs_width_count_label.setAlignment(QtCore.Qt.AlignRight)
        top_studs_width_count_label.setMinimumWidth(100)

        top_studs_width_count_spinbox = QtGui.QSpinBox()
        top_studs_width_count_spinbox.setMinimum(1)
        top_studs_width_count_spinbox.setMaximum(20)
        top_studs_width_count_spinbox.setFont(self.normal_font)
        top_studs_width_count_spinbox.setMinimumWidth(70)

        top_studs_width_count_note_label = QtGui.QLabel(u"ℹ")
        top_studs_width_count_note_label.setToolTip("1..dimensions.width\nor\n 1..dimensions.width - 1 if "
                                                    "top_studs.width_half_stud_offset == True")
        top_studs_width_count_note_label.setFont(self.note_font)
        top_studs_width_count_note_label.setMinimumWidth(25)

        top_studs_depth_count_label = QtGui.QLabel("Depth Count")
        top_studs_depth_count_label.setAlignment(QtCore.Qt.AlignRight)
        top_studs_depth_count_label.setMinimumWidth(100)

        top_studs_depth_count_spinbox = QtGui.QSpinBox()
        top_studs_depth_count_spinbox.setMinimum(1)
        top_studs_depth_count_spinbox.setMaximum(20)
        top_studs_depth_count_spinbox.setFont(self.normal_font)
        top_studs_depth_count_spinbox.setMinimumWidth(70)

        top_studs_depth_count_note_label = QtGui.QLabel(u"ℹ")
        top_studs_depth_count_note_label.setToolTip("1..dimensions.depth\nor\n 1..dimensions.depth - 1 if "
                                                    "top_studs.depth_half_stud_offset == True")
        top_studs_depth_count_note_label.setFont(self.note_font)
        top_studs_depth_count_note_label.setMinimumWidth(25)

        top_studs_width_offset_label = QtGui.QLabel(u"Width Half Stud Offset")
        top_studs_width_offset_label.setAlignment(QtCore.Qt.AlignRight)

        top_studs_width_offset_checkbox = QtGui.QCheckBox()

        top_studs_width_offset_note_label = QtGui.QLabel(u"ℹ")
        top_studs_width_offset_note_label.setToolTip("forced to False if dimensions.width == 1")
        top_studs_width_offset_note_label.setFont(self.note_font)
        top_studs_width_offset_note_label.setMinimumWidth(25)

        top_studs_depth_offset_label = QtGui.QLabel(u"Depth Half Stud Offset")
        top_studs_depth_offset_label.setAlignment(QtCore.Qt.AlignRight)

        top_studs_depth_offset_checkbox = QtGui.QCheckBox()

        top_studs_depth_offset_note_label = QtGui.QLabel(u"ℹ")
        top_studs_depth_offset_note_label.setToolTip("forced to False if dimensions.depth == 1")
        top_studs_depth_offset_note_label.setFont(self.note_font)
        top_studs_depth_offset_note_label.setMinimumWidth(25)

        top_studs_style_group = QtGui.QWidget()
        top_studs_style_group_layout = QtGui.QHBoxLayout(top_studs_style_group)
        top_studs_style_group_layout.setContentsMargins(0, 0, 0, 0)
        top_studs_style_group_layout.addWidget(top_studs_style_label)
        top_studs_style_group_layout.addWidget(top_studs_style_combobox)
        top_studs_style_group_layout.addStretch(1)
        top_studs_style_group_layout.setAlignment(top_studs_style_label, QtCore.Qt.AlignVCenter)
        top_studs_style_group_layout.setAlignment(top_studs_style_combobox, QtCore.Qt.AlignVCenter)

        top_studs_width_group = QtGui.QWidget()
        top_studs_width_group_layout = QtGui.QHBoxLayout(top_studs_width_group)
        top_studs_width_group_layout.setContentsMargins(0, 0, 0, 0)
        top_studs_width_group_layout.addWidget(top_studs_width_count_label)
        top_studs_width_group_layout.addWidget(top_studs_width_count_spinbox)
        top_studs_width_group_layout.addWidget(top_studs_width_count_note_label)
        top_studs_width_group_layout.addSpacing(50)
        top_studs_width_group_layout.addWidget(top_studs_width_offset_label)
        top_studs_width_group_layout.addWidget(top_studs_width_offset_checkbox)
        top_studs_width_group_layout.addSpacing(6)
        top_studs_width_group_layout.addWidget(top_studs_width_offset_note_label)
        top_studs_width_group_layout.addStretch(1)
        top_studs_width_group_layout.setAlignment(top_studs_width_count_label, QtCore.Qt.AlignVCenter)
        top_studs_width_group_layout.setAlignment(top_studs_width_count_spinbox, QtCore.Qt.AlignVCenter)
        top_studs_width_group_layout.setAlignment(top_studs_width_count_note_label, QtCore.Qt.AlignVCenter)
        top_studs_width_group_layout.setAlignment(top_studs_width_offset_label, QtCore.Qt.AlignVCenter)
        top_studs_width_group_layout.setAlignment(top_studs_width_offset_checkbox, QtCore.Qt.AlignVCenter)
        top_studs_width_group_layout.setAlignment(top_studs_width_offset_note_label, QtCore.Qt.AlignVCenter)

        top_studs_depth_group = QtGui.QWidget()
        top_studs_depth_group_layout = QtGui.QHBoxLayout(top_studs_depth_group)
        top_studs_depth_group_layout.setContentsMargins(0, 0, 0, 0)
        top_studs_depth_group_layout.addWidget(top_studs_depth_count_label)
        top_studs_depth_group_layout.addWidget(top_studs_depth_count_spinbox)
        top_studs_depth_group_layout.addWidget(top_studs_depth_count_note_label)
        top_studs_depth_group_layout.addSpacing(50)
        top_studs_depth_group_layout.addWidget(top_studs_depth_offset_label)
        top_studs_depth_group_layout.addWidget(top_studs_depth_offset_checkbox)
        top_studs_depth_group_layout.addSpacing(6)
        top_studs_depth_group_layout.addWidget(top_studs_depth_offset_note_label)
        top_studs_depth_group_layout.addStretch(1)
        top_studs_depth_group_layout.setAlignment(top_studs_depth_count_label, QtCore.Qt.AlignVCenter)
        top_studs_depth_group_layout.setAlignment(top_studs_depth_count_spinbox, QtCore.Qt.AlignVCenter)
        top_studs_depth_group_layout.setAlignment(top_studs_depth_count_note_label, QtCore.Qt.AlignVCenter)
        top_studs_depth_group_layout.setAlignment(top_studs_depth_offset_label, QtCore.Qt.AlignVCenter)
        top_studs_depth_group_layout.setAlignment(top_studs_depth_offset_checkbox, QtCore.Qt.AlignVCenter)
        top_studs_depth_group_layout.setAlignment(top_studs_depth_offset_note_label, QtCore.Qt.AlignVCenter)

        top_studs_group = QtGui.QGroupBox("Top Studs")
        top_studs_group.setFont(self.heading_font)

        top_studs_layout = QtGui.QVBoxLayout(top_studs_group)
        top_studs_layout.addWidget(top_studs_style_group)
        top_studs_layout.addWidget(top_studs_width_group)
        top_studs_layout.addWidget(top_studs_depth_group)

        # Maintain a reference to all form inputs
        self.top_studs_style_combobox = top_studs_style_combobox
        self.top_studs_width_count_spinbox = top_studs_width_count_spinbox
        self.top_studs_depth_count_spinbox = top_studs_depth_count_spinbox
        self.top_studs_width_offset_checkbox = top_studs_width_offset_checkbox
        self.top_studs_depth_offset_checkbox = top_studs_depth_offset_checkbox

        return top_studs_group

    def _construct_side_studs_widgets(self):

        side_studs_style_label = QtGui.QLabel("Style")
        side_studs_style_label.setAlignment(QtCore.Qt.AlignRight)
        side_studs_style_label.setMinimumWidth(100)

        side_studs_style_combobox = QtGui.QComboBox()
        side_studs_style_combobox.addItem("None", SideStudStyle.NONE)
        side_studs_style_combobox.addItem("Closed", SideStudStyle.CLOSED)
        side_studs_style_combobox.addItem("Open", SideStudStyle.OPEN)
        side_studs_style_combobox.addItem("Hole", SideStudStyle.HOLE)
        side_studs_style_combobox.setFont(self.normal_font)
        side_studs_style_combobox.setMinimumWidth(100)

        side_studs_style_note_label = QtGui.QLabel(u"ℹ")
        side_studs_style_note_label.setToolTip("forced to None if dimensions.height < 3)")
        side_studs_style_note_label.setFont(self.note_font)
        side_studs_style_note_label.setMinimumWidth(25)

        side_studs_front_label = QtGui.QLabel("Front")
        side_studs_front_label.setAlignment(QtCore.Qt.AlignRight)
        side_studs_front_label.setMinimumWidth(80)

        side_studs_front_checkbox = QtGui.QCheckBox()

        side_studs_back_label = QtGui.QLabel("Back")
        side_studs_back_label.setAlignment(QtCore.Qt.AlignRight)
        side_studs_back_label.setMinimumWidth(80)

        side_studs_back_checkbox = QtGui.QCheckBox()

        side_studs_left_label = QtGui.QLabel("Left")
        side_studs_left_label.setAlignment(QtCore.Qt.AlignRight)
        side_studs_left_label.setMinimumWidth(100)

        side_studs_left_checkbox = QtGui.QCheckBox()

        side_studs_right_label = QtGui.QLabel("Right")
        side_studs_right_label.setAlignment(QtCore.Qt.AlignRight)
        side_studs_right_label.setMinimumWidth(80)

        side_studs_right_checkbox = QtGui.QCheckBox()

        side_studs_style_group = QtGui.QWidget()
        side_studs_style_group_layout = QtGui.QHBoxLayout(side_studs_style_group)
        side_studs_style_group_layout.setContentsMargins(0, 0, 0, 0)
        side_studs_style_group_layout.addWidget(side_studs_style_label)
        side_studs_style_group_layout.addWidget(side_studs_style_combobox)
        side_studs_style_group_layout.addWidget(side_studs_style_note_label)
        side_studs_style_group_layout.addStretch(1)
        side_studs_style_group_layout.setAlignment(side_studs_style_label, QtCore.Qt.AlignVCenter)
        side_studs_style_group_layout.setAlignment(side_studs_style_combobox, QtCore.Qt.AlignVCenter)
        side_studs_style_group_layout.setAlignment(side_studs_style_note_label, QtCore.Qt.AlignVCenter)

        side_studs_location_group = QtGui.QWidget()
        side_studs_location_group_layout = QtGui.QHBoxLayout(side_studs_location_group)
        side_studs_location_group_layout.setContentsMargins(0, 0, 0, 0)
        side_studs_location_group_layout.addWidget(side_studs_front_label)
        side_studs_location_group_layout.addWidget(side_studs_front_checkbox)
        side_studs_location_group_layout.addWidget(side_studs_back_label)
        side_studs_location_group_layout.addWidget(side_studs_back_checkbox)
        side_studs_location_group_layout.addWidget(side_studs_left_label)
        side_studs_location_group_layout.addWidget(side_studs_left_checkbox)
        side_studs_location_group_layout.addWidget(side_studs_right_label)
        side_studs_location_group_layout.addWidget(side_studs_right_checkbox)
        side_studs_location_group_layout.addStretch(1)
        side_studs_location_group_layout.setAlignment(side_studs_front_label, QtCore.Qt.AlignVCenter)
        side_studs_location_group_layout.setAlignment(side_studs_front_checkbox, QtCore.Qt.AlignVCenter)
        side_studs_location_group_layout.setAlignment(side_studs_back_label, QtCore.Qt.AlignVCenter)
        side_studs_location_group_layout.setAlignment(side_studs_back_checkbox, QtCore.Qt.AlignVCenter)
        side_studs_location_group_layout.setAlignment(side_studs_left_label, QtCore.Qt.AlignVCenter)
        side_studs_location_group_layout.setAlignment(side_studs_left_checkbox, QtCore.Qt.AlignVCenter)
        side_studs_location_group_layout.setAlignment(side_studs_right_label, QtCore.Qt.AlignVCenter)
        side_studs_location_group_layout.setAlignment(side_studs_right_checkbox, QtCore.Qt.AlignVCenter)

        side_studs_group = QtGui.QGroupBox("Side Studs")
        side_studs_group.setFont(self.heading_font)

        side_studs_layout = QtGui.QVBoxLayout(side_studs_group)
        side_studs_layout.addWidget(side_studs_style_group)
        side_studs_layout.addWidget(side_studs_location_group)

        # Maintain a reference to all form inputs
        self.side_studs_style_combobox = side_studs_style_combobox
        self.side_studs_front_checkbox = side_studs_front_checkbox
        self.side_studs_back_checkbox = side_studs_back_checkbox
        self.side_studs_left_checkbox = side_studs_left_checkbox
        self.side_studs_right_checkbox = side_studs_right_checkbox

        return side_studs_group

    def _construct_pins_widgets(self):

        pins_style_label = QtGui.QLabel("Style")
        pins_style_label.setAlignment(QtCore.Qt.AlignRight)
        pins_style_label.setMinimumWidth(100)

        pins_style_combobox = QtGui.QComboBox()
        pins_style_combobox.addItem("None", PinStyle.NONE)
        pins_style_combobox.addItem("Pin", PinStyle.PIN)
        pins_style_combobox.addItem("Axle", PinStyle.AXLE)
        pins_style_combobox.setFont(self.normal_font)
        pins_style_combobox.setMinimumWidth(100)

        pins_style_note_label = QtGui.QLabel(u"ℹ")
        pins_style_note_label.setToolTip("forced to None if conflicting with side_studs\nor if dimensions.height < 3")
        pins_style_note_label.setFont(self.note_font)
        pins_style_note_label.setMinimumWidth(25)

        pins_front_label = QtGui.QLabel("Front")
        pins_front_label.setAlignment(QtCore.Qt.AlignRight)
        pins_front_label.setMinimumWidth(80)

        pins_front_checkbox = QtGui.QCheckBox()

        pins_back_label = QtGui.QLabel("Back")
        pins_back_label.setAlignment(QtCore.Qt.AlignRight)
        pins_back_label.setMinimumWidth(80)

        pins_back_checkbox = QtGui.QCheckBox()

        pins_left_label = QtGui.QLabel("Left")
        pins_left_label.setAlignment(QtCore.Qt.AlignRight)
        pins_left_label.setMinimumWidth(100)

        pins_left_checkbox = QtGui.QCheckBox()

        pins_right_label = QtGui.QLabel("Right")
        pins_right_label.setAlignment(QtCore.Qt.AlignRight)
        pins_right_label.setMinimumWidth(80)

        pins_right_checkbox = QtGui.QCheckBox()

        pins_offset_label = QtGui.QLabel("Half Stud Offset")
        pins_offset_label.setAlignment(QtCore.Qt.AlignRight)

        pins_offset_checkbox = QtGui.QCheckBox()

        pins_offset_note_label = QtGui.QLabel(u"ℹ")
        pins_offset_note_label.setToolTip("ignored for left/right if dimensions.width == 1 \n"
                                          "ignored for front/back if dimensions.depth == 1")
        pins_offset_note_label.setFont(self.note_font)
        pins_offset_note_label.setMinimumWidth(25)

        pins_style_group = QtGui.QWidget()
        pins_style_group_layout = QtGui.QHBoxLayout(pins_style_group)
        pins_style_group_layout.setContentsMargins(0, 0, 0, 0)
        pins_style_group_layout.addWidget(pins_style_label)
        pins_style_group_layout.addWidget(pins_style_combobox)
        pins_style_group_layout.addWidget(pins_style_note_label)
        pins_style_group_layout.addStretch(1)
        pins_style_group_layout.setAlignment(pins_style_label, QtCore.Qt.AlignVCenter)
        pins_style_group_layout.setAlignment(pins_style_combobox, QtCore.Qt.AlignVCenter)
        pins_style_group_layout.setAlignment(pins_style_note_label, QtCore.Qt.AlignVCenter)

        pins_location_group = QtGui.QWidget()
        pins_location_group_layout = QtGui.QHBoxLayout(pins_location_group)
        pins_location_group_layout.setContentsMargins(0, 0, 0, 0)
        pins_location_group_layout.addWidget(pins_front_label)
        pins_location_group_layout.addWidget(pins_front_checkbox)
        pins_location_group_layout.addWidget(pins_back_label)
        pins_location_group_layout.addWidget(pins_back_checkbox)
        pins_location_group_layout.addWidget(pins_left_label)
        pins_location_group_layout.addWidget(pins_left_checkbox)
        pins_location_group_layout.addWidget(pins_right_label)
        pins_location_group_layout.addWidget(pins_right_checkbox)
        pins_location_group_layout.addStretch(1)
        pins_location_group_layout.setAlignment(pins_front_label, QtCore.Qt.AlignVCenter)
        pins_location_group_layout.setAlignment(pins_front_checkbox, QtCore.Qt.AlignVCenter)
        pins_location_group_layout.setAlignment(pins_back_label, QtCore.Qt.AlignVCenter)
        pins_location_group_layout.setAlignment(pins_back_checkbox, QtCore.Qt.AlignVCenter)
        pins_location_group_layout.setAlignment(pins_left_label, QtCore.Qt.AlignVCenter)
        pins_location_group_layout.setAlignment(pins_left_checkbox, QtCore.Qt.AlignVCenter)
        pins_location_group_layout.setAlignment(pins_right_label, QtCore.Qt.AlignVCenter)
        pins_location_group_layout.setAlignment(pins_right_checkbox, QtCore.Qt.AlignVCenter)

        pins_offset_group = QtGui.QWidget()
        pins_offset_group_layout = QtGui.QHBoxLayout(pins_offset_group)
        pins_offset_group_layout.setContentsMargins(0, 0, 0, 0)
        pins_offset_group_layout.addWidget(pins_offset_label)
        pins_offset_group_layout.addWidget(pins_offset_checkbox)
        pins_offset_group_layout.addSpacing(6)
        pins_offset_group_layout.addWidget(pins_offset_note_label)
        pins_offset_group_layout.addStretch(1)
        pins_offset_group_layout.setAlignment(pins_offset_label, QtCore.Qt.AlignVCenter)
        pins_offset_group_layout.setAlignment(pins_offset_checkbox, QtCore.Qt.AlignVCenter)
        pins_offset_group_layout.setAlignment(pins_offset_note_label, QtCore.Qt.AlignVCenter)

        pins_group = QtGui.QGroupBox("Pins")
        pins_group.setFont(self.heading_font)

        pins_layout = QtGui.QVBoxLayout(pins_group)
        pins_layout.addWidget(pins_style_group)
        pins_layout.addWidget(pins_location_group)
        pins_layout.addWidget(pins_offset_group)

        # Maintain a reference to all form inputs
        self.pins_style_combobox = pins_style_combobox
        self.pins_front_checkbox = pins_front_checkbox
        self.pins_back_checkbox = pins_back_checkbox
        self.pins_left_checkbox = pins_left_checkbox
        self.pins_right_checkbox = pins_right_checkbox
        self.pins_offset_checkbox = pins_offset_checkbox

        return pins_group

    def _construct_holes_widgets(self):

        holes_style_label = QtGui.QLabel("Style")
        holes_style_label.setAlignment(QtCore.Qt.AlignRight)
        holes_style_label.setMinimumWidth(100)

        holes_style_note_label = QtGui.QLabel(u"ℹ")
        holes_style_note_label.setFont(self.note_font)
        holes_style_note_label.setToolTip(
            "forced to None if conflicting with side_studs or pins\nor\nif dimensions.height < 3")
        holes_style_note_label.setMinimumWidth(25)

        holes_offset_label = QtGui.QLabel("Half Stud Offset")
        holes_offset_label.setAlignment(QtCore.Qt.AlignRight)
        holes_offset_label.setMinimumWidth(100)

        holes_offset_note_label = QtGui.QLabel(u"ℹ")
        holes_offset_note_label.setFont(self.note_font)
        holes_offset_note_label.setToolTip("ignored if dimensions.width == 1")
        holes_offset_note_label.setMinimumWidth(25)

        holes_style_combobox = QtGui.QComboBox()
        holes_style_combobox.addItem("None", HoleStyle.NONE)
        holes_style_combobox.addItem("Hole", HoleStyle.HOLE)
        holes_style_combobox.addItem("Axle", HoleStyle.AXLE)
        holes_style_combobox.setFont(self.normal_font)
        holes_style_combobox.setMinimumWidth(100)

        holes_offset_checkbox = QtGui.QCheckBox()

        holes_style_group = QtGui.QWidget()
        holes_style_group_layout = QtGui.QHBoxLayout(holes_style_group)
        holes_style_group_layout.setContentsMargins(0, 0, 0, 0)
        holes_style_group_layout.addWidget(holes_style_label)
        holes_style_group_layout.addWidget(holes_style_combobox)
        holes_style_group_layout.addWidget(holes_style_note_label)
        holes_style_group_layout.addStretch(1)
        holes_style_group_layout.setAlignment(holes_style_label, QtCore.Qt.AlignVCenter)
        holes_style_group_layout.setAlignment(holes_style_combobox, QtCore.Qt.AlignVCenter)
        holes_style_group_layout.setAlignment(holes_style_note_label, QtCore.Qt.AlignVCenter)

        holes_offset_group = QtGui.QWidget()
        holes_offset_group_layout = QtGui.QHBoxLayout(holes_offset_group)
        holes_offset_group_layout.setContentsMargins(0, 0, 0, 0)
        holes_offset_group_layout.addWidget(holes_offset_label)
        holes_offset_group_layout.addWidget(holes_offset_checkbox)
        holes_offset_group_layout.addSpacing(6)
        holes_offset_group_layout.addWidget(holes_offset_note_label)
        holes_offset_group_layout.addStretch(1)
        holes_offset_group_layout.setAlignment(holes_offset_label, QtCore.Qt.AlignVCenter)
        holes_offset_group_layout.setAlignment(holes_offset_checkbox, QtCore.Qt.AlignVCenter)
        holes_offset_group_layout.setAlignment(holes_offset_note_label, QtCore.Qt.AlignVCenter)

        holes_group = QtGui.QGroupBox("Holes")
        holes_group.setFont(self.heading_font)

        holes_layout = QtGui.QVBoxLayout(holes_group)
        holes_layout.addWidget(holes_style_group)
        holes_layout.addWidget(holes_offset_group)

        # Maintain a reference to all form inputs
        self.holes_style_combobox = holes_style_combobox
        self.holes_offset_checkbox = holes_offset_checkbox

        return holes_group

    def _construct_button_widgets(self):

        buttons = QtGui.QDialogButtonBox()
        buttons.setOrientation(QtCore.Qt.Horizontal)
        buttons.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.on_ok_clicked)
        buttons.rejected.connect(self.on_cancel_clicked)

        return buttons

    def on_ok_clicked(self):
        self.dialog.close()

        dimensions = dict([
            ("width", self.brick_width_spinbox.value()),
            ("depth", self.brick_depth_spinbox.value()),
            ("height", self.brick_height_spinbox.value())
        ])

        top_studs = dict([
            ("style", self.top_studs_style_combobox.itemData(self.top_studs_style_combobox.currentIndex())),
            ("width_count", self.top_studs_width_count_spinbox.value()),
            ("depth_count", self.top_studs_depth_count_spinbox.value()),
            ("width_offset", self.top_studs_width_offset_checkbox.isChecked()),
            ("depth_offset", self.top_studs_depth_offset_checkbox.isChecked())
        ])

        side_studs = dict([
            ("style", self.side_studs_style_combobox.itemData(self.side_studs_style_combobox.currentIndex())),
            ("front", self.side_studs_front_checkbox.isChecked()),
            ("back", self.side_studs_back_checkbox.isChecked()),
            ("left", self.side_studs_left_checkbox.isChecked()),
            ("right", self.side_studs_right_checkbox.isChecked())
        ])

        pins = dict([
            ("style", self.pins_style_combobox.itemData(self.pins_style_combobox.currentIndex())),
            ("front", self.pins_front_checkbox.isChecked()),
            ("back", self.pins_back_checkbox.isChecked()),
            ("left", self.pins_left_checkbox.isChecked()),
            ("right", self.pins_right_checkbox.isChecked()),
            ("offset", self.pins_offset_checkbox.isChecked()),
        ])

        holes = dict([
            ("style", self.holes_style_combobox.itemData(self.holes_style_combobox.currentIndex())),
            ("offset", self.holes_offset_checkbox.isChecked()),
        ])

        BrickRenderer(dimensions, top_studs, side_studs, pins, holes).render()

        Gui.activeDocument().activeView().viewAxonometric()
        Gui.SendMsgToActiveView("ViewFit")

    def on_cancel_clicked(self):
        self.dialog.close()
