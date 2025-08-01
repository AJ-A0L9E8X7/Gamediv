import arcade
import os

# Constants
# Screen size + Title
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Hypervision - noclipper"

# Size of tiles in map
TILE_SCALING = 1.5

# Settings for player character.
PLAYER_JUMP_SPEED = 15
GRAVITY = 1
MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 5
RIGHT_FACING = 0
LEFT_FACING = 1
CHARACTER_SCALING = 0.3
DIM = 1

# Animation for player character.
class PlayerCharacter(arcade.Sprite):
    def __init__(self, idle_texture_pair, walk_texture_pairs, jump_texture_pair, fall_texture_pair):
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.idle_texture_pair = idle_texture_pair
        self.walk_textures = walk_texture_pairs
        self.jump_texture_pair = jump_texture_pair
        self.fall_texture_pair = fall_texture_pair
        super().__init__(self.idle_texture_pair[0], scale=CHARACTER_SCALING)

    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x < 0:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0:
            self.character_face_direction = RIGHT_FACING

        if self.change_y > 0:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return

        if self.change_y < 0:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        self.cur_texture += 1
        if self.cur_texture >= 8 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]

# Start Screen
class InstructionView(arcade.View):

    def on_show_view(self):
        """ This is run once when we switch to this view """
        self.window.background_color = arcade.csscolor.BLACK

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        self.window.default_camera.use()

    # Draw the starting text.
    def on_draw(self):
        """ Draw this view """
        self.clear()
        arcade.draw_text("Hypervision . Noclipper", self.window.width / 2, self.window.height / 2,
                        arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("""WASD to move, Q to quit, E to see, X to retry, th
e coins you picked up will be your score.""", 
                        self.window.width / 2, self.window.height / 2-25,
                        arcade.color.WHITE, font_size=10, anchor_x="center")
        arcade.draw_text("Click to contiue", self.window.width / 2, self.window.height / 2-75,
                        arcade.color.WHITE, font_size=20, anchor_x="center")
        
    # Starts the game after mouse click.
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)
        
# This class shows the end of the game using a picture
class GameEndView(arcade.View):

    """ View to show when game is over """
    def __init__(self):

        """ This is run once when we switch to this view """
        super().__init__()
        self.texture = arcade.load_texture("end.png")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        self.window.default_camera.use()

    def on_draw(self):
        """ Draw this view """
        self.clear()
        arcade.draw_texture_rect(
            self.texture,
            rect=arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, re-start the game. """
        arcade.close_window()

# Class for main game
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        # tiled map
        self.tile_map = None
        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.player_sprite_list = None
        self.physics_engine = None
        # Hide the underlayer at the start of the game.
        self.layer2_visible = False
        self.player = None
        # Init player score & deaths 
        self.gold = 0
        self.deaths = 0
        self.key = 0
        self.reset_key = True 
        self.reset_gold = True
        self.reset_death = False
        self.exit = 0
        # Set init level
        self.level = 1

        character = ":resources:images/animated_characters/female_adventurer/femaleAdventurer"

        idle = arcade.load_texture(f"{character}_idle.png")
        self.idle_texture_pair = idle, idle.flip_left_right()

        self.walk_texture_pairs = []
        for i in range(8):
            texture = arcade.load_texture(f"{character}_walk{i}.png")
            self.walk_texture_pairs.append((texture, texture.flip_left_right()))

        jump = arcade.load_texture(f"{character}_jump.png")
        self.jump_texture_pair = jump, jump.flip_left_right()

        fall = arcade.load_texture(f"{character}_fall.png")
        self.fall_texture_pair = fall, fall.flip_left_right()

    # Import layers and show info
    def setup(self):
        layer_options = {
            "platforms": {
                "use_spatial_hash": True
            },
            "underlayer": {
                "use_spatial_hash": True
            },
            "spike":{
                "use_spatial_hash": True
            },
            "gold":{
                "use_spatial_hash": True
            },
            "key":{
                "use_spatial_hash": True
            },
            "exit":{
                "use_spatial_hash": True
            }
        }

        if self.level >= 4:
            view = GameEndView()
            self.window.show_view(view)
        else:   
            map_path = os.path.join(os.path.dirname(__file__), f"Tiled/world{self.level}.tmx")
        #map_path = os.path.join(os.path.dirname(__file__), f"Tiled/world3.tmx")
        self.tile_map = arcade.load_tilemap(
            map_path,
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        # Hide underlayer at the start of game
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        if "underlayer" in self.scene:
            for block in self.scene["underlayer"]:
                block.visible = False


        self.player_sprite_list = arcade.SpriteList()

        # Load textures for player
        self.player = PlayerCharacter(
            self.idle_texture_pair,
            self.walk_texture_pairs,
            self.jump_texture_pair,
            self.fall_texture_pair
        )
        
        # Desplay the character on screen in a specific position.
        self.player.center_x = WINDOW_WIDTH / 7
        self.player.center_y = WINDOW_HEIGHT / 3
        self.player_sprite_list.append(self.player)
        self.scene.add_sprite("Player", self.player)

        # Add collision box for the platforms
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, walls=self.scene["platforms"], gravity_constant=GRAVITY
        )
        #self.physics_engine = arcade.PhysicsEnginePlatformer(
        #    self.player, walls=self.scene["underlayer"], gravity_constant=GRAVITY
        #)

        # Camera follow
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        
        # Show the number of loot and deaths
        if self.reset_gold:
            self.gold = 0
        self.reset_gold = False
        
        # Reset key after death and progress
        if self.reset_key:
            self.key = 0
        self.reset_key = True
        
        self.gold_text = arcade.Text(f"Loot: {self.gold}", x=50, y=650, font_size=50)
        
        self.deaths_text = arcade.Text(f"Deaths:{self.deaths}", x=50, y=600, font_size=50)
        
        
        
        if self.key != 1:
            self.key_text = arcade.Text(f"You need a key to open the door", x=50, y=500, font_size=50)
        else:
            self.key_text = arcade.Text(f"Key:{self.key}", x=50, y=550, font_size=50)
        
        self.background_color = arcade.csscolor.BLACK
        
        # load exit
        self.exit_list = self.scene["exit"]
    
    # Switch between layers   
    def toggle_layers(self):
        self.layer2_visible = not self.layer2_visible
        if "underlayer" in self.scene:
            for blocks in self.scene["underlayer"]:
                blocks.visible = self.layer2_visible
    
    # Display game screen            
    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()
        self.gold_text.draw()
        self.deaths_text.draw()
        self.key_text.draw()

    # Detections during play
    def on_update(self, delta_time):
        # Show the underlayer and apply collision if press E
        if self.layer2_visible:
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player, 
                walls=self.scene["platforms"], 
                platforms=self.scene["underlayer"], 
                gravity_constant=GRAVITY
            )
            
        else:
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player, 
                walls=self.scene["platforms"], 
                gravity_constant=GRAVITY
            )
        
        # Load collision, player collision, animation, and camera follow
        self.physics_engine.update()
        self.player_sprite_list.update()
        self.player.update_animation(delta_time)
        self.camera.position = self.player.position
        
        # Update all the coins to a player hit list
        coin_hit_list = []
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player, self.scene["gold"]
        )

        # When user hits a coin, remove the object and add the score by 1
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.gold += 1
            self.gold_text.text = f"Loot: {self.gold}"
        
        # Update all keys to a list
        key_hit_list = []
        key_hit_list = arcade.check_for_collision_with_list(
            self.player, self.scene["key"]
        )
        
        # When the user hits a key, removes key and add key count.
        for key in key_hit_list:
            key.remove_from_sprite_lists()
            self.key += 1
            self.key_text.text = f"Key: {self.key}"
        
        # Check if the player hits a spike, if so reset.
        if "spike" in self.scene:
            if arcade.check_for_collision_with_list(self.player, self.scene["spike"]):
                self.deaths += 1
                self.deaths_text.text = f"Deaths: {self.deaths}"
                self.reset_gold = True
                self.setup()
        
        # if exit, add level number by one
        exit_hit_list = arcade.check_for_collision_with_list(self.player, self.exit_list)
        if exit_hit_list:
            if self.key == 1:
                self.level += 1
                self.key = 0
            if self.level >=4:
                self.level -= 1
            self.reset_score = False
            self.setup()
        
        # If level larger than 4, end game
        


    # Key detection
    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.player.change_x = -MOVEMENT_SPEED
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.player.change_x = MOVEMENT_SPEED
        elif key in (arcade.key.ESCAPE, arcade.key.Q):
            arcade.close_window()
        elif key == arcade.key.X:
            self.setup()
        elif key == arcade.key.E:
            layer_image = 0
            self.toggle_layers()

    # Release key
    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D):
            self.player.change_x = 0


# Load game
def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()


