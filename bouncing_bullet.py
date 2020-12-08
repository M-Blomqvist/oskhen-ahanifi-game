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

TILE_SCALING = 1.5

# Classes

class Shooter(arcade.Window):
    """Main welcome window
    """

    def __init__(self):
        """Initialize the window
        """
        # Call the parent class constructor
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

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
        map_name = "./maps/map_1/map.tmx"
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

        bullet = Bullet("./sprites/weapon_gun.png", SCALING, 3)
        bullet.center_y = self.height / 2
        bullet.left = 200
        bullet.change_x = BULLET_SPEED
        bullet.change_y = BULLET_SPEED

        self.bullets.append(bullet)
        self.all_sprites.append(bullet)

        # Player setups
        self.player1 = Player("sprites/duck_small.png", 0.2, MOVE_MAP_PLAYER_1)
        self.player1.center_y = self.height / 2
        self.player1.left = 100

        self.players.append(self.player1)

        # Player - wall Collisions
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player1, self.wall_list)

        self.time_since_dmg = 10000
        # self.all_sprites.append(player1)

    def on_draw(self):
        """Called whenever you need to draw your window
        """

        # Clear the screen and start drawing
        arcade.start_render()
        self.all_sprites.draw()
        self.bullets.draw()

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

        if self.player1.collides_with_list(self.deadly_list):
            self.player1.color = arcade.color.AFRICAN_VIOLET
            self.player1.take_damage(10)
        else:
            self.player1.color = arcade.color.NON_PHOTO_BLUE

        self.player1.update(delta_time)

        hit_list = self.physics_engine.update()
        if len(hit_list) > 0:
            self.player1.collided = True
        else:
            self.player1.collided = False

        self.all_sprites.update()

    def on_key_press(self, key, modifiers):

        if key == arcade.key.N:
            bullet = self.player2.shoot()
            self.bullets.append(bullet)
            self.all_sprites.append(bullet)

        for player in self.players:
            sprite = player.on_key_press(key, modifiers)
            if sprite != None:
                self.bullets.append(sprite)
                self.all_sprites.append(sprite)

    def on_key_release(self, key, modifiers):

        for player in self.players:
            player.on_key_release(key, modifiers)


# Main code entry point
if __name__ == "__main__":
    app = Shooter()
    app.setup()
    arcade.run()
