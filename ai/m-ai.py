# OBSERVATIONS: [[[terrain, player/bullet(bill)]; 32];56]
# action_space: [0-2, 0-2, 0-1, 0-1] == [move_up/down/not y, move_right/left_notx, shoot/dont, dash/dont]
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.models import Sequential
from tensorflow import keras
import os.path
import random
import tensorflow as tf
import numpy as np
import json
from collections import deque
from ai.const import (GRID_WIDTH, GRID_HEIGHT, NUM_ACTIONS, INPUT_TIME_FRAME, INPUT_CHANNELS, HIDDEN_LAYER, WAIT_UNTIL, ITERATIONS_PER_EPOCH, EPSILON_STEPS, EPSILON_START, EPSILON_END, EPSILON_DECREASE,
                      FUTURE_DISCOUNT, REWARD_HIT, REWARD_SELF_HIT, REWARD_SHOT, REWARD_PASSIVE, DEATH_REWARD, DECREASING_DISTANCE_R, KILL_REWARD, MEMORY_SIZE, BATCH_SIZE, STRING_VALUE_MAP, VALUE_TO_ACTION, WEIGHTS_SAVE)

# import pytest
new_ai = True
setup = True
# timestep for training
time_step = 0
epsilon = EPSILON_START

# Memory for batching & training


class agent_memory():

    def __init__(self, name):
        self.name = name
        self.experience_memory = deque(maxlen=MEMORY_SIZE)
        self.previous_s_a = (None, None)
        self.distance_to_enemy = 0
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
    model.add(Conv2D(34, kernel_size=(6, 6), strides=(
        1, 1), activation='relu', input_shape=(GRID_WIDTH, GRID_HEIGHT, INPUT_CHANNELS)))
    model.add(MaxPooling2D(pool_size=(3, 3), strides=(3, 3), padding='same'))
    model.add(Flatten())
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(NUM_ACTIONS))
    model.compile(loss='mse', optimizer='adam')
    if len(os.listdir(WEIGHTS_SAVE[:-16])) != 0:
        print("Weights found, trying to load")
        model.load_weights(WEIGHTS_SAVE)
    print(model.summary())
    return model

 # simple non-convolutional
"""     model.add(Flatten())
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(NUM_ACTIONS))
    model.compile(SGD(lr=LEARNING_RATE), "mse") """


def train(network):
    # Training
    training_batch = random.sample(
        agent_memory.experience_memory, BATCH_SIZE)

    inputs = np.zeros(
        (BATCH_SIZE, GRID_WIDTH, GRID_HEIGHT, INPUT_CHANNELS))
    targets = np.zeros((inputs.shape[0], NUM_ACTIONS))
    for i in range(0, len(training_batch)):
        state_t = training_batch[i][0]
        action_t = training_batch[i][1]
        reward_t = training_batch[i][2]
        state_t1 = training_batch[i][3]
        inputs[i:i + 1] = state_t
        targets[i] = network.predict(state_t)
        Q_sa = network.predict(state_t1)
        targets[i, action_t] = reward_t + FUTURE_DISCOUNT * np.max(Q_sa)
    network_loss = network.train_on_batch(inputs, targets)
    return network_loss


# observation preprocessing

# process observation into int-state 56x32xINPUTCHANNELS(3 filled)  + reward


def process_observtions(observation, player_name):
    reward = REWARD_PASSIVE
    player_pos = None
    enemy_pos = None
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
            bullet_person = observation[i][j][1]
            if type(bullet_person).__name__ == "Bullet":
                third = 1
            elif bullet_person == '':
                second = 0
                third = 0
            elif bullet_person.name == player_name:
                if bullet_person.shot_by == player_name:
                    reward += REWARD_SELF_HIT
                elif bullet_person.shot_by != None:
                    reward += REWARD_SHOT
                if bullet_person.health <= 0:
                    reward += DEATH_REWARD
                player_pos = (i, j)
                second = 1
                third = 0
            else:
                if bullet_person.shot_by == player_name:
                    reward += REWARD_HIT
                if bullet_person.health <= 0:
                    reward += KILL_REWARD
                enemy_pos = (i, j)
                second = -1
                third = 0
            np_state[i][j][:3] = [first, second, third]
    distance_to_enemy = abs(
        (enemy_pos[0] - player_pos[0])) + abs((enemy_pos[1]-player_pos[1]))
    if distance_to_enemy < agent_memory.distance_to_enemy:
        reward += DECREASING_DISTANCE_R
    if distance_to_enemy > agent_memory.distance_to_enemy:
        reward -= DECREASING_DISTANCE_R
    agent_memory.distance_to_enemy = distance_to_enemy
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


def predict(agent, network, observations, action_space):
    # parse and format observations
    state, reward = process_observtions(observations, agent.name)
    stacked_frames = agent_memory.stacked_frames
    previous_s_a = agent_memory.previous_s_a
    # If game just started, send in stacked copies of initial state of bullets
    global setup
    if setup:
        print("First time predicting")
        for i in range(INPUT_TIME_FRAME):
            stacked_frames.append(state[:, :, 2])
        for i in range(INPUT_TIME_FRAME):
            state[:, :, (INPUT_CHANNELS-INPUT_TIME_FRAME)] = stacked_frames[i]
        stacked_state = state.reshape(
            1, state.shape[0], state.shape[1], state.shape[2])
        setup = False
    # otherwise stack new bullet state on
    else:
        stacked_frames.append(state[:, :, 2])
        for i in range(INPUT_TIME_FRAME):
            state[:, :, (INPUT_CHANNELS-INPUT_TIME_FRAME)] = stacked_frames[i]
        stacked_state = state.reshape(
            1, state.shape[0], state.shape[1], state.shape[2])
        agent_memory.add_memory(
            (previous_s_a[0], previous_s_a[1], reward, stacked_state))

    global time_step
    global epsilon
    if epsilon > EPSILON_END:
        epsilon -= EPSILON_DECREASE
    network_loss = 0
    global loaded_weights
    if ((time_step < WAIT_UNTIL) & new_ai) | (random.random() < epsilon):
        action = VALUE_TO_ACTION[random.randint(0, len(VALUE_TO_ACTION)-1)]
    elif time_step >= ITERATIONS_PER_EPOCH:
        print(agent.network_loss)
        print("Preparing reset... Saving Weights")
        network.save_weights(WEIGHTS_SAVE)
        agent.player.lives = 0
        agent.player.die()
        action = VALUE_TO_ACTION[random.randint(0, len(VALUE_TO_ACTION)-1)]
    else:
        if time_step > BATCH_SIZE:
            network_loss = train(network)
        # Predict new action
        q = network.predict(stacked_state)
        action = VALUE_TO_ACTION[np.argmax(q[0])]
    agent_memory.set_prev_sa(stacked_state, action)
    if time_step % 100 == 0:
        print(time_step)
    time_step += 1
    return action, network_loss
