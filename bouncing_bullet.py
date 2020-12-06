import arcade
import math
from pymunk.vec2d import Vec2d

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Under Development"
SCALING = 0.1
PLAYER_1_SPEED = 5
PLAYER_2_SPEED = 3

TILE_SCALING = 1.5

MOVE_MAP_PLAYER_1 = {
    arcade.key.W: Vec2d(0, 1),
    arcade.key.S: Vec2d(0, -1),
    arcade.key.A: Vec2d(-1, 0),
    arcade.key.D: Vec2d(1, 0),
}

MOVE_MAP_PLAYER_2 = {
    arcade.key.I: Vec2d(0, 1),
    arcade.key.K: Vec2d(0, -1),
    arcade.key.J: Vec2d(-1, 0),
    arcade.key.L: Vec2d(1, 0),
}

# Classes


class Bullet(arcade.Sprite):
    def __init__(self, filename, scaling, max_bounces, speed=5):
        super().__init__(filename, scaling)
        self.bounces = 0
        self.max_bounces = max_bounces
        self.speed = speed

    def update(self):
        if self.bounces > self.max_bounces:
            self.remove_from_sprite_lists()


class Player(arcade.Sprite):
    def __init__(self, filename, scaling, health=100):
        super().__init__(filename, scaling)
        self.health = health
        self.move_direction = Vec2d(0, 0)
        self.facing_direction = Vec2d(1, 0)

    def shoot(self):
        bullet = Bullet("./sprites/weapon_gun.png", 1, 3)
        bullet.change_x = self.facing_direction.x * bullet.speed
        bullet.change_y = self.facing_direction.y * bullet.speed

        start_x = self.player1.center_x
        start_y = self.player1.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y
        angle = math.atan2(self.facing_direction.y/self.facing_direction.x)

        bullet.angle = math.degrees(angle)

        self.bullets.append(bullet)
        self.all_sprites.append(bullet)


class Shooter(arcade.Window):
    """Main welcome window
    """

    def __init__(self):
        """Initialize the window
        """
        # Call the parent class constructor
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.move_keys_1_pressed = {k: False for k in MOVE_MAP_PLAYER_1}
        self.move_keys_2_pressed = {k: False for k in MOVE_MAP_PLAYER_2}

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

        #points= arcade.PointList(arcade.Point((1,1)),arcade.Point((1,0)),arcade.Point((0,1)),arcade.Point((0,0)))

        #-- Floor
        self.floor_list = arcade.tilemap.process_layer(
            my_map, floor_layer_name, TILE_SCALING)
        #-- Deadly
        self.deadly_list = arcade.tilemap.process_layer(
            my_map, deadly_layer_name, TILE_SCALING)

        self.all_sprites.extend(self.deadly_list)
        self.all_sprites.extend(self.floor_list)  # extend appends spriteList
        self.all_sprites.extend(self.wall_list)

        # arcade.set_background_color(arcade.color.PURPLE_MOUNTAIN_MAJESTY)

        bullet = Bullet("./sprites/weapon_gun.png", SCALING, 3)
        bullet.center_y = self.height / 2
        bullet.left = 200
        bullet.change_x = 3
        bullet.change_y = 3

        # sprite = arcade.Sprite("./sprites/tile_42.png")
        # num_of_tiles_y = math.ceil(SCREEN_HEIGHT / sprite.height)
        # num_of_tiles_x = math.ceil(SCREEN_WIDTH / sprite.width)

        # for i in range(num_of_tiles_y):
        #     wall = arcade.Sprite("./sprites/tile_42.png")
        #     wall.center_y = i * sprite.height
        #     wall.left = 0

        #     self.wall_list.append(wall)
        #     self.all_sprites.append(wall)

        #     wall = arcade.Sprite("./sprites/tile_42.png")
        #     wall.center_y = i * sprite.height
        #     wall.right = num_of_tiles_x * sprite.width - (sprite.height / 2)

        #     self.wall_list.append(wall)
        #     self.all_sprites.append(wall)

        # for i in range(num_of_tiles_x):
        #     wall = arcade.Sprite("./sprites/tile_42.png")
        #     wall.center_x = i * sprite.width
        #     wall.bottom = 0

        #     self.wall_list.append(wall)
        #     self.all_sprites.append(wall)

        #     wall = arcade.Sprite("./sprites/tile_42.png")
        #     wall.center_x = i * sprite.width
        #     wall.top = num_of_tiles_y * sprite.width - (sprite.width / 2)

        #     self.wall_list.append(wall)
        #     self.all_sprites.append(wall)

        self.bullets.append(bullet)
        self.all_sprites.append(bullet)

        # Player setups
        self.move_direction = Vec2d(0, 0)
        self.facing_direction = Vec2d(1, 0)

        self.player1 = arcade.Sprite("sprites/duck_small.png", 0.2)
        self.player1.center_y = self.height / 2
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
        else:
            self.player1.color = arcade.color.NON_PHOTO_BLUE

        self.player1.change_y = self.move_direction.y*PLAYER_1_SPEED
        self.player1.change_x = self.move_direction.x*PLAYER_1_SPEED

        self.physics_engine.update()

        self.all_sprites.update()

    def on_key_press(self, key, modifiers):

        if key == arcade.key.SPACE:
            self.spawn_bullet()

        if key in self.move_keys_1_pressed:
            self.move_keys_1_pressed[key] = True
            self.move_direction = sum(
                self.move_keys_1_pressed[k] * MOVE_MAP_PLAYER_1[k] for k in self.move_keys_1_pressed).normalized()  
            self.player1.change_y = self.move_direction.y * PLAYER_1_SPEED
            self.player1.change_x = self.move_direction.x * PLAYER_1_SPEED

            if self.move_direction != Vec2d(0, 0):
                self.facing_direction = self.move_direction
              

    def on_key_release(self, key, modifiers):
        if key in self.move_keys_1_pressed:
            self.move_keys_1_pressed[key] = False
            self.move_direction = sum(
                self.move_keys_1_pressed[k] * MOVE_MAP_PLAYER_1[k] for k in self.move_keys_1_pressed).normalized()
            self.player1.change_y = self.move_direction.y * PLAYER_1_SPEED
            self.player1.change_x = self.move_direction.x * PLAYER_1_SPEED

            if self.move_direction != Vec2d(0, 0):
                self.facing_direction = self.move_direction


    def spawn_bullet(self):
        bullet = Bullet("./sprites/weapon_gun.png", 1, 3)
        bullet.change_x = self.facing_direction.x * bullet.speed
        bullet.change_y = self.facing_direction.y * bullet.speed

        start_x = self.player1.center_x
        start_y = self.player1.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        angle = math.atan2(self.facing_direction.y, self.facing_direction.x)
        bullet.angle = math.degrees(angle)

        self.bullets.append(bullet)
        self.all_sprites.append(bullet)


# Main code entry point
if __name__ == "__main__":
    app = Shooter()
    app.setup()
    arcade.run()
