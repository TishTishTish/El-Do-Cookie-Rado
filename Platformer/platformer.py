# El Do-Cookie-Rado - Platform Game
# A part of 'The Last Cookie' game
# Created by Ahartisha Selakanabarajah

import arcade
from arcade.application import View
import pygame
from pygame import mixer
import pathlib

# Initialise Pygame - Need this for looping background music
pygame.init()
mixer.init()

# Game constants
# Window dimensions
SCREEN_WIDTH = 648
SCREEN_HEIGHT = 468
SCREEN_TITLE = "El Do-Cookie-Rado | The Last Cookie"

# Scaling Constants
MAP_SCALING = 1.0

# Player constants
GRAVITY = 1.0
PLAYER_START_X = 65
PLAYER_START_Y = 256
PLAYER_MOVE_SPEED = 2
PLAYER_JUMP_SPEED = 10

# Viewport margins
LEFT_VIEWPORT_MARGIN = 0
RIGHT_VIEWPORT_MARGIN = 0
TOP_VIEWPORT_MARGIN = 0
BOTTOM_VIEWPORT_MARGIN = 0

# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent / "Platformer" / "platformer-assets"

# Title view
class TitleView(arcade.View):
    def __init__(self) -> None:
        super().__init__()

        # Find the title image in the images folder
        title_image_path = ASSETS_PATH / "images" / "title-screen.png"

        # Load our title image
        self.title_image = arcade.load_texture(title_image_path)

        # Set our display timer
        self.display_timer = 3.0

        # Are we showing the help?
        self.show_help = False
        
        # Load background music
        mixer.music.load(str(ASSETS_PATH / "audio" / "music" / "intro.wav"))
        
        # Start background music
        mixer.music.play(loops=-1)

    def on_update(self, delta_time: float) -> None:
        # First, count down the time
        self.display_timer -= delta_time

        # If the timer has run out, toggle help
        if self.display_timer < 0:

            # Toggle whether to show the help
            self.show_help = not self.show_help

            # And reset the timer so the help flash slowly
            self.display_timer = 1.0

    def on_draw(self) -> None:
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with title screen
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=self.title_image,
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.RETURN:
            game_view = PlatformerView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.Q:
            help_view = HelpView()
            self.window.show_view(help_view)


# Help Screen
class HelpView(arcade.View):
    def __init__(self) -> None:
        super().__init__()

        # Find the help image in the image folder
        help_image_path = (
            ASSETS_PATH / "images" / "help-screen.png"
        )

        # Load our title image
        self.help_image = arcade.load_texture(help_image_path)

    def on_draw(self) -> None:
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with the help image
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=self.help_image,
        )

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.RETURN:
            game_view = PlatformerView()
            game_view.setup()
            self.window.show_view(game_view)

        elif key == arcade.key.ESCAPE:
            title_view = TitleView()
            self.window.show_view(title_view)

class EndView(arcade.View):
    def __init__(self) -> None:
        super().__init__()

        # Find the title image in the images folder
        title_image_path = ASSETS_PATH / "images" / "victory-screen.png"

        # Load our title image
        self.title_image = arcade.load_texture(title_image_path)

        # Set our display timer
        self.display_timer = 3.0

        # Are we showing the help?
        self.show_help = False
        
        # Load background music
        mixer.music.load(str(ASSETS_PATH / "audio" / "music" / "back-home.wav"))
        
        # Start background music
        mixer.music.play(loops=-1)

    def on_update(self, delta_time: float) -> None:
        # First, count down the time
        self.display_timer -= delta_time

        # If the timer has run out, toggle help
        if self.display_timer < 0:

            # Toggle whether to show the help
            self.show_help = not self.show_help

            # And reset the timer so the help flash slowly
            self.display_timer = 1.0

    def on_draw(self) -> None:
        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with title screen
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=self.title_image,
        )
    
    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
            print("End of El Do-Cookie-Rado")

class PlatformerView(arcade.View):
    def __init__(self) -> None:
        super().__init__()

        # Sprite List
        self.cookies = None
        self.background = None
        self.walls = None
        self.ladders = None
        self.goals = None
        self.portal = None

        # Player Sprite
        self.player = None

        # Phyics Engine
        self.physics_engine = None

        # Keeping score
        self.score = 0

        # Current Level
        self.level = 1

        # Load sound effects
        self.cookie_sound = arcade.load_sound(
            str(ASSETS_PATH / "audio" / "sounds" / "select.mp3")
        )
        self.jump_sound = arcade.load_sound(
            str(ASSETS_PATH / "audio" / "sounds" / "jump.mp3")
        )
    
    def setup(self) -> None:
        # Set up game for current level

        # Current map according level
        map_name = f"platform_level_{self.level:02}.tmx"
        map_path = ASSETS_PATH / map_name

        # What are the names of the layers?
        wall_layer = "ground"
        cookie_layer = "cookies"
        goal_layer = "goal"
        background_layer = "background"
        ladders_layer = "ladders"
        portal_layer = "portal"

        # Load the current map
        game_map = arcade.tilemap.read_tmx(str(map_path))

        # Load the layers
        self.background = arcade.tilemap.process_layer(
            game_map, layer_name=background_layer, scaling=MAP_SCALING
        )
        self.goals = arcade.tilemap.process_layer(
            game_map, layer_name=goal_layer, scaling=MAP_SCALING
        )
        self.walls = arcade.tilemap.process_layer(
            game_map, layer_name=wall_layer, scaling=MAP_SCALING
        )
        self.ladders = arcade.tilemap.process_layer(
            game_map, layer_name=ladders_layer, scaling=MAP_SCALING
        )
        self.cookies = arcade.tilemap.process_layer(
            game_map, layer_name=cookie_layer, scaling=MAP_SCALING
        )
        self.portal = arcade.tilemap.process_layer(
            game_map, layer_name=portal_layer, scaling=MAP_SCALING
        )

        # Set the background color
        background_color = arcade.color.FRESH_AIR
        if game_map.background_color:
            background_color = game_map.background_color
        arcade.set_background_color(background_color)
        
        # Load background music
        mixer.music.load(str(ASSETS_PATH / "audio" / "music" / "finding-home.wav"))
        
        # Start background music
        mixer.music.play(loops=-1)

        # Find the edge of the map to control viewport scrolling
        self.map_width = (
            game_map.map_size.width - 1
        ) * game_map.tile_size.width

        # Create the player sprite, if they're not already setup
        if not self.player:
            self.player = self.create_player_sprite()

        # Move the player sprite back to the beginning
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.player.change_x = 0
        self.player.change_y = 0

        # Reset the viewport
        self.view_left = 0
        self.view_bottom = 0

        # Load the physics engine for this map
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            platforms=self.walls,
            gravity_constant=GRAVITY,
            ladders=self.ladders,
        )

    def create_player_sprite(self) -> arcade.AnimatedWalkingSprite:
        # Create the player sprite
        
        # Folder location of sprites
        texture_path = ASSETS_PATH / "images" / "player"

        # Setup textures
        walking_paths = [
            texture_path / f"walking_to_right{x}.png" for x in (1, 2)
        ]
        climbing_paths = [
            texture_path / f"climbing_{x}.png" for x in (1, 2)
        ]
        standing_path = texture_path / "standing_l.png"

        # Load textures
        walking_right_textures = [
            arcade.load_texture(texture) for texture in walking_paths
        ]
        walking_left_textures = [
            arcade.load_texture(texture, mirrored=True)
            for texture in walking_paths
        ]

        walking_up_textures = [
            arcade.load_texture(texture) for texture in climbing_paths
        ]
        walking_down_textures = [
            arcade.load_texture(texture) for texture in climbing_paths
        ]

        standing_right_textures = [arcade.load_texture(standing_path)]

        standing_left_textures = [
            arcade.load_texture(standing_path, mirrored=True)
        ]

        # Create the sprite
        player = arcade.AnimatedWalkingSprite()

        # Add the textures
        player.stand_left_textures = standing_left_textures
        player.stand_right_textures = standing_right_textures
        player.walk_left_textures = walking_left_textures
        player.walk_right_textures = walking_right_textures
        player.walk_up_textures = walking_up_textures
        player.walk_down_textures = walking_down_textures

        # Set the player defaults
        player.center_x = PLAYER_START_X
        player.center_y = PLAYER_START_Y
        player.state = arcade.FACE_RIGHT

        # Set the initial texture
        player.texture = player.stand_right_textures[0]

        return player

    def on_key_press(self, key: int, modifiers: int) -> None:
        # Check for player left/right movement
        if key in [arcade.key.LEFT, arcade.key.J]:
            self.player.change_x = -PLAYER_MOVE_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.L]:
            self.player.change_x = PLAYER_MOVE_SPEED

        # Check if player can climb up or down
        elif key in [arcade.key.UP, arcade.key.I]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = PLAYER_MOVE_SPEED
        elif key in [arcade.key.DOWN, arcade.key.K]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = -PLAYER_MOVE_SPEED

        # Check if we can jump
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
                # Play the jump sound
                arcade.play_sound(self.jump_sound)

    def on_key_release(self, key: int, modifiers: int) -> None:
        # Check for player left/right movement
        if key in [
            arcade.key.LEFT,
            arcade.key.J,
            arcade.key.RIGHT,
            arcade.key.L,
        ]:
            self.player.change_x = 0

        # Check if player can climb up or down
        elif key in [
            arcade.key.UP,
            arcade.key.I,
            arcade.key.DOWN,
            arcade.key.K,
        ]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = 0

    def on_update(self, delta_time: float) -> None:
        # Update the player animation
        self.player.update_animation(delta_time)

        # Update player movement based on the physics engine
        self.physics_engine.update()

        # Restrict user movement so they can't walk off screen
        if self.player.left < 0:
            self.player.left = 0

        # Check if a cookie has been picked up
        cookies_hit = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.cookies
        )

        for cookie in cookies_hit:
            # Add the cookie score to our score
            self.score += int(cookie.properties["point_value"])

            # Play the cookie sound
            arcade.play_sound(self.cookie_sound)

            # Remove the cookie
            cookie.remove_from_sprite_lists()

        # Now check if we're at the ending goal
        goals_hit = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.goals
        )

        if goals_hit:
            # Setup the next level
            self.level += 1
            self.setup()
            
        # Check if the player has reached the end of the game i.e. found the key
        end_of_game = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.portal
        )
        
        if end_of_game:
            view = EndView()
            self.window.show_view(view)
        
        # Set the viewport, scrolling if necessary
        self.scroll_viewport()

    def scroll_viewport(self) -> None:
        # Attempted to create a camera to follow the player's movement
        # Scroll left
        # Find the current left boundary
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN

        # Are we to the left of this boundary? Then we should scroll left
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            # But don't scroll past the left edge of the map
            if self.view_left < 0:
                self.view_left = 0

        # Scroll right
        # Find the current right boundary
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN

        # Are we right of this boundary? Then we should scroll right
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            # Don't scroll past the right edge of the map
            if self.view_left > self.map_width - SCREEN_WIDTH:
                self.view_left = self.map_width - SCREEN_WIDTH

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom

        # Only scroll to integers. Otherwise we end up with pixels that
        # don't line up on the screen
        self.view_bottom = int(self.view_bottom)
        self.view_left = int(self.view_left)

        # Do the scrolling
        arcade.set_viewport(
            left=self.view_left,
            right=SCREEN_WIDTH + self.view_left,
            bottom=self.view_bottom,
            top=SCREEN_HEIGHT + self.view_bottom,
        )

    def on_draw(self) -> None:
        arcade.start_render()

        # Draw all the sprites
        self.background.draw()
        self.walls.draw()
        self.cookies.draw()
        self.goals.draw()
        self.ladders.draw()
        self.portal.draw()
        self.player.draw()

        # Define the score variable
        score_text = f"Score: {self.score}"

        # Draw the score onto the screen
        arcade.draw_text(
            score_text,
            start_x=12 + self.view_left,
            start_y=432 + self.view_bottom,
            color=arcade.csscolor.DEEP_PINK,
            font_size=20,
        )

if __name__ == "__main__":
    window = arcade.Window(
        width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE
    )
    title_view = TitleView()
    window.show_view(title_view)
    arcade.run()