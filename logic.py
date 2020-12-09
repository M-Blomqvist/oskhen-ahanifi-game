import arcade
from pymunk.vec2d import Vec2d
import math
from dataclasses import dataclass
import time





@dataclass
class Cooldown():
    cooldown: float
    last_used: float=0
    def ready(self):
        if time.time()-self.last_used>self.cooldown:
            return True
        else:
            return False
    def use(self):
        self.last_used=time.time()

COOLDOWNS ={
    "DashState": Cooldown(2),
    "shoot":(Cooldown(0.5))
} 

class Bullet(arcade.Sprite):
    def __init__(self, filename, scaling, max_bounces, speed=7):
        super().__init__(filename, scaling)
        self.bounces = 0
        self.max_bounces = max_bounces
        self.speed = speed
        #self.color = arcade.color.BRIGHT_GREEN

    def update(self):
        if self.bounces > self.max_bounces:
            self.remove_from_sprite_lists()
            
    def destroy(self):
        self.remove_from_sprite_lists()


@dataclass
class InputContext():
    move_map: dict()
    move_keys_pressed: dict()
    key_map: dict()
    abilities_pressed: dict()
    prev_key: arcade.key = None
    time_since_last: float = 0


class DefaultState():
    def __init__(self):
        self.time_since_dmg = 1000

    def update(self, player, delta_time):
        for ability in player.input_context.abilities_pressed:
            if player.input_context.abilities_pressed[ability] == True:
                ability(player)

        self.time_since_dmg += delta_time
        player.input_context.time_since_last += delta_time
        player.change_x = player.move_direction.x*player.speed
        player.change_y = player.move_direction.y*player.speed

    def take_damage(self, player, damage):
        if self.time_since_dmg > 1:
            
            self.time_since_dmg = 0
            player.health -= damage
            if player.health <= 0:
                player.health = 0
                print("I'm legally dead")

            num_dashes = int(player.health/10)
            text = f"|"+'_'*num_dashes+' '*(10-num_dashes)+'|'
            print(text)

    def on_key_press(self, player, key):
        inputs=player.input_context
        inputs.time_since_last = 0
        if key in inputs.move_map:
            inputs.move_keys_pressed[key] = True
            player.move_direction = sum(
                inputs.move_keys_pressed[k] * inputs.move_map[k] for k in inputs.move_keys_pressed).normalized()

            player.change_y = player.move_direction.y * player.speed
            player.change_x = player.move_direction.x * player.speed

            if player.move_direction != Vec2d(0, 0):
                player.facing_direction = player.move_direction

        elif key in inputs.key_map:
            ability = inputs.key_map[key]
            inputs.abilities_pressed[ability]=True
        inputs.prev_key = key
        return

    def on_key_release(self, player, key):
        inputs=player.input_context
        if key in inputs.move_map:
            inputs.move_keys_pressed[key] = False
            player.move_direction = sum(
                inputs.move_keys_pressed[k] * inputs.move_map[k] for k in inputs.move_keys_pressed).normalized()
            player.change_y = player.move_direction.y * player.speed
            player.change_x = player.move_direction.x * player.speed

            if player.move_direction != Vec2d(0, 0):
                player.facing_direction = player.move_direction
        elif key in inputs.key_map:
            inputs.abilities_pressed[inputs.key_map[key]]=False

class DashState(DefaultState):
    def __init__(self, player, dash_time):
        super().__init__()
        player.cooldowns["DashState"].last_used = time.time()
        player.change_y = player.move_direction.y * player.speed*3
        player.change_x = player.move_direction.x * player.speed*3
        self.dash_time = dash_time
        self.time_since_dashed = 0.0

    def update(self, player, delta_time):
        self.time_since_dashed += delta_time
        player.input_context.time_since_last+=delta_time
        if self.time_since_dashed > self.dash_time or player.collided:
            print("end dash")
            player.to_prev_state()

    def on_key_press(self, player, key):
        inputs=player.input_context
        if key in inputs.move_map:
            inputs.move_keys_pressed[key] = True
        elif key in inputs.key_map:
            inputs.abilities_pressed[inputs.key_map[key]]=True
        return

    def on_key_release(self, player, key):
        inputs=player.input_context
        if key in inputs.move_map:
            inputs.move_keys_pressed[key] = False
        elif key in inputs.key_map:
            inputs.abilities_pressed[inputs.key_map[key]]=False
        return

    def take_damage(self, player, damage):
        super().take_damage(player=player, damage=damage)

