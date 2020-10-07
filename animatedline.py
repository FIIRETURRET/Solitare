# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 10:53:42 2020

@author: joutras
"""

"""
Example "Arcade" library code.

This example shows the drawing primitives and how they are used.
It does not assume the programmer knows how to define functions or classes
yet.

API documentation for the draw commands can be found here:
http://arcade.academy/quick_index.html#id1

A video explaining this example can be found here:
https://vimeo.com/167158158

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.drawing_primitives
"""

# Import the Arcade library. If this fails, then try following the instructions
# for how to install arcade:
# http://arcade.academy/installation.html
import arcade
import os
import time

# Screen title and size
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Drag and Drop Cards"

# Maximum line length size for animated line
MAX_LINE_LENGTH = 1000

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.AMAZON)
        
        # Keep track of the game's start time
        self.start_time = None
        self.current_time = None
        
        # Keep a list of points to draw lines between
        self.point_list = None
        
        # Keep track of how long our animated line should be
        self.line_length = None
        
        
    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        
        self.start_time = time.time()
        self.current_time = time.time()
        
        self.line_length = 1
        
        self.point_list = ((0, 0),
                              (0, 0),
                              )
        
    def on_update(self, dt):
        """ Update game """
        
        # Slow down the line drawing by drawing smaller lines and using the timer
        #if time.time() > self.current_time+.01:
            
        self.current_time = time.time()
        
        if self.line_length < MAX_LINE_LENGTH:
            
            self.point_list = ((0, 0),
                          (0 + self.line_length, 0 + self.line_length),
                          )
            
            self.line_length += 2
    
    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        arcade.start_render()
        
        # Draw a set of lines
        arcade.draw_text("draw_lines", 363, 405, arcade.color.BLACK, 12)
        arcade.draw_lines(self.point_list, arcade.color.BLUE, 3)
        
def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
        
