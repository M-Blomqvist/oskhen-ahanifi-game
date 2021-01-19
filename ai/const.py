
# Network specifications
GRID_WIDTH = 56
GRID_HEIGHT = 32
NUM_ACTIONS = 36
INPUT_TIME_FRAME = 3
# ENVIRONMENT,PLAYERS,BULLETS,PAST BUlLETS1-3
INPUT_CHANNELS = 3 + INPUT_TIME_FRAME
HIDDEN_LAYER = 512
LEARNING_RATE = .2

# Training Variables
WAIT_UNTIL = 100
ITERATIONS_PER_EPOCH = 1000
TRAINING_EPOCHS = 1000
EXPLORATION_E = 0.1
FUTURE_DISCOUNT = .9
REWARD_HIT = 4
REWARD_SELF_HIT = -4
REWARD_PASSIVE = 0
DEATH_REWARD = -100
KILL_REWARD = 50

# For memory batching
MEMORY_SIZE = 5000
BATCH_SIZE = 10

STRING_VALUE_MAP = {
    "walls": 0,
    "floor": 1,
    "deadly": 2,
    "own_player": 3,
    "enemy_player": 4,
}

# initialy only do one action at a time.
VALUE_TO_ACTION = [[(0, 0), (1, 0), (2, 0), (3, 0)],
                   [(0, 0), (1, 0), (2, 1), (3, 0)],
                   [(0, 0), (1, 0), (2, 0), (3, 1)],
                   [(0, 0), (1, 0), (2, 1), (3, 1)],
                   [(0, 1), (1, 0), (2, 0), (3, 0)],
                   [(0, 1), (1, 0), (2, 1), (3, 0)],
                   [(0, 1), (1, 0), (2, 0), (3, 1)],
                   [(0, 1), (1, 0), (2, 1), (3, 1)],
                   [(0, 2), (1, 0), (2, 0), (3, 0)],
                   [(0, 2), (1, 0), (2, 1), (3, 0)],
                   [(0, 2), (1, 0), (2, 0), (3, 1)],
                   [(0, 2), (1, 0), (2, 1), (3, 1)],
                   [(0, 0), (1, 1), (2, 0), (3, 0)],
                   [(0, 0), (1, 1), (2, 1), (3, 0)],
                   [(0, 0), (1, 1), (2, 0), (3, 1)],
                   [(0, 0), (1, 1), (2, 1), (3, 1)],
                   [(0, 1), (1, 1), (2, 0), (3, 0)],
                   [(0, 1), (1, 1), (2, 1), (3, 0)],
                   [(0, 1), (1, 1), (2, 0), (3, 1)],
                   [(0, 1), (1, 1), (2, 1), (3, 1)],
                   [(0, 2), (1, 1), (2, 0), (3, 0)],
                   [(0, 2), (1, 1), (2, 1), (3, 0)],
                   [(0, 2), (1, 1), (2, 0), (3, 1)],
                   [(0, 2), (1, 1), (2, 1), (3, 1)],
                   [(0, 0), (1, 2), (2, 0), (3, 0)],
                   [(0, 0), (1, 2), (2, 1), (3, 0)],
                   [(0, 0), (1, 2), (2, 0), (3, 1)],
                   [(0, 0), (1, 2), (2, 1), (3, 1)],
                   [(0, 1), (1, 2), (2, 0), (3, 0)],
                   [(0, 1), (1, 2), (2, 1), (3, 0)],
                   [(0, 1), (1, 2), (2, 0), (3, 1)],
                   [(0, 1), (1, 2), (2, 1), (3, 1)],
                   [(0, 2), (1, 2), (2, 0), (3, 0)],
                   [(0, 2), (1, 2), (2, 1), (3, 0)],
                   [(0, 2), (1, 2), (2, 0), (3, 1)],
                   [(0, 2), (1, 2), (2, 1), (3, 1)]]
