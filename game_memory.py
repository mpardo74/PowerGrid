import numpy as np
import pickle
import config

class GameMemory():
    def __init__(self, game_uuid):
        self.game_id = game_uuid
        self.states = []
        self.game_results = []
    
    def add_to_memory_states(self, player, state):
        state.nodes = None
        state.connections = None
        state.shortest_paths = None
        self.states.append((player, state))
    
    def add_game_result(self, result):
        for k, s in enumerate(self.states):
            self.game_results.append(np.zeros(5))
            for p in range(5):
                p_order = (5 + p - s[0]) % 5
                self.game_results[k][p_order] = result[p]

    def dump_to_file(self):
        with open(config.folder_self_play + '\\' + str(self.game_id) + '.pkl', 'wb') as output:
            pickle.dump(self, output, -1)
