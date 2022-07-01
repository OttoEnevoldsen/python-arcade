"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""

import arcade
import random



SPRITE_SCALING = 0.3

# Set the size of the screen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

# Variables controlling the player
PLAYER_LIVES = 5
PLAYER_SPEED_X = 5
PLAYER_SPEED_Y = 5
PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = SCREEN_HEIGHT / 2
PLAYER_SHOT_SPEED = 4
OBSTACLE_SPEED = 5
DASHING_TIME = 0.3
DASH_COOLDOWN = 1
OBSTACLE_HARMLESS_TIME = 2.5
OBSTACLE_HARMLESS_ALPHA = 100
OBSTACLE_HARMLESS_SPEED_FACTOR = 0.3
# length of a level in seconds
LEVEL_TIME = 20

TAKING_DAMAGE_TIME = 0.75
LIVES_TAKING_DAMAGE = 1
DASH_ALPHA = 150



DASHING_KEY = arcade.key.SPACE

class Player(arcade.Sprite):
    """
    The player
    """

    def __init__(self, **kwargs):
        """
        Setup new Player object
        """


        # How much to scale the graphics
        kwargs['scale'] = SPRITE_SCALING

        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)

        self.taking_damage_timer = 0
        self.taking_damage_path = "images/playerShip1_red.png"
        self.normal_path = "images/playerShip1_blue.png"

        self.texture = arcade.load_texture(self.normal_path)

        self.player_lives = PLAYER_LIVES


        self.is_dashing = False
        self.dashing_time_left = 0
        self.dash_cooldown = 0

    def dash(self):
        """
        Enable Dashing
        """
        if not self.is_dashing and self.dash_cooldown <= 0:
            self.is_dashing = True
            self.dashing_time_left = DASHING_TIME
            self.dash_cooldown = DASH_COOLDOWN
            self.alpha = DASH_ALPHA

    def taking_damage(self):
        if self.taking_damage_timer == 0:
            self.taking_damage_timer = TAKING_DAMAGE_TIME
            self.texture = arcade.load_texture(self.taking_damage_path)
            self.player_lives -= LIVES_TAKING_DAMAGE


    def update(self, delta_time):
        """
        Move the sprite
        """
        if self.is_dashing:
            self.dashing_time_left -= delta_time
            if self.dashing_time_left <= 0:
                self.is_dashing = False
                self.dashing_time_left = 0
                self.alpha = 255

        if self.taking_damage_timer > 0:
            self.taking_damage_timer -= delta_time
        elif self.taking_damage_timer <= 0:
            self.texture = arcade.load_texture(self.normal_path)
            self.taking_damage_timer = 0



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

        if not self.is_dashing:
            self.dash_cooldown -= delta_time

