import arcade
import logic
import importlib.util
import numpy as np
import random
from pymunk import Vec2d



AI_KEYMAP_1={
  (0,0) : None,
  (0,1) : arcade.key.A, # key for left
  (0,2) : arcade.key.D, # key for right
  (1,0) : None,
  (1,1) : arcade.key.W, # key for up
  (1,2) : arcade.key.S, # key for down
  (2,0) : None,
  (2,1) : arcade.key.SPACE, # key for shoot
  (3,0) : None,
  (3,1) : arcade.key.LSHIFT, # key for dash
}

AI_KEYMAP_2={
  (0,0) : None,
  (0,1) : arcade.key.J, # key for left
  (0,2) : arcade.key.L, # key for right
  (1,0) : None,         
  (1,1) : arcade.key.I, # key for up
  (1,2) : arcade.key.K, # key for down
  (2,0) : None,
  (2,1) : arcade.key.PERIOD, # key for shoot
  (3,0) : None,
  (3,1) : arcade.key.MINUS,  # key for dash
}

Value_To_Action={
    Vec2d(0, 1).int_tuple :(1,1),
    Vec2d(0, -1).int_tuple:(1,2),
    Vec2d(-1, 0).int_tuple:(0,1),
    Vec2d(1, 0).int_tuple:(0,2),
    "shoot":(2,1),
    "dash":(3,1),
}


class MultiDiscrete():
    def __init__(self,nvec):
        self.rng=np.random.default_rng()
        self.nvec=nvec
    def sample(self):
        self.rng.random()
        actions=list()
        for i,value in enumerate(self.nvec):
            actions.append((i,random.randint(0,value-1)))

        return actions
class Agent():
    def __init__(self,ai_script,player):
        self.player=player
        self.ai_module=self.load_module(ai_script)
        self.action_space= MultiDiscrete([3,3,2,2])
        self.action_key_map=self.generate_action_keymap(player)

    def set_observation(self,observation):
        self.observation=observation

    def get_action_key(self,actions):
        keys= list()
        for action in actions:
            key=self.action_key_map[action]
            keys.append(key)
        
        return keys

    def predict(self):
        actions=self.ai_module.predict(self.observation,self.action_space)
        return self.get_action_key(actions)
        

    def load_module(self,path):    
        spec = importlib.util.spec_from_file_location("ai_module", path)
        ai_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ai_module)
        return ai_module

    def generate_action_keymap(self,player):
        dict={}

        for key,value in player.input_context.move_map.items():
            action=Value_To_Action[value.int_tuple]
            dict[action]=key
        for key,value in player.input_context.key_map.items():
            action=Value_To_Action[value]
            dict[action]=key

        for i in range(len(self.action_space.nvec)):
            dict[(i,0)]=None

        return dict
 


if __name__ == "__main__":
    ...
    # agent=Agent(AI_KEYMAP_1,"./ai.py")
    # print(agent.action_space.sample())