# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 18:26:00 2020

@author: Brandon'
"""

from array import array
from dataclasses import dataclass
import arcade
import arcade.gl
import time
import random

@dataclass
class Burst:
    """ Track for each Burst """
    buffer: arcade.gl.Buffer
    vao: arcade.gl.Geometry
    start_time: float