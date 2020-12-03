import arcade
import math
from pymunk.vec2d import Vec2d
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Welcome to Arcade"
SCALING= 2.0

# Classes

class Bullet(arcade.Sprite):
    def __init__(self,filename,scaling,max_bounces):
        super().__init__(filename,scaling)
        self.bounces=0
        self.max_bounces=max_bounces
    
    def update(self):
        if self.bounces>self.max_bounces:
            self.remove_from_sprite_lists()


class Shooter(arcade.Window):
    """Main welcome window
    """
    def __init__(self):
        """Initialize the window
        """
        # Call the parent class constructor
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        self.bullets= arcade.SpriteList()
        self.wall_list=arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        # Set the background window

    def setup(self):
        arcade.set_background_color(arcade.color.PURPLE_MOUNTAIN_MAJESTY)

        bullet=Bullet("./sprites/weapon_gun.png",SCALING,3)
        bullet.center_y = self.height / 2
        bullet.left = 200
        bullet.change_x=3
        bullet.change_y=1

        sprite=arcade.Sprite("./sprites/tile_42.png")
        num_of_tiles_y=math.ceil(SCREEN_HEIGHT/sprite.height)
        num_of_tiles_x=math.ceil(SCREEN_WIDTH/sprite.width)
        
        for i in range(num_of_tiles_y):
            wall=arcade.Sprite("./sprites/tile_42.png")
            wall.center_y=i*sprite.height
            wall.left=0
            self.wall_list.append(wall)
            self.all_sprites.append(wall)

            wall=arcade.Sprite("./sprites/tile_42.png")
            wall.center_y=i*sprite.height
            wall.right=num_of_tiles_x*sprite.width-(sprite.height/2)
            self.wall_list.append(wall)
            self.all_sprites.append(wall)

        for i in range(num_of_tiles_x):
            wall=arcade.Sprite("./sprites/tile_42.png")
            wall.center_x=i*sprite.width
            wall.bottom=0
            self.wall_list.append(wall)
            self.all_sprites.append(wall)

            wall=arcade.Sprite("./sprites/tile_42.png")
            wall.center_x=i*sprite.width
            wall.top=num_of_tiles_y*sprite.width-(sprite.width/2)
            self.wall_list.append(wall)
            self.all_sprites.append(wall)

        
        
        self.bullets.append(bullet)
        self.all_sprites.append(bullet)


    def on_draw(self):
        """Called whenever you need to draw your window
        """

        # Clear the screen and start drawing
        arcade.start_render()

        self.all_sprites.draw()

    def on_update(self, delta_time):
        for bullet in self.bullets:
            bullet.center_x += bullet.change_x
            walls_hit = arcade.check_for_collision_with_list(bullet, self.wall_list)
            for wall in walls_hit:
                if bullet.change_x > 0:
                    bullet.right = wall.left
                elif bullet.change_x < 0:
                    bullet.left = wall.right
            if len(walls_hit) > 0:
                bullet.change_x *= -1
                bullet.bounces+=1

            bullet.center_y += bullet.change_y
            walls_hit = arcade.check_for_collision_with_list(bullet, self.wall_list)
            for wall in walls_hit:
                if bullet.change_y > 0:
                    bullet.top = wall.bottom
                elif bullet.change_y < 0:
                    bullet.bottom = wall.top
            if len(walls_hit) > 0:
                bullet.change_y *= -1
                bullet.bounces+=1

        self.all_sprites.update()



# Main code entry point
if __name__ == "__main__":
    app = Shooter()
    app.setup()
    arcade.run()