import arcade
import math
from pymunk.vec2d import Vec2d
import time

from dataclasses import dataclass
from typing import List

from player import Player,Bullet,MOVE_MAP_PLAYER_1



SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Under Development"
SCALING = 0.1
PLAYER_1_SPEED = 5
PLAYER_2_SPEED = 3
BULLET_SPEED = 7
TILE_SCALING = 1.5

# Classes

class GameView(arcade.View):
    """Main welcome window
    """

    def __init__(self):
        """Initialize the window
        """
        # Call the parent class constructor
        super().__init__()

        self.bullets = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.deadly_list = arcade.SpriteList()
        self.players = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        # Physics engine currently only handles player-wall collisions
        self.physics_engine = None

    def setup(self):

        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = "./maps/map_2/map.tmx"
        # Name of the layer in the file that has our platforms/walls
        walls_layer_name = 'walls'
        # Name of the layer that has floor
        floor_layer_name = 'floor'
        # Name of the layer that has deadly tiles
        deadly_layer_name = "toxic"

        my_map = arcade.tilemap.read_tmx(map_name)
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=walls_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        #-- Floor
        self.floor_list = arcade.tilemap.process_layer(
            my_map, floor_layer_name, TILE_SCALING)
        #-- Deadly
        self.deadly_list = arcade.tilemap.process_layer(
            my_map, deadly_layer_name, TILE_SCALING)

        self.all_sprites.extend(self.deadly_list)
        self.all_sprites.extend(self.floor_list)  # extend appends spriteList
        self.all_sprites.extend(self.wall_list)

        # Player setups
        self.player1 = Player("sprites/duck_small.png", 0.2, MOVE_MAP_PLAYER_1)
        self.player1.center_y = self.window.height / 2
        self.player1.left = 100

        self.players.append(self.player1)

        # Player - wall Collisions
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player1, self.wall_list)

        # self.all_sprites.append(player1)

    def on_draw(self):
        """Called whenever you need to draw your window
        """

        # Clear the screen and start drawing
        arcade.start_render()
        self.all_sprites.draw()
        self.bullets.draw()
        for player in self.players:
            num_dashes = int(player.health/10)
            text = f"|"+'-'*num_dashes+' '*(10-num_dashes)+'|'
            arcade.draw_text(text, 30, SCREEN_HEIGHT-35, arcade.color.ANTI_FLASH_WHITE, 20)
        self.players.draw()

    def on_update(self, delta_time):

        # Bullet bounces
        for bullet in self.bullets:
            bounced = False
            bullet.center_x += bullet.change_x

            walls_hit = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            for wall in walls_hit:
                if bullet.change_x > 0:
                    bullet.right = wall.left
                elif bullet.change_x < 0:
                    bullet.left = wall.right

            if len(walls_hit) > 0:
                bullet.change_x *= -1
                bullet.bounces += 1
                bounced = True

            bullet.center_y += bullet.change_y

            walls_hit = arcade.check_for_collision_with_list(
                bullet, self.wall_list)

            for wall in walls_hit:
                if bullet.change_y > 0:
                    bullet.top = wall.bottom
                elif bullet.change_y < 0:
                    bullet.bottom = wall.top

            if len(walls_hit) > 0:
                bullet.change_y *= -1
                bullet.bounces += 1
                bounced = True

            if bounced == True:
                angle = math.atan2(bullet.change_y, bullet.change_x)
                bullet.angle = math.degrees(angle)

            players_hit=arcade.check_for_collision_with_list(bullet,self.players)
            for player in players_hit:
                player.take_damage(10)
                bullet.destroy()

        for player in self.players:
            if player.collides_with_list(self.deadly_list):
                player.take_damage(10)
            

        for player in self.players:
            player.update(delta_time)

        hit_list = self.physics_engine.update()
        if len(hit_list) > 0:
            self.player1.collided = True
        else:
            self.player1.collided = False

        self.all_sprites.update()
        
        

    def on_key_press(self, key, modifiers):

        for player in self.players:
            sprite = player.on_key_press(key, modifiers)
            if sprite != None:
                self.bullets.append(sprite)
                self.all_sprites.append(sprite)

    def on_key_release(self, key, modifiers):

        for player in self.players:
            player.on_key_release(key, modifiers)

class MenuView(arcade.View):

    def __init__(self):
        super().__init__()

        self.playscreen = arcade.load_texture("sprites/play.png")
        self.optionscreen = arcade.load_texture("sprites/options.png")
        self.quitscreen = arcade.load_texture("sprites/quit.png")

        self.screenlist = [self.playscreen, self.optionscreen, self.quitscreen]
        self.currentselection = 0
        
    
    def on_draw(self):
        arcade.start_render()
        
        self.screenlist[self.currentselection].draw_sized(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_key_press(self, key, modifiers):
        
        if key == arcade.key.S:
            self.currentselection = (self.currentselection + 1) % 3
        
        if key == arcade.key.W:
            self.currentselection = (self.currentselection - 1) % 3
        
        if key == arcade.key.ENTER:
            if self.currentselection == 0:
                game_view = GameView()
                window.show_view(game_view)
                game_view.setup()
                self.window.show_view(game_view)

            elif self.currentselection == 2:
                self.window.close()
        

# Main code entry point
if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = MenuView()
    window.show_view(start_view)
    arcade.run()
