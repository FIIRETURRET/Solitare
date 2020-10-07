# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 12:52:44 2020

@author: joutras
"""

import math

class Line():
    def __init__(self, start_point, end_point, speed):
        """ Line constructor """
        self.start_point = start_point
        self.end_point = end_point
        self.speed = speed
        
        self.draw = True
            