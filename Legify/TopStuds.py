# coding: UTF-8

from FreeCAD import Console
from Legify.Common import *


class TopStudsRenderer(object):

    def __init__(self, brick_width, brick_depth, top_stud_style, top_studs_width_count, top_studs_width_offset,
                 top_studs_depth_count, top_studs_depth_offset):
        Console.PrintMessage("TopStudsRenderer\n")

        self.doc = FreeCAD.activeDocument()
        self.body = self.doc.body

        self.width = brick_width
        self.depth = brick_depth
        self.style = top_stud_style
        self.width_count = top_studs_width_count
        self.width_offset = top_studs_width_offset
        self.depth_count = top_studs_depth_count
        self.depth_offset = top_studs_depth_offset

    def render(self):
        Console.PrintMessage("render\n")
        # TODO: render top studs

        # TODO: render pocket


