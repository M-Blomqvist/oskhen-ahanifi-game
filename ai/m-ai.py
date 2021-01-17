# OBSERVATIONS: [[[terrain, player/bullet(bill)]; 32];56]
# action_space: [0-2, 0-2, 0-1, 0-1] == [move_up/down/not y, move_right/left_notx, shoot/dont, dash/dont]
import json
import numpy as np
import tensorflow as tf
import pytest
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD

from collections import deque

# parameters
epsilon = .1  # exploration
num_actions = 36  # four types of actions with three states each
epoch = 100
max_memory = 500
hidden_size = 4000
batch_size = 50
grid_size = 52*32
input_size = 3586
model = None
dictionary = None

# Memory for batching and less over fitted AI
# class ExperienceMemory

# create NN


def network_setup():
    global model
    model = Sequential()
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(num_actions))
    model.compile(SGD(lr=.2), "mse")

# observation preprocessing


def process_observtions(observation, player):
    flat_obs = list()
    for x in observation:
        for e in x:

            if e[0] == "walls":
                first = 1
            elif e[0] == "floor":
                first = 0
            elif e[0] == "deadly":
                first = -1
            if e[1] == '':
                # empty tile
                second = 0
            else:
                if e[1].name == player.name:
                    second = 1
                elif e[1].name == "Bill":
                    first = -1
                else:
                    second = -1
            flat_obs.extend([first, second])
    # add current health to observation
    flat_obs.extend([player.health, player.lives])
    return flat_obs


def gen_dict():
    dictionary = list()
    for y_mov in range(0, 3):
        for x_mov in range(0, 3):
            dictionary.append([(0, x_mov), (1, y_mov), (2, 0), (3, 0)])
            dictionary.append([(0, x_mov), (1, y_mov), (2, 1), (3, 0)])
            dictionary.append([(0, x_mov), (1, y_mov), (2, 0), (3, 1)])
            dictionary.append([(0, x_mov), (1, y_mov), (2, 1), (3, 1)])
    return dictionary


def predict(agent, observations, action_space):
    if model == None:
        global dictionary
        dictionary = gen_dict()
        # print(dictionary)
        # print(len(dictionary))
        network_setup()
    # parse and format observations
    flat_obs = process_observtions(observations, agent.player)

    # print(observations)
    # print(flat_obs)
    f = np.array(flat_obs).reshape(-1, len(flat_obs))
    q = model.predict(f)
    # print(model.get_layer(index=0).input_shape)
    # print(model.summary())
    actions = dictionary[np.argmax(q[0])]
    print(actions)
    return actions
