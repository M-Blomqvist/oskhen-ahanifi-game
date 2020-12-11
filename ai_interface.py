import arcade
import logic
import importlib.util
import numpy as np


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


class Agent():
    def __init__(self,action_key_map,ai_script):
        self.ai_module=self.load_module(ai_script)
        self.action_key_map=action_key_map
        self.action_space=[3,3,2,2]
        self.get_action_key

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