class Player(arcade.Sprite):
    def __init__(self,arcade, filename, scaling, MOVE_MAP,KEY_MAP, health=100, speed=5):
        super().__init__(filename, scaling)
        self.arcade=arcade
        self.speed = speed
        self.health = health
        self.collided = False
        self.move_direction = Vec2d(0, 0)
        self.facing_direction = Vec2d(1, 0)

        abilities_pressed=dict()
        for k in KEY_MAP:
            abilities_pressed[KEY_MAP[k]]=False

        self.input_context = InputContext(
            MOVE_MAP, {k: False for k in MOVE_MAP},KEY_MAP,abilities_pressed)
       
        self.cooldowns=COOLDOWNS

        self.prev_states = list()
        self.state = DefaultState()

    def update(self, delta_time):
        self.state.update(player=self, delta_time=delta_time)

    def change_state(self, state):
        self.prev_states.append(self.state)
        self.state = state

    def to_prev_state(self):
        # if len(self.prev_states)>0:
        self.state = self.prev_states[-1]
        self.update_direction()
        self.prev_states.pop(len(self.prev_states)-1)

    def shoot(self):
        
        if self.cooldowns["shoot"].ready():
            self.cooldowns["shoot"].use()
            bullet = Bullet("./sprites/weapon_gun_purple.png", 1, 4)
            bullet.change_x = self.facing_direction.x * bullet.speed
            bullet.change_y = self.facing_direction.y * bullet.speed

            start_x = self.center_x+self.width*self.facing_direction.x
            start_y = self.center_y+self.height*self.facing_direction.y
            bullet.center_x = start_x
            bullet.center_y = start_y
            angle = math.atan2(self.facing_direction.y, self.facing_direction.x)

            bullet.angle = math.degrees(angle)

            self.arcade.bullets.append(bullet)
            self.arcade.all_sprites.append(bullet)

    def take_damage(self, damage):
        self.state.take_damage(player=self, damage=damage)

    def on_key_press(self, key, modifiers):
        return self.state.on_key_press(player=self, key=key)

    def on_key_release(self, key, modifiers):
        return self.state.on_key_release(player=self, key=key)

    def update_direction(self):
        self.move_direction = sum(
            self.input_context.move_keys_pressed[k] * self.input_context.move_map[k] for k in self.input_context.move_keys_pressed).normalized()

    def dash(self):
        print("called dash")
        self.cooldowns["DashState"].use()
        self.change_state(DashState(self, 0.10))


MOVE_MAP_PLAYER_1 = {
    arcade.key.W: Vec2d(0, 1),
    arcade.key.S: Vec2d(0, -1),
    arcade.key.A: Vec2d(-1, 0),
    arcade.key.D: Vec2d(1, 0),
}

KEY_MAP_PLAYER_1 = {
    arcade.key.SPACE: Player.shoot,
    arcade.key.LSHIFT: Player.dash,
}

KEY_MAP_PLAYER_2 = {
    arcade.key.PERIOD: Player.shoot,
    arcade.key.MINUS: Player.dash,
}

MOVE_MAP_PLAYER_2 = {
    arcade.key.I: Vec2d(0, 1),
    arcade.key.K: Vec2d(0, -1),
    arcade.key.J: Vec2d(-1, 0),
    arcade.key.L: Vec2d(1, 0),
}