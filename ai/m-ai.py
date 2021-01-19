# OBSERVATIONS: [[[terrain, player/bullet(bill)]; 32];56]
# action_space: [0-2, 0-2, 0-1, 0-1] == [move_up/down/not y, move_right/left_notx, shoot/dont, dash/dont]
from ai.const import *
from collections import deque
import json
import numpy as np
import tensorflow as tf
import random
# import pytest
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.optimizers import SGD

setup = True
# timestep for training
time_step = 0

# Memory for batching & training


class agent_memory():

    def __init__(self, name):
        self.name = name
        self.experience_memory = deque(maxlen=MEMORY_SIZE)
        self.previous_s_a = (None, None)
        # short-term memory for perception of time (only bullets)
        self.stacked_frames = deque([np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=np.int)
                                     for i in range(INPUT_TIME_FRAME)], maxlen=INPUT_TIME_FRAME)

    def add_memory(self, memory):
        self.experience_memory.append(memory)

    def set_prev_sa(self, new_state, new_action):
        self.previous_s_a = (new_state, new_action)


agent_memory = agent_memory("Player 1")


# create NN
def network_setup():
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3), strides=(
        1, 1), activation='relu', input_shape=(GRID_WIDTH, GRID_HEIGHT, INPUT_CHANNELS)))
    model.add(MaxPooling2D(pool_size=(3, 3), strides=(1, 1), padding='same'))
    model.add(Conv2D(64, kernel_size=(3, 3), strides=(1, 1), activation='relu'))
    model.add(MaxPooling2D(pool_size=(3, 3), strides=(1, 1), padding='same'))
    model.add(Flatten())
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(NUM_ACTIONS))
    model.compile(loss='mse', optimizer='adam')
    return model

 # simple non-convolutional
"""     model.add(Flatten())
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(NUM_ACTIONS))
    model.compile(SGD(lr=LEARNING_RATE), "mse") """

# Network for both agents
model = network_setup()
network_loss = 0


def train():
    # Training
    training_batch = random.sample(
        agent_memory, BATCH_SIZE)

    inputs = np.zeros(
        (BATCH_SIZE, GRID_WIDTH, GRID_HEIGHT, INPUT_CHANNELS))
    targets = np.zeros((inputs.shape[0], NUM_ACTIONS))
    for i in range(0, len(training_batch)):
        state_t = training_batch[i][0]
        action_t = training_batch[i][1]
        reward_t = training_batch[i][2]
        state_t1 = training_batch[i][3]
        inputs[i:i + 1] = state_t
        targets[i] = model.predict(state_t)
        Q_sa = model.predict(state_t1)
        targets[i, action_t] = reward_t + FUTURE_DISCOUNT * np.max(Q_sa)
    global network_loss
    network_loss += model.train_on_batch(inputs, targets)


# observation preprocessing

# process observation into int-state 56x32xINPUTCHANNELS(3 filled)  + reward


def process_observtions(observation, player):
    reward = REWARD_PASSIVE
    np_state = np.zeros(
        (len(observation), len(observation[0]), INPUT_CHANNELS), dtype=np.uint8)
    for i in range(np_state.shape[0]):
        for j in range(np_state.shape[1]):
            if observation[i][j] == 'walls':
                first = 1
            elif observation[i][j][0] == 'deadly':
                first = -1
            else:
                first = 0
            if type(observation[i][j][1]).__name__ == "Bullet":
                third = 1
            elif observation[i][j][1] == player.name:
                second = 1
                third = 0
            elif observation[i][j][1] != '':
                second = -1
                third = 0
            else:
                second = 0
                third = 0
            np_state[i][j][:3] = [first, second, third]
    return np_state, reward


""" def process_observtions(observation, player):
    reward = REWARD_PASSIVE
    np_state = np.zeros(
        (len(observation), len(observation[0])), dtype=np.uint8)
    for i in range(np_state.shape[0]):
        for j in range(np_state.shape[1]):
            if observation[i][j][1] != '':
                if type(observation[i][j][1]).__name__ == "Bullet":
                    np_state[i, j] = 5
                else:
                    p = observation[i][j][1]
                    if p.name == player.name:
                        if p.health <= 0:
                            reward = DEATH_REWARD
                        elif p.shot_by == player.name:
                            reward = REWARD_SELF_HIT
                        np_state[i, j] = 3
                    else:
                        if p.shot_by == player.name:
                            if p.health <= 0:
                                reward = KILL_REWARD
                            else:
                                reward = REWARD_HIT
                        np_state[i, j] = 4
            else:
                np_state[i, j] = STRING_VALUE_MAP[observation[i][j][0]]

    return np_state, reward """


def predict(agent, observations, action_space):
    # if model == None:
    # network_setup()
    # print(model.summary())
    # parse and format observations
    state, reward = process_observtions(observations, agent.player)
    stacked_frames = agent_memory.stacked_frames
    previous_s_a = agent_memory.previous_s_a
    # If game just started, send in stacked copies of initial state of bullets
    global setup
    if setup:
        for i in range(INPUT_TIME_FRAME):
            stacked_frames.append(state[:, :, 2])
        for i in range(INPUT_TIME_FRAME, INPUT_CHANNELS):
            state[:, :, i] = stacked_frames[i-INPUT_TIME_FRAME]
        stacked_state = state.reshape(
            1, state.shape[0], state.shape[1], state.shape[2])
        setup = False
    # otherwise stack new bullet state on
    else:
        stacked_frames.append(state[:, :, 2])
        for i in range(INPUT_TIME_FRAME, INPUT_CHANNELS):
            state[:, :, i] = stacked_frames[i-INPUT_TIME_FRAME]
        stacked_state = state.reshape(
            1, state.shape[0], state.shape[1], state.shape[2])
        agent_memory.add_memory(
            (previous_s_a[0], previous_s_a[1], reward, stacked_state))

    global time_step
    if (time_step < WAIT_UNTIL) | (random.random() < EXPLORATION_E):
        action = VALUE_TO_ACTION[random.randint(0, len(VALUE_TO_ACTION)-1)]
    else:

        # Predict new action
        q = model.predict(stacked_state)
        action = VALUE_TO_ACTION[np.argmax(q[0])]
    agent_memory.set_prev_sa(stacked_state, action)
    time_step += 1
    print(action)
    return action
