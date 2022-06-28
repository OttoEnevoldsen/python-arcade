"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""

import arcade
import random


SPRITE_SCALING = 0.5

# Set the size of the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Variables controlling the player
PLAYER_LIVES = 500
PLAYER_SPEED_X = 5
PLAYER_SPEED_Y = 5
PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = SCREEN_HEIGHT / 2
PLAYER_SHOT_SPEED = 4
OBSTACLE_SPEED = 3
DASHING_TIME = 0.3



DASHING_KEY = arcade.key.SPACE

class Player(arcade.Sprite):
    """
    The player
    """

    def __init__(self, **kwargs):
        """
        Setup new Player object
        """

        # Graphics to use for Player
        kwargs['filename'] = "images/playerShip1_blue.png"

        # How much to scale the graphics
        kwargs['scale'] = SPRITE_SCALING

        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)

        self.is_dashing = False
        self.dashing_time_left = 0

    def dash(self):
        """
        Enable Dashing
        """
        if not self.is_dashing:
            self.is_dashing = True
            self.dashing_time_left = DASHING_TIME

    def update(self, delta_time):
        """
        Move the sprite
        """
        if self.is_dashing:
            self.dashing_time_left -= delta_time
            if self.dashing_time_left <= 0:
                self.is_dashing = False
                self.dashing_time_left = 0

        # Update center_x
        if self.is_dashing:
            self.center_x += self.change_x * 3
            self.center_y += self.change_y * 3
        else:
            self.center_x += self.change_x
            self.center_y += self.change_y

        # Don't let the player move off-screen
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1
        elif self.bottom < 0:
            self.bottom = 0


class Obstacle(arcade.Sprite):
    """
    obstacles to dodge
    """
    types = {
        1: {
            "velocities": [
                [1, 0], # right
                [-1, 0],  # left
                [0, 1], # up
                [0, -1], # down
                [1, 1],
                [-1, -1],
                [1, -1],
                [-1, 1]
            ],
            "graphics": "images/Meteors/meteorGrey_med2.png"
        },
        2: {
            "velocities": [
                [2, 0],  # right
                [-2, 0],  # left
                [0, 2],  # up
                [0, - 2] # down
            ],
            "graphics": "images/Meteors/meteorBrown_med3.png"
        }
    }
    def __init__(self, type=1):

        super().__init__(Obstacle.types[type]["graphics"], SPRITE_SCALING * random.randint(3, 8))

        self.center_y = random.randint(0, 800)
        self.center_x = random.randint(0, 1200)
        self.velocity = random.choice(Obstacle.types[type]["velocities"])
        # self.change_x, self.change_y = random.choice(Obstacle.directions)

    def on_update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.left > SCREEN_WIDTH:
            self.kill()
        elif self.right < 0:
            self.kill()
        elif self.bottom > SCREEN_HEIGHT:
            self.kill()
        elif self.top < 0:
            self.kill()


class PlayerShot(arcade.Sprite):
    """
    A shot fired by the Player
    """

    def __init__(self, center_x=0, center_y=0):
        """
        Setup new PlayerShot object
        """

        # Set the graphics to use for the sprite
        super().__init__("images/Lasers/laserBlue01.png", SPRITE_SCALING)

        self.center_x = center_x
        self.center_y = center_y
        self.change_y = PLAYER_SHOT_SPEED

    def update(self):
        """
        Move the sprite
        """

        # Update y position
        self.center_y += self.change_y

        # Remove shot when over top of screen
        if self.bottom > SCREEN_HEIGHT:
            self.kill()


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(width, height)

        # Variable that will hold a list of shots fired by the player
        self.player_shot_list = None
        self.obstacle_list = None

        # Set up the player info
        self.player_sprite = None
        self.player_score = None
        self.player_lives = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # level
        self.current_level = None

        # Get list of joysticks
        joysticks = arcade.get_joysticks()

        if joysticks:
            print("Found {} joystick(s)".format(len(joysticks)))

            # Use 1st joystick found
            self.joystick = joysticks[0]

            # Communicate with joystick
            self.joystick.open()

            # Map joysticks functions to local functions
            self.joystick.on_joybutton_press = self.on_joybutton_press
            self.joystick.on_joybutton_release = self.on_joybutton_release
            self.joystick.on_joyaxis_motion = self.on_joyaxis_motion
            self.joystick.on_joyhat_motion = self.on_joyhat_motion

        else:
            print("No joysticks found")
            self.joystick = None


            #self.joystick.
        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # No points when the game starts
        self.player_score = 0

        # No of lives
        self.player_lives = PLAYER_LIVES

        # Sprite lists
        self.player_shot_list = arcade.SpriteList()

        # Create a Player object
        self.player_sprite = Player(
            center_x=PLAYER_START_X,
            center_y=PLAYER_START_Y
        )

        self.current_level = 0

        self.new_level()

    def new_level(self):

        self.obstacle_list = arcade.SpriteList()

        self.current_level += 1

        for i in range(100):
            # exits game when there is no more levels
            try:
                self.obstacle_list.append(Obstacle(type=self.current_level))
            except KeyError:
                self.game_over()

    def game_over(self):
        print("Game Over You Won!!")
        exit(0)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw the player shot
        self.player_shot_list.draw()

        # Draw the player sprite
        self.player_sprite.draw()

        # Draw the obstacles
        self.obstacle_list.draw()

        # Draw players score on screen
        arcade.draw_text(
            "LIVES: {}".format(self.player_lives),  # Text to show
            10,                  # X position
            SCREEN_HEIGHT - 20,  # Y positon
            arcade.color.WHITE   # Color of text
        )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        obstacle_colliding_with_player = arcade.check_for_collision_with_list(
            self.player_sprite,
            self.obstacle_list
        )

        if len(obstacle_colliding_with_player) > 0:
            print("Hit!\nYou have {}, lives.".format(self.player_lives))
            self.player_lives -= 1

        # Calculate player speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        # Move player with keyboard
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_SPEED_X
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_SPEED_X
        elif self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_SPEED_Y
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_SPEED_Y


        # Move player with joystick if present
        if self.joystick:
            self.player_sprite.change_x = round(self.joystick.x) * PLAYER_SPEED_X

        # Update player sprite
        self.player_sprite.update(delta_time)

        # Update the player shots
        self.player_shot_list.update()

        for o in self.obstacle_list:
            o.on_update(delta_time)

        if len(self.obstacle_list) == 0:
            self.new_level()



    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """

        # Track state of arrow keys
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

        if key == DASHING_KEY:
            self.player_sprite.dash()

    def on_key_release(self, key, modifiers):
        """
        Called whenever a key is released.
        """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_joybutton_release(self, joystick, button_no):
        print("Button released:", button_no)

    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Joystick hat ({}, {})".format(hat_x, hat_y))

def main():
    """
    Main method
    """

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