class Obstacle(arcade.Sprite):
    """
    obstacles to dodge
    """

    obstacle_max_speed = 3

    types = {
        1: {
            "vectors": [
                [1, 0], # right
                [-1, 0],  # left
                [0, 1], # up
                [0, -1], # down
                [1, 1],
                [-1, -1],
                [1, -1],
                [-1, 1]
            ],
            "graphics": "images/Meteors/meteorGrey_med2.png",
            # "scaling": random.randint(3, 8)
        },
        2: {
            "vectors": [
                [1, 0],  # right
                [-1, 0],  # left
                [0, 1],  # up
                [0, -1],  # down
                [1, 1],
                [-1, -1],
                [1, -1],
                [-1, 1]
            ],
            "graphics": "images/Meteors/meteorBrown_med3.png",
            # "scaling": random.randint(4, 9)
        },
        3: {
            "vectors": [
                [1, 0],  # right
                [-1, 0],  # left
                [0, 1],  # up
                [0, -1],  # down
                [1, 1],
                [-1, -1],
                [1, -1],
                [-1, 1]
            ],
            "graphics": "images/Meteors/meteorGrey_tiny2.png",
            # "scaling": random.randint(4, 9),
        }
    }
    def __init__(self, speed, type=1, spawn_on_edge=False):

        super().__init__(Obstacle.types[type]["graphics"], SPRITE_SCALING * random.randint(4, 9))

        if spawn_on_edge:
            spawn_positions = [
                (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT), # Top edge
                (SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)), # Right
                (0, random.randint(0, SCREEN_HEIGHT)), # Left
                (random.randint(0, SCREEN_WIDTH), 0) #
            ]
            self.center_x, self.center_y = random.choice(spawn_positions)
        else:
            self.center_x = random.randint(0, SCREEN_WIDTH)
            self.center_y = random.randint(0, SCREEN_HEIGHT)

        self.speed_x, self.speed_y = random.choice(Obstacle.types[type]["vectors"])

        # random speed noise for obstacles
        self.speed_noise = random.uniform(0.9, 1.1)
        self.change_x *= speed * self.speed_noise
        self.change_y *= speed * self.speed_noise

        self.change_angle = random.uniform(-1, 1)

        self.alpha = OBSTACLE_HARMLESS_ALPHA

        if spawn_on_edge is False:
            self.harmless_timer = OBSTACLE_HARMLESS_TIME
            self.is_harmless = True
        else:
            self.harmless_timer = 0
            self.is_harmless = False

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

        if self.harmless_timer > 0:
            self.is_harmless = True
            self.alpha = min(255 / self.harmless_timer, 255)
            self.harmless_timer -= delta_time
        else:
            self.is_harmless = False
            self.alpha = 255

        if self.is_harmless:
            self.change_x = self.speed_x * OBSTACLE_HARMLESS_SPEED_FACTOR
            self.change_y = self.speed_y * OBSTACLE_HARMLESS_SPEED_FACTOR
            self.angle += self.change_angle * OBSTACLE_HARMLESS_SPEED_FACTOR
        else:
            self.change_x = self.speed_x
            self.change_y = self.speed_y
            self.angle += self.change_angle



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

        self.level_timer = None
        self.player_score = None

        # Variable that will hold a list of shots fired by the player
        self.player_shot_list = None
        self.obstacle_list = None
        self.number_of_obstacles = None

        # Set up the player info
        self.player_sprite = None
        self.player_score = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

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

            # self.joystick.
        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # No points when the game starts
        self.player_score = 0

        # Sprite lists
        self.player_shot_list = arcade.SpriteList()

        # Create a Player object
        self.player_sprite = Player(
            center_x=PLAYER_START_X,
            center_y=PLAYER_START_Y
        )

        self.current_level = 0
        self.obstacle_speed = OBSTACLE_SPEED

        self.number_of_obstacles = 40

        self.new_level()


    def new_level(self):

        self.level_timer = LEVEL_TIME


        self.obstacle_list = arcade.SpriteList()
        self.number_of_obstacles += self.current_level
        self.current_level += 1

        # Increases obstacle_speed with 50%
        self.obstacle_speed *= 1.5

        for i in range(self.number_of_obstacles):
            self.obstacle_list.append(Obstacle(speed=self.obstacle_speed, type=random.randint(1, 3)))

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw the obstacles
        self.obstacle_list.draw()

        # Draw the player sprite
        self.player_sprite.draw()

        # Draw players score on screen
        arcade.draw_text(
            "LIVES: {}".format(self.player_sprite.player_lives),  # Text to show
            10,  # X position
            SCREEN_HEIGHT - 20,  # Y positon
            arcade.color.WHITE  # Color of text
        )

        arcade.draw_text(
            "score: {}".format(int(self.player_score) * 10),  # Text to show
            10,  # X position
            SCREEN_HEIGHT - 40,  # Y positon
            arcade.color.WHITE  # Color of text
        )

        arcade.draw_text(
            "Next level in: {}".format(int(self.level_timer)),  # Text to show
            10,  # X position
            SCREEN_HEIGHT - 60,  # Y positon
            arcade.color.WHITE  # Color of text
        )

        arcade.draw_text(
            "Level: {}".format(int(self.current_level)),  # Text to show
            10,  # X position
            SCREEN_HEIGHT - 80,  # Y positon
            arcade.color.WHITE  # Color of text
        )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Calculate player speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        obstacles_colliding_with_player = arcade.check_for_collision_with_list(
            self.player_sprite, self.obstacle_list
        )
        for o in obstacles_colliding_with_player:
            if self.player_sprite.is_dashing is False and not o.is_harmless:
                self.player_sprite.taking_damage()

        # Move player with keyboard
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_SPEED_X
            self.player_sprite.angle = 90

        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_SPEED_X
            self.player_sprite.angle = -90

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_SPEED_Y
            self.player_sprite.angle = 0

        if self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = - PLAYER_SPEED_Y
            self.player_sprite.angle = 180

        # Move player with joystick if present
        if self.joystick:
            self.player_sprite.change_x = round(self.joystick.x) * PLAYER_SPEED_X
            self.player_sprite.change_y = round(self.joystick.y) * PLAYER_SPEED_Y * -1
            if round(self.joystick.x) == 1:
                self.player_sprite.angle = -90
            elif round(self.joystick.x) == -1:
                self.player_sprite.angle = 90
            elif round(self.joystick.y) == 1:
                self.player_sprite.angle = 180
            elif round(self.joystick.y) == -1:
                self.player_sprite.angle = 0

        # Update player sprite
        self.player_sprite.update(delta_time)

        # add missing obstacles
        while len(self.obstacle_list) < self.number_of_obstacles:
            self.obstacle_list.append(Obstacle(speed=self.obstacle_speed, type=random.randint(1, 3), spawn_on_edge=True))

        # Update the player shots
        for o in self.obstacle_list:
            o.on_update(delta_time)

        self.level_timer -= delta_time

        if self.level_timer <= 0:
            self.new_level()

        if self.obstacle_speed > Obstacle.obstacle_max_speed:
            self.obstacle_speed = Obstacle.obstacle_max_speed

        self.player_score += int((10. * delta_time) * 10)
        if self.player_sprite.player_lives < 1:
            print("your final score is", int(self.player_score * 10))
            exit(0)

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

            # self.player_shot_list.append(new_shot)

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

    def on_joybutton_press(self, joystick, button_no):
        # print("Button pressed:", button_no)
        # Press the fire key
        self.on_key_press(DASHING_KEY, [])
        pass
    def on_joybutton_release(self, joystick, button_no):
        # print("Button released:", button_no)
        pass
    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))


    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        # print("Joystick hat ({}, {})".format(hat_x, hat_y))
        pass


def main():
    """
    Main method
    """

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()