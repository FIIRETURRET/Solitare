# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 18:26:00 2020

@author: Brandon'
"""

from array import array
from dataclasses import dataclass, field
import arcade
import arcade.gl
import time
import random

from Line import Line

@dataclass
class Burst:
    """ Track for each Burst """
    buffer: arcade.gl.Buffer
    vao: arcade.gl.Geometry
    start_time: float
    
    point: (int, int)
    line: Line = field(default=None)
    
    def __post_init__(self):
        self.line = Line(self.point[0], self.point[1], 2)
    