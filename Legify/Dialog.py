# coding: UTF-8

from PySide import QtGui, QtCore
from Legify.Brick import *


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
        top_studs_style_combobox.setCurrentIndex(1)
        top_studs_width_count_label = QtGui.QLabel("Width Count")
        top_studs_width_count_label.setAlignment(QtCore.Qt.AlignRight)
        top_studs_width_count_label.setMinimumWidth(100)

        top_studs_width_count_spinbox = QtGui.QSpinBox()
        top_studs_width_count_spinbox.setMinimum(1)
        top_studs_width_count_spinbox.setMaximum(20)
        top_studs_width_count_spinbox.setFont(self.normal_font)
        top_studs_width_count_spinbox.setMinimumWidth(70)

        top_studs_width_count_note_label = QtGui.QLabel(u"ℹ")
        top_studs_width_count_note_label.setToolTip("1..dimensions.width")
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
        top_studs_depth_count_note_label.setToolTip("1..dimensions.depth")
        top_studs_depth_count_note_label.setFont(self.note_font)
        top_studs_depth_count_note_label.setMinimumWidth(25)

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
        top_studs_width_group_layout.addStretch(1)
        top_studs_width_group_layout.setAlignment(top_studs_width_count_label, QtCore.Qt.AlignVCenter)
        top_studs_width_group_layout.setAlignment(top_studs_width_count_spinbox, QtCore.Qt.AlignVCenter)
        top_studs_width_group_layout.setAlignment(top_studs_width_count_note_label, QtCore.Qt.AlignVCenter)

        top_studs_depth_group = QtGui.QWidget()
        top_studs_depth_group_layout = QtGui.QHBoxLayout(top_studs_depth_group)
        top_studs_depth_group_layout.setContentsMargins(0, 0, 0, 0)
        top_studs_depth_group_layout.addWidget(top_studs_depth_count_label)
        top_studs_depth_group_layout.addWidget(top_studs_depth_count_spinbox)
        top_studs_depth_group_layout.addWidget(top_studs_depth_count_note_label)
        top_studs_depth_group_layout.addSpacing(50)
        top_studs_depth_group_layout.addStretch(1)
        top_studs_depth_group_layout.setAlignment(top_studs_depth_count_label, QtCore.Qt.AlignVCenter)
        top_studs_depth_group_layout.setAlignment(top_studs_depth_count_spinbox, QtCore.Qt.AlignVCenter)
        top_studs_depth_group_layout.setAlignment(top_studs_depth_count_note_label, QtCore.Qt.AlignVCenter)

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

        return top_studs_group

    def _construct_side_studs_widgets(self):

        side_studs_style_label = QtGui.QLabel("Style")
        side_studs_style_label.setAlignment(QtCore.Qt.AlignRight)
        side_studs_style_label.setMinimumWidth(100)

        side_studs_style_combobox = QtGui.QComboBox()
        side_studs_style_combobox.addItem("None", SideStudStyle.NONE)
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
        side_studs_left_label.setMinimumWidth(80)

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
        pins_left_label.setMinimumWidth(80)

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
            ("depth_count", self.top_studs_depth_count_spinbox.value())
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

    def on_cancel_clicked(self):
        self.dialog.close()
