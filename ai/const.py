
# Network specifications
GRID_WIDTH = 56
GRID_HEIGHT = 32
NUM_ACTIONS = 36
INPUT_TIME_FRAME = 1
WEIGHTS_SAVE = "ai/weights/network_weights"
# ENVIRONMENT,PLAYERS,BULLETS,PAST BUlLETS1-3
INPUT_CHANNELS = 3 + INPUT_TIME_FRAME
HIDDEN_LAYER = 128
LEARNING_RATE = .2

# Training Variables
WAIT_UNTIL = 100
ITERATIONS_PER_EPOCH = 1000
EPSILON_START = .9
EPSILON_STEPS = 200
EPSILON_END = .05
EPSILON_DECREASE = (EPSILON_START-EPSILON_END)/EPSILON_STEPS
FUTURE_DISCOUNT = .9
REWARD_HIT = 20
REWARD_SELF_HIT = -10
REWARD_SHOT = -5
REWARD_PASSIVE = 0
DEATH_REWARD = -100
DECREASING_DISTANCE_R = 5
KILL_REWARD = 1000

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
