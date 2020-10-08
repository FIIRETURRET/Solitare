# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 10:51:30 2020

@author: Brandon'
"""

import arcade

class RocketEmitter(arcade.Emitter):
    """ Custom emitter class to add gravity to the emitter to represent gravity on the firework shell """
    
    def update(self):
        super().update()
        # gravity
        self.change_y += -0.05