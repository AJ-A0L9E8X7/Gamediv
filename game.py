import arcade
import os

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"

TILE_SCALING = 1.5
PLAYER_JUMP_SPEED = 20
GRAVITY = 1.5

MOVEMENT_SPEED = 6
UPDATES_PER_FRAME = 5

RIGHT_FACING = 0
LEFT_FACING = 1

CHARACTER_SCALING = 0.3
DIM = 1



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


class GameView(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        # tiled map
        self.tile_map = None
        self.scene = None
        self.camera = None
        self.gui_camera = None
        self.player_sprite_list = None
        self.physics_engine = None
# SpriteList for coins the player can collect
        self.layer2_visible = True
        self.player = None


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

    def setup(self):
        layer_options = {
            "platforms": {
                "use_spatial_hash": True
            },
            "underlayer": {
                "use_spatial_hash": True
            }
        }

        map_path = os.path.join(os.path.dirname(__file__), "Tiled/world1.tmx")

        self.tile_map = arcade.load_tilemap(
            map_path,
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        self.scene = arcade.Scene.from_tilemap(self.tile_map)


        self.player_sprite_list = arcade.SpriteList()


        self.player = PlayerCharacter(
            self.idle_texture_pair,
            self.walk_texture_pairs,
            self.jump_texture_pair,
            self.fall_texture_pair
        )
        self.player.center_x = WINDOW_WIDTH / 7
        self.player.center_y = WINDOW_HEIGHT / 2
        self.player_sprite_list.append(self.player)
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, walls=self.scene["platforms"], gravity_constant=GRAVITY
        )
        #self.physics_engine = arcade.PhysicsEnginePlatformer(
        #    self.player, walls=self.scene["underlayer"], gravity_constant=GRAVITY
        #)

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE
        
    def toggle_layers(self):
        self.layer2_visible = not self.layer2_visible
 
        if "underlayer" in self.scene:
            for blocks in self.scene["underlayer"]:
                blocks.visible = self.layer2_visible
                
    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()

    def on_update(self, delta_time):
        if self.layer2_visible:
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player, walls=self.scene["platforms"], gravity_constant=GRAVITY
            )
        else:
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player, walls=self.scene["platforms"], platforms=self.scene["underlayer"], gravity_constant=GRAVITY
            )
            
        self.physics_engine.update()
        self.player_sprite_list.update()
        self.player.update_animation(delta_time)
        self.camera.position = self.player.position

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
        elif key == arcade.key.E:
            layer_image = 0
            self.toggle_layers()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D):
            self.player.change_x = 0


def main():
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
 

