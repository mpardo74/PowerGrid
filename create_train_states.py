import pickle
from os import listdir
from random import choice
from agent_nn import Agent_NN
import numpy as np

import config

def create_sets(type, batch_size, i, states_per_loop):
    states = {}
    dummy_ai = Agent_NN()

    for j in range(states_per_loop):
        states[j] = {'states': [],
                     'target_results': []}

    for b in range(batch_size):
        game_file = choice(listdir(type))
        
        with open(type + '\\' + game_file, 'rb') as input_file:
            game_memory = pickle.load(input_file)
            
        move_num = np.random.randint(len(game_memory.game_results), size = states_per_loop)
            
        for j in range(states_per_loop):
            perspective = np.random.randint(4, size = 1)[0]
            nn = dummy_ai.build_nn_input(game_memory.states[move_num[j]][1], perspective)
            
            p_order = (4 + perspective - game_memory.states[move_num[j]][0]) % 4
            
            states[j]['states'].append(nn[0])
            states[j]['target_results'].append([game_memory.game_results[move_num[j]][p_order]])
    
    for j in range(states_per_loop):    
        file_output = {}
        file_output['batch_states'] = np.array(states[j]['states'])
        file_output['batch_targets'] = [np.array(states[j]['target_results'])]
        
        if type == 'training':
            with open('train_states\\states' + str(states_per_loop * i + j) + '.pkl', 'wb') as output_file:
                pickle.dump(file_output, output_file, -1)
        else:
            with open('validation_states\\states' + str(states_per_loop * i + j) + '.pkl', 'wb') as output_file:
                pickle.dump(file_output, output_file, -1)