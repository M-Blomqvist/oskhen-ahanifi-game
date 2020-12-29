import numpy as np
from matplotlib import pyplot as plt
import parseconf

# input 56x32x1

## Dynamic names
settings = parseconf.parsefile()

P1_NAME = settings["p1_name"]
P2_NAME = settings["p2_name"]
PLAYER_NAME = P2_NAME

STRING_VALUE_MAP = {
    "walls": 0,
    "floor": 1,
    "deadly": 2,
    "own_player": 3,
    "enemy_player": 4,
}

def string_state_to_int_state(state):
    players_health = [0,0]
    np_state = np.zeros((len(state), len(state[0])), dtype=np.uint8)
    for i in range(np_state.shape[0]):
        for j in range(np_state.shape[1]):
            if state[i][j][1] != '':
                if type(state[i][j][1]).__name__ != "Bill":
                    if state[i][j][1].name==P1_NAME:
                        players_health[0]=state[i][j][1].health
                    else:
                        players_health[1]=state[i][j][1].health
                    np_state[i, j] = 5
                elif type(state[i][j][1]).__name__ == "Bill":
                    np_state[i, j] = 6
            else:
                np_state[i, j] = STRING_VALUE_MAP[state[i][j][0]]

    return np_state,players_health


def predict(observations, action_space):

    current_s,current_players_health= string_state_to_int_state(observations)
    print(observations)
    plt.imshow(np.rot90(current_s))
    plt.gray()
    plt.show()








    actions = action_space.sample()

    return actions
