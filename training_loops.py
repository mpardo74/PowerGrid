import numpy as np

from create_train_states import create_sets
from train_network import train_network
import config

from agent_nn import Agent_NN

training_passes = [('general', 'value')]
agents_to_train = [6, 5]
new_agents = [9, 10]

# New combinations
agents = []
for a in agents_to_train:
    agent_object = Agent_NN()
    agent_object.nn_read(a)
    agents.append(agent_object)
    
new_agent_breed = Agent_NN()

nn0 = agents[0].nn
nn1 = agents[1].nn
nn_new = new_agent_breed.nn

break_point = np.random.randint(len(nn0.model.layers))

for i in range(len(nn0.model.layers)):
    if i < break_point:
        nn_new.model.set_weights(nn0.model.get_weights())
    else:
        nn_new.model.set_weights(nn1.model.get_weights())

# Randomize layer            
for i, new_networks in enumerate([new_agent_breed, agents[0]]):
    try:
        random_layer = np.random.randint(len(new_networks.nn.model.layers))
        required_shape = new_networks.nn.model.layers[random_layer].shape
        new_networks.nn.model.layers[random_layer].set_weights(np.random.randn(required_shape))
    except:
        pass
        
    new_networks.nn_write(new_agents[i])

# Create states
val_states_per_loop = 0
val_number_of_sets = 0
states_per_loop = 10
number_of_sets = 2

for net, head in training_passes:
    # Validation
    for i in range(val_number_of_sets):
        print ("Validation Iteration #" + str(i))
        create_sets('validation', config.VALIDATION_BATCH_SIZE, i, val_states_per_loop)

    # Training
    for i in range(number_of_sets):
        print ("Iteration #" + str(i))
        create_sets('training', config.TRAIN_BATCH_SIZE, i, states_per_loop)
        
    for a in new_agents:
        print ("Training Agent: " + str(a))
        train_network(a)