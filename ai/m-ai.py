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


# Network for both agents
model = None
network_loss = 0
dictionary = None
setup = True

# Memory for batching and less overfitted AI
experience_memory = deque(maxlen=MEMORY_SIZE)
previous_s_a = (None, None)

# timestep for training
time_step = 0

# short-term memory for perception of time
stacked_frames = deque([np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=np.int)
                        for i in range(STACKED_FRAMES)], maxlen=STACKED_FRAMES)

# create NN


def network_setup():
    global model
    model = Sequential()
    """ model.add(Conv2D(32, kernel_size=(8, 8), strides=(
        4, 4), activation='relu', input_shape=(GRID_WIDTH, GRID_HEIGHT, STACKED_FRAMES)))
    model.add(MaxPooling2D(pool_size=(4, 4), strides=(2, 2), padding='same'))
    model.add(Conv2D(64, kernel_size=(4, 4), strides=(2, 2), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(1, 1), padding='same'))
    model.add(Flatten())
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(NUM_ACTIONS))
    model.compile(loss='mse', optimizer='adam') """

 # simple non-convolutional
    model.add(Flatten())
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(HIDDEN_LAYER, activation='relu'))
    model.add(Dense(NUM_ACTIONS))
    model.compile(SGD(lr=LEARNING_RATE), "mse")

# observation preprocessing

# process observation into int-state (0-5) 56x32 + reward


def process_observtions(observation, player):
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

    return np_state, reward


def predict(agent, observations, action_space):
    global p1_name
    if model == None:
        network_setup()
        # print(model.summary())
        p1_name = agent.player.name
    # parse and format observations
    state, reward = process_observtions(observations, agent.player)

    # If game just started, send in four stacked copies of initial state
    global setup
    global stacked_frames
    global players_health
    if setup:
        stacked_frames.append(state)
        stacked_frames.append(state)
        stacked_frames.append(state)
        stacked_frames.append(state)
        stacked_states = np.stack(stacked_frames, axis=2)
        stacked_states = stacked_states.reshape(
            1, stacked_states.shape[0], stacked_states.shape[1], stacked_states.shape[2])  # 1*num_of_cols*num_of_rows*4
        setup = False
    # otherwise stack new state on
    else:
        global previous_s_a
        state = state.reshape(1, state.shape[0], state.shape[1], 1)
        stacked_states = np.append(
            state, previous_s_a[0][:, :, :, :STACKED_FRAMES-1], axis=3)
        global experience_memory
        experience_memory.append(
            (previous_s_a[0], previous_s_a[1], reward, stacked_states))

    global time_step
    if (time_step < WAIT_UNTIL) | (random.random() < EXPLORATION_E):
        action = VALUE_TO_ACTION[random.randint(0, len(VALUE_TO_ACTION)-1)]
    else:
        # Training
        training_batch = random.sample(
            experience_memory, BATCH_SIZE)

        inputs = np.zeros(
            (BATCH_SIZE, stacked_states.shape[1], stacked_states.shape[2], stacked_states.shape[3]))
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

        # Predict new action
        q = model.predict(stacked_states)
        action = VALUE_TO_ACTION[np.argmax(q[0])]
    previous_s_a = (stacked_states, action)
    time_step += 1
    print(action)
    return action
