# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 14:47:34 2020
@author: Brandon'
"""

from arcade.utils import _Vec2  # bring in "private" class
import arcade
import random
import arcade.gl
import time
import pyglet

from Card import Card
from RocketEmitter import RocketEmitter
from AnimatedAlphaParticle import AnimatedAlphaParticle


# Screen title and size
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Drag and Drop Cards"

# Constants for sizing
CARD_SCALE = 0.6

# How big are the cards?
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

# How big is the mat we'll place the card on?
MAT_PERCENT_OVERSIZE = 1.25
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)

# How much space do we leave as a gap between the mats?
# Done as a percent of the mat size.
VERTICAL_MARGIN_PERCENT = 0.10
HORIZONTAL_MARGIN_PERCENT = 0.10

# The Y of the bottom row (2 piles)
BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The X of where to start putting things on the left side
START_X = MAT_WIDTH / 2 + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# The Y of the top row (4 piles)
TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The Y of the middle row (7 piles)
MIDDLE_Y = TOP_Y - MAT_HEIGHT - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# How far apart each pile goes
X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# Card constants
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]

# If we fan out cards stacked on each other, how far apart to fan them?
CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3

# Constants that represent "what pile is what" for the game
PILE_COUNT = 13
BOTTOM_FACE_DOWN_PILE = 0
BOTTOM_FACE_UP_PILE = 1
PLAY_PILE_1 = 2
PLAY_PILE_2 = 3
PLAY_PILE_3 = 4
PLAY_PILE_4 = 5
PLAY_PILE_5 = 6
PLAY_PILE_6 = 7
PLAY_PILE_7 = 8
TOP_PILE_1 = 9
TOP_PILE_2 = 10
TOP_PILE_3 = 11
TOP_PILE_4 = 12

ROCKET_SMOKE_TEXTURE = arcade.make_soft_circle_texture(15, arcade.color.GRAY)
FLASH_TEXTURE = arcade.make_soft_circle_texture(70, (128, 128, 90))
PUFF_TEXTURE = arcade.make_soft_circle_texture(80, (40, 40, 40))
CLOUD_TEXTURES = [
    arcade.make_soft_circle_texture(50, arcade.color.WHITE),
    arcade.make_soft_circle_texture(50, arcade.color.LIGHT_GRAY),
    arcade.make_soft_circle_texture(50, arcade.color.LIGHT_BLUE),
]
STAR_TEXTURES = [
    arcade.make_soft_circle_texture(8, arcade.color.WHITE),
    arcade.make_soft_circle_texture(8, arcade.color.PASTEL_YELLOW),
]
LAUNCH_INTERVAL_MIN = 0.2
LAUNCH_INTERVAL_MAX = 1.0
RAINBOW_COLORS = (
    arcade.color.ELECTRIC_CRIMSON,
    arcade.color.FLUORESCENT_ORANGE,
    arcade.color.ELECTRIC_YELLOW,
    arcade.color.ELECTRIC_GREEN,
    arcade.color.ELECTRIC_CYAN,
    arcade.color.MEDIUM_ELECTRIC_BLUE,
    arcade.color.ELECTRIC_INDIGO,
    arcade.color.ELECTRIC_PURPLE,
)
SPARK_TEXTURES = [arcade.make_circle_texture(8, clr) for clr in RAINBOW_COLORS]
SPARK_PAIRS = [
    [SPARK_TEXTURES[0], SPARK_TEXTURES[3]],
    [SPARK_TEXTURES[1], SPARK_TEXTURES[5]],
    [SPARK_TEXTURES[7], SPARK_TEXTURES[2]],
]
SPINNER_HEIGHT = 75


def make_spinner():
    spinner = arcade.Emitter(
        center_xy=(SCREEN_WIDTH / 2, SPINNER_HEIGHT - 5),
        emit_controller=arcade.EmitterIntervalWithTime(0.025, 2.0),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=random.choice(STAR_TEXTURES),
            change_xy=(0, 6.0),
            lifetime=0.2
        )
    )
    spinner.change_angle = 16.28
    return spinner

def make_rocket(emit_done_cb):
    """ Emitter that displays the smoke trail as the firework shell climbs into the sky """
    rocket = RocketEmitter(
            center_xy = ( random.uniform(100, SCREEN_WIDTH - 100), 25),
            emit_controller=arcade.EmitterIntervalWithTime(0.04, 2.0),
            particle_factory=lambda emitter: arcade.FadeParticle(
                    filename_or_texture=ROCKET_SMOKE_TEXTURE,
                    change_xy=arcade.rand_in_circle((0.0, 0.0), 0.08),
                    scale=0.5,
                    lifetime=random.uniform(1.0, 1.5),
                    start_alpha=100,
                    end_alpha=0,
                    mutation_callback=rocket_smoke_mutator
            ),
            emit_done_cb=emit_done_cb            
    )
    rocket.change_x = random.uniform(-1.0, 1.0)
    rocket.change_y = random.uniform(5.0, 7.25)
    return rocket

def make_flash(prev_emitter):
    """ Return emitter that displays the brief flash when a firework shell explodes """
    return arcade.Emitter(
        center_xy=prev_emitter.get_pos(),
        emit_controller=arcade.EmitBurst(3),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=FLASH_TEXTURE,
            change_xy=arcade.rand_in_circle((0.0, 0.0), 3.5),
            lifetime=0.15
        )
    )
        
def make_puff(prev_emitter):
    """ Return emitter that generates the subtle smoke cloud left after a firework shell explodes """
    return arcade.Emitter(
        center_xy=prev_emitter.get_pos(),
        emit_controller=arcade.EmitBurst(4),
        particle_factory=lambda emitter: arcade.FadeParticle(
            filename_or_texture=PUFF_TEXTURE,
            change_xy=(_Vec2(arcade.rand_in_circle((0.0, 0.0), 0.4)) + _Vec2(0.3, 0.0)).as_tuple(),
            lifetime=4.0
        )
        
    )

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = None

        arcade.set_background_color(arcade.color.AMAZON)

        # List of cards we are dragging with the mouse
        self.held_cards = None

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = None

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list = None

        # Create a list of lists, each holds a pile of cards.
        self.piles = None
        
        # A variable for the game end state
        self.game_over = None
        
        # A sprite list for the game end states
        self.game_over_list = None
        
        self.fireworks_started = False
        
        self.emitters = []

        stars = arcade.Emitter(
            center_xy=(0.0, 0.0),
            emit_controller=arcade.EmitMaintainCount(20),
            particle_factory=lambda emitter: AnimatedAlphaParticle(
                filename_or_texture=random.choice(STAR_TEXTURES),
                change_xy=(0.0, 0.0),
                start_alpha=0,
                duration1=random.uniform(2.0, 6.0),
                mid_alpha=128,
                duration2=random.uniform(2.0, 6.0),
                end_alpha=0,
                center_xy=arcade.rand_in_rect((0.0, 0.0), SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        )
        

        self.cloud = arcade.Emitter(
            center_xy=(50, 500),
            change_xy=(0.15, 0),
            emit_controller=arcade.EmitMaintainCount(60),
            particle_factory=lambda emitter: AnimatedAlphaParticle(
                filename_or_texture=random.choice(CLOUD_TEXTURES),
                change_xy=(_Vec2(arcade.rand_in_circle((0.0, 0.0), 0.04)) + _Vec2(0.1, 0)).as_tuple(),
                start_alpha=0,
                duration1=random.uniform(5.0, 10.0),
                mid_alpha=255,
                duration2=random.uniform(5.0, 10.0),
                end_alpha=0,
                center_xy=arcade.rand_in_circle((0.0, 0.0), 50)
            )
        )
        

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        # A variable for the game end state
        self.game_over = False
        
        # A sprite list for the game end states
        self.game_over_list = arcade.SpriteList()
        self.you_win_sprite = arcade.Sprite("resources/images/game states/you win.PNG", 1.5)
        self.you_win_sprite.center_x = SCREEN_WIDTH/2 
        self.you_win_sprite.center_y = SCREEN_HEIGHT/2 
        self.game_over_list.append(self.you_win_sprite)

        # List of cards we are dragging with the mouse
        self.held_cards = []

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = []

        # ---  Create the mats the cards go on.

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Create the mats for the bottom face down and face up piles
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X, BOTTOM_Y
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X + X_SPACING, BOTTOM_Y
        self.pile_mat_list.append(pile)

        # Create the seven middle piles
        for i in range(7):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + i * X_SPACING, MIDDLE_Y
            self.pile_mat_list.append(pile)

        # Create the top "play" piles
        for i in range(4):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + i * X_SPACING, TOP_Y
            self.pile_mat_list.append(pile)

        # --- Create, shuffle, and deal the cards

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = arcade.SpriteList()

        # Create every card
        for card_suit in CARD_SUITS:
            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)
                card.position = START_X, BOTTOM_Y
                self.card_list.append(card)

        # Shuffle the cards
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list[pos1], self.card_list[pos2] = self.card_list[pos2], self.card_list[pos1]

        # Create a list of lists, each holds a pile of cards.
        self.piles = [[] for _ in range(PILE_COUNT)]

        # Put all the cards in the bottom face-down pile
        for card in self.card_list:
            self.piles[BOTTOM_FACE_DOWN_PILE].append(card)
            
        # - Pull from that pile into the middle piles, all face-down
        # Loop for each pile
        for pile_no in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            # Deal proper number of cards for that pile
            for j in range(pile_no - PLAY_PILE_1 + 1):
                # Pop the card off the deck we are dealing from
                card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                # Put in the proper pile
                self.piles[pile_no].append(card)
                # Move card to same position as pile we just put it in
                card.position = self.pile_mat_list[pile_no].position
                # Put on top in draw order
                self.pull_to_top(card)
                
        # Flip up the top cards
        for i in range(PLAY_PILE_1, PLAY_PILE_7+1):
            self.piles[i][-1].face_up()
            
            
    # Firework functions
    def launch_firework(self, delta_time):
        launchers = (
            self.launch_random_firework,
            self.launch_ringed_firework,
            self.launch_sparkle_firework,
        )
        random.choice(launchers)(delta_time)
        pyglet.clock.schedule_once(self.launch_firework, random.uniform(LAUNCH_INTERVAL_MIN, LAUNCH_INTERVAL_MAX))

    def launch_random_firework(self, _delta_time):
        """Simple firework that explodes in a random color"""
        rocket = make_rocket(self.explode_firework)
        self.emitters.append(rocket)

    def launch_ringed_firework(self, _delta_time):
        """"Firework that has a basic explosion and a ring of sparks of a different color"""
        rocket = make_rocket(self.explode_ringed_firework)
        self.emitters.append(rocket)

    def launch_sparkle_firework(self, _delta_time):
        """Firework which has sparks that sparkle"""
        rocket = make_rocket(self.explode_sparkle_firework)
        self.emitters.append(rocket)

    def launch_spinner(self, _delta_time):
        """Start the spinner that throws sparks"""
        spinner1 = make_spinner()
        spinner2 = make_spinner()
        spinner2.angle = 180
        self.emitters.append(spinner1)
        self.emitters.append(spinner2)

    def explode_firework(self, prev_emitter):
        """Actions that happen when a firework shell explodes, resulting in a typical firework"""
        #self.emitters.append(make_puff(prev_emitter))
        self.emitters.append(make_flash(prev_emitter))

        spark_texture = random.choice(SPARK_TEXTURES)
        sparks = arcade.Emitter(
            center_xy=prev_emitter.get_pos(),
            emit_controller=arcade.EmitBurst(random.randint(30, 40)),
            particle_factory=lambda emitter: arcade.FadeParticle(
                filename_or_texture=spark_texture,
                change_xy=arcade.rand_in_circle((0.0, 0.0), 9.0),
                lifetime=random.uniform(0.5, 1.2),
                mutation_callback=firework_spark_mutator
            )
        )
        self.emitters.append(sparks)

    def explode_ringed_firework(self, prev_emitter):
        """Actions that happen when a firework shell explodes, resulting in a ringed firework"""
        #self.emitters.append(make_puff(prev_emitter))
        self.emitters.append(make_flash(prev_emitter))

        spark_texture, ring_texture = random.choice(SPARK_PAIRS)
        sparks = arcade.Emitter(
            center_xy=prev_emitter.get_pos(),
            emit_controller=arcade.EmitBurst(25),
            particle_factory=lambda emitter: arcade.FadeParticle(
                filename_or_texture=spark_texture,
                change_xy=arcade.rand_in_circle((0.0, 0.0), 8.0),
                lifetime=random.uniform(0.55, 0.8),
                mutation_callback=firework_spark_mutator
            )
        )
        self.emitters.append(sparks)

        ring = arcade.Emitter(
            center_xy=prev_emitter.get_pos(),
            emit_controller=arcade.EmitBurst(20),
            particle_factory=lambda emitter: arcade.FadeParticle(
                filename_or_texture=ring_texture,
                change_xy=arcade.rand_on_circle((0.0, 0.0), 5.0) + arcade.rand_in_circle((0.0, 0.0), 0.25),
                lifetime=random.uniform(1.0, 1.6),
                mutation_callback=firework_spark_mutator
            )
        )
        self.emitters.append(ring)

    def explode_sparkle_firework(self, prev_emitter):
        """Actions that happen when a firework shell explodes, resulting in a sparkling firework"""
        #self.emitters.append(make_puff(prev_emitter))
        self.emitters.append(make_flash(prev_emitter))

        spark_texture = random.choice(SPARK_TEXTURES)
        sparks = arcade.Emitter(
            center_xy=prev_emitter.get_pos(),
            emit_controller=arcade.EmitBurst(random.randint(30, 40)),
            particle_factory=lambda emitter: AnimatedAlphaParticle(
                filename_or_texture=spark_texture,
                change_xy=arcade.rand_in_circle((0.0, 0.0), 9.0),
                start_alpha=255,
                duration1=random.uniform(0.6, 1.0),
                mid_alpha=0,
                duration2=random.uniform(0.1, 0.2),
                end_alpha=255,
                mutation_callback=firework_spark_mutator
            )
        )
        self.emitters.append(sparks)
        
        
    
    def pull_to_top(self, card):
        """ Pull card to top of rendering order (last to render, looks on-top) """
        # Find the index of the card
        index = self.card_list.index(card)
        # Loop and pull all the other cards down towards the zero end
        for i in range(index, len(self.card_list) - 1):
            self.card_list[i] = self.card_list[i + 1]
        # Put this card at the right-side/top/size of list
        self.card_list[len(self.card_list) - 1] = card

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """

        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # Have we clicked on a card?
        if len(cards) > 0:

            # Might be a stack of cards, get the top one
            primary_card = cards[-1]
            # Figure out what pile the card is in
            pile_index = self.get_pile_for_card(primary_card)
            
            # Are we clicking on the bottom deck, to flip three cards?
            if pile_index == BOTTOM_FACE_DOWN_PILE:
                # Flip three cards
                for i in range(3):
                    # If we ran out of cards, stop
                    if len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                        break
                    # Get top card
                    card = self.piles[BOTTOM_FACE_DOWN_PILE][-1]
                    # Flip face up
                    card.face_up()
                    # Move card position to bottom-right face up pile
                    card.position = self.pile_mat_list[BOTTOM_FACE_UP_PILE].position
                    # Remove card from face down pile
                    self.piles[BOTTOM_FACE_DOWN_PILE].remove(card)
                    # Move card to face up list
                    self.piles[BOTTOM_FACE_UP_PILE].append(card)
                    # Put on top draw-order wise
                    self.pull_to_top(card)
            
            elif primary_card.is_face_down:
                # Is the card face down? In one of those middle 7 piles? Then flip up
                primary_card.face_up()
            else:
                # All other cases, grab the face-up card we are clicking on
                self.held_cards = [primary_card]
                # Save the position
                self.held_cards_original_position = [self.held_cards[0].position]
                # Put on top in drawing order
                self.pull_to_top(self.held_cards[0])
    
                # Is this a stack of cards? If so, grab the other cards too
                card_index = self.piles[pile_index].index(primary_card)
                for i in range(card_index + 1, len(self.piles[pile_index])):
                    card = self.piles[pile_index][i]
                    self.held_cards.append(card)
                    self.held_cards_original_position.append(card.position)
                    self.pull_to_top(card)
                    
        else:
            
            # Click on a mat instead of a card?
            mats = arcade.get_sprites_at_point((x,y), self.pile_mat_list)
            
            if len(mats) > 0:
                mat = mats[0]
                mat_index = self.pile_mat_list.index(mat)
                
                # Is it our turned over flip mat? and no cards on it?
                if mat_index == BOTTOM_FACE_DOWN_PILE and len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                    # Flip the deck back over so we can restart
                    temp_list = self.piles[BOTTOM_FACE_UP_PILE].copy()
                    for card in reversed(temp_list):
                        card.face_down()
                        self.piles[BOTTOM_FACE_UP_PILE].remove(card)
                        self.piles[BOTTOM_FACE_DOWN_PILE].append(card)
                        card.position = self.pile_mat_list[BOTTOM_FACE_DOWN_PILE].position

    def remove_card_from_pile(self, card):
        """ Remove card from whatever pile it was in. """
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def get_pile_for_card(self, card):
        """ What pile is this card in? """
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def move_card_to_new_pile(self, card, pile_index):
        """ Move the card to a new pile """
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """

        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return

        # Find the closest pile, in case we are in contact with more than one
        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = True

        # See if we are in contact with the closest pile
        if arcade.check_for_collision(self.held_cards[0], pile):

            # What pile is it?
            pile_index = self.pile_mat_list.index(pile)

            #  Is it the same pile we came from?
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                # If so, who cares. We'll just reset our position.
                pass

            # Is it on a middle play pile?
            elif PLAY_PILE_1 <= pile_index <= PLAY_PILE_7:
                # Are there already cards there?
                if len(self.piles[pile_index]) > 0:
                    # Move cards to proper position
                    top_card = self.piles[pile_index][-1]
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = top_card.center_x, \
                                                top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)
                else:
                    # Are there no cards in the middle play pile?
                    for i, dropped_card in enumerate(self.held_cards):
                        # Move cards to proper position
                        dropped_card.position = pile.center_x, \
                                                pile.center_y - CARD_VERTICAL_OFFSET * i

                for card in self.held_cards:
                    # Cards are in the right position, but we need to move them to the right list
                    self.move_card_to_new_pile(card, pile_index)

                # Success, don't reset position of cards
                reset_position = False

            # Release on top play pile? And only one card held?
            elif TOP_PILE_1 <= pile_index <= TOP_PILE_4 and len(self.held_cards) == 1:
                # Move position of card to pile
                self.held_cards[0].position = pile.position
                # Move card to card list
                for card in self.held_cards:
                    self.move_card_to_new_pile(card, pile_index)

                reset_position = False

        if reset_position:
            # Where-ever we were dropped, it wasn't valid. Reset the each card's position
            # to its original spot.
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # We are no longer holding cards
        self.held_cards = []
        
        # Check to see if the game is over
        # If we have no cards in hand, no cards in our face up pile, and no cards in our facedown pile, the game is over
        if len(self.held_cards) == 0 and len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0 and len(self.piles[BOTTOM_FACE_UP_PILE]) == 0:
            self.game_over = True
            self.burst_timer = time.time()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy
            
    def on_key_press(self, symbol: int, modifiers: int):
        """ Uer presses key"""
        if symbol == arcade.key.R:
            # Restart
            self.setup()
       
    def update(self, delta_time):
        print(self.emitters)
        if self.game_over:
            if not self.fireworks_started:
                self.launch_firework(0)
                self.fireworks_started = True
                #arcade.schedule(self.launch_spinner, 4.0)
            
            # prevent list from being mutated (often by callbacks) while iterating over it
            emitters_to_update = self.emitters.copy()
            # update cloud
            if self.cloud.center_x > SCREEN_WIDTH:
                self.cloud.center_x = 0
            # update
            for e in emitters_to_update:
                e.update()
            # remove emitters that can be reaped
            to_del = [e for e in emitters_to_update if e.can_reap()]
            for e in to_del:
                self.emitters.remove(e)
        
    def on_update(self, dt):
        """ Update game """
        pass
                
    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        arcade.start_render()

        # Draw the mats the cards go on to
        self.pile_mat_list.draw()

        # Draw the cards
        self.card_list.draw()
        
        # Draw fireworks
        if self.game_over:
            for e in self.emitters:
                e.draw()
        
            
def firework_spark_mutator(particle: arcade.FadeParticle):
    """mutation_callback shared by all fireworks sparks"""
    # gravity
    particle.change_y += -0.03
    # drag
    particle.change_x *= 0.92
    particle.change_y *= 0.92


def rocket_smoke_mutator(particle: arcade.LifetimeParticle):
    particle.scale = arcade.lerp(0.5, 3.0, particle.lifetime_elapsed / particle.lifetime_original)
       
def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()