# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 14:46:23 2020

@author: Brandon'
"""

import arcade

# Face down image
FACE_DOWN_IMAGE = ":resources:images/cards/cardBack_red2.png"

class Card(arcade.Sprite):
    """ Card sprite """

    def __init__(self, suit, value, scale=1):
        """ Card constructor """

        # Attributes for suit and value
        self.suit = suit
        self.value = value

        # Image to use for the sprite when face up
        self.image_file_name = f"resources/images/cards/card{self.suit}{self.value}.png"
        self.is_face_up = False

        # Call the parent
        super().__init__(FACE_DOWN_IMAGE, scale)
        
    def face_down(self):
        """ Turn card face-down """
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE)
        self.is_face_up = False
        
    def face_up(self):
        """ Turn card face-up """
        self.texture = arcade.load_texture(self.image_file_name)
        self.is_face_up = True
        
    @property
    def is_face_down(self):
        """ is this card face down? """
        return not self.is_face_up