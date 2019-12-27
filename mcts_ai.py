import numpy as np
from math import sqrt
from copy import copy, deepcopy
from random import shuffle, choice

import config

class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of player_turn.
        Crashes if state not specified.
    """
    def __init__(self, player, parent = None, move = None):
        self.current_player = player
        self.parentNode = parent # "None" for the root node
        self.move = move
        self.childNodes = []
        self.child_moves = []
        self.possible_moves = []
        self.is_random = False
        self.W = 0 # Total value of node
        self.N = 0 # Total visits
        self.Q = 0
        
    def UCTSelectChild(self, weight):
        def evaluation(x):
            return weight * x.Q + (1 - weight) * 0.2 * sqrt(self.N / (0.01 + x.N))

        potential_moves = []
        
        for m in self.possible_moves:
            n = self.childNodes[self.child_moves.index(m)]
            potential_moves.append(n)
        
        s = sorted(potential_moves, key = evaluation )
        try:
            return s[-1]
        except:
            raise Exception("No moves found. Move: " + str(self.move) + "; Possible_moves: " + str(self.possible_moves))
    
    def get_child_probs(self):
        probs = []
        for c in self.childNodes:
            probs.append(c.N)
        
        probs = np.array(probs)
        probs = np.power(probs, 1 / config.ETA)
        probs = probs / np.sum(probs)
        
        return probs
    
    def add_virtual_loss(self):
        self.N += 1
        self.W -= 1
        self.Q = self.W / self.N
    
    def update(self, result):
        self.N += 1
        self.W += result
        self.Q = self.W / self.N
        
    def get_possible_moves(self, state):
        self.possible_moves = state.ai_get_moves()
        return self.possible_moves
    
    def check_untried(self, state):
        self.get_possible_moves(state)
        
        possible_expansion = []
        for m in self.possible_moves:
            if m not in self.child_moves:
                possible_expansion.append(m)
                
        return possible_expansion
    
    def add_child(self, player, move):
        if move[0] == config.DRAW_PLANT:
            n = Draw_Plant(player, self)
        else:
            n = Node(player, self, move)
        self.childNodes.append(n)
        self.child_moves.append(move)
        return n
        
    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s

    def __repr__(self):
        return "[M:" + str(self.move) + " Q/N:" + str(self.Q) + "/" + str(self.N) + "]"

class Draw_Plant(Node):
    def __init__(self, player, parent = None):
        Node.__init__(self, player, parent, (config.DRAW_PLANT, ))
        self.possible_moves = []
        self.is_random = True
        
    def get_possible_moves(self, state):
        return self.possible_moves
    
    def roll(self, state):
        plant = state.plants_stack[0]
        
        if ((config.DRAW_PLANT, plant[0]) in self.child_moves):
            idx = self.child_moves.index((config.DRAW_PLANT, plant[0]))
            return self.childNodes[idx], False
        else:
            node = self.add_child((config.DRAW_PLANT, plant[0]))
            return node, True
            
    def add_child(self, move):
        node = Node(self.current_player, self, move)
        self.childNodes.append(node)
        self.child_moves.append(move)
        return node
        
class MCTS_AI():
    def __init__(self, player_id, itermax, agent, agent_name):
        self.itermax = itermax
        self.player_id = player_id
        self.agent_name = agent_name
        self.deteministic_play = config.DETERMINISTIC_PLAY
        self.agent = agent
        
        self.agent.purge_cache()  

        self.plants_below_3 = []
        self.potential_available_plants = []
        self.num_plants_above_3 = 0
        self.plant_13_drafted = False
        
    def add_plant_below_3(self, plant):
        self.plants_below_3.append(plant)
        
    def initialize_potential_plants(self):
        self.potential_available_plants = config.PLANTS[8:]
        self.num_plants_above_3 = len(self.potential_available_plants) - config.NUMBER_PLANTS_NOT_IN_PLAY[5]
         
    def remove_potential_plant(self, plant):
        self.potential_available_plants.remove(plant)
        self.num_plants_above_3 -= 1
        
        if plant[0] == 13:
            self.plant_13_drafted = True
    
    def select(self, state, node, weight):
        while 1:
            if node.is_random:
                node, evaluate = node.roll(state)
                #node.add_virtual_loss()
                state.ai_do_move(node.move)
            else:
                expansion_nodes = node.check_untried(state)
                if expansion_nodes != [] or state.game_phase == config.PHASE_END_GAME:
                    return node, expansion_nodes
                else:
                    node = node.UCTSelectChild(weight)
                    #node.add_virtual_loss()
                    if node.move[0] != config.DRAW_PLANT:
                        state.ai_do_move(node.move)
                    
    def expand(self, state, node, possible_expansions):
        m = choice(possible_expansions) 
        current_player = state.get_player_moving()
        if m[0] != config.DRAW_PLANT:
            state.ai_do_move(m)
        node = node.add_child(current_player, m) # add child and descend tree
        #node.add_virtual_loss()

        if node.is_random:
            node, evaluate = node.roll(state)
            #node.add_virtual_loss()
            state.ai_do_move(node.move)

        return node
        
    def expansion_possibilities(self, state, node):
        expansion_nodes = node.check_untried(state)
        return expansion_nodes    
    
    def determinization(self, state):
        # Plants_stack
        final_stack = []
        plants_av = deepcopy(self.potential_available_plants)
        plants_from_av = self.num_plants_above_3
        
        # Add plant 13 if not drafted
        if self.plant_13_drafted is False:
            for p in plants_av:
                if p[0] == 13:
                    final_stack.append(p)
                    plants_av.remove(p)
                    plants_from_av -= 1
                    break
                    
        # Shuffle
        shuffle(plants_av)
        final_stack = final_stack + plants_av[:plants_from_av]
        
        # Step 3
        final_stack.append((999, config.STEP_3, 0, 0))
        
        # Plants below
        shuffle(self.plants_below_3)
        final_stack = final_stack + self.plants_below_3
        
        state.plants_stack = final_stack
        
    def move(self, rootstate):
        iterations_done = 0
        itermax = self.itermax
        
        if rootstate.num_rounds > config.DETEMINISTIC_MOVES_THRESHOLD:
            self.deteministic_play = True
        
        self.rootnode = Node(rootstate.get_player_moving())
        
        if len(self.rootnode.get_possible_moves(rootstate)) == 1:
            print (rootstate.get_player_moving())
            print (self.rootnode.possible_moves[0])
            return self.rootnode.possible_moves[0], rootstate.get_player_moving()
            
        print(rootstate.get_player_moving())
        
        i = iterations_done
        while i < itermax:
            
            if i % 2000 == 0:
                print("Iterations Done: " + str(i))
                
            node = self.rootnode
            state = copy(rootstate)
            state.ai_rollout = 1
            
            self.determinization(state)
                
            # Select
            node, expansion_nodes = self.select(state, node, (i / itermax) * (i / itermax))
            
            for j in range(config.EXPANSION_STEPS):
                # Expand
                if expansion_nodes != []: # Otherwise this is a terminal Node
                    node = self.expand(state, node, expansion_nodes)
                    prediction = self.agent.predict(state, node.current_player)

                # Backpropagate
                last_node_player = node.current_player
                if state.game_phase == config.PHASE_END_GAME:
                    expansion_result = np.zeros(5)
                    for p in range(5):
                        p_order = (5 + p - last_node_player) % 5
                        expansion_result[p_order] = state.ai_get_result(p)
                else:
                    expansion_result = [None, None, None, None, None]
                    expansion_result[0] = prediction[0][0]
                    
                backprop_node = node
                while backprop_node != None: # backpropagate from the expanded node and work back to the root node
                    p_order = (5 + backprop_node.current_player - last_node_player) % 5
                    
                    if expansion_result[p_order] is None:
                        prediction = self.agent.predict(state, backprop_node.current_player)
                        expansion_result[p_order] = prediction[0][0]
                        
                    backprop_node.update(expansion_result[p_order]) # state is terminal. Update node with result from POV of node.playerJustMoved
                    backprop_node = backprop_node.parentNode
                    
                expansion_nodes = self.expansion_possibilities(state, node)
                
                if expansion_nodes == []: # It was a terminal node
                    break
                
            if self.deteministic_play is True and i > itermax / 2.0:
                s_children = sorted(self.rootnode.childNodes, key = lambda c: c.N)
                
                if len(s_children) < 2 or s_children[-1].N > s_children[-2].N + config.EXPANSION_STEPS * (itermax - i):
                    move = s_children[-1].move
                    
                    print (self.rootnode.ChildrenToString())
                    #posterior_probs = self.calc_posteriors(self.rootnode, rootstate)
                    
                    print ("Move selected: " + str(move))
                    return move, rootstate.get_player_moving()
                    
            itermax = len(self.rootnode.childNodes) * self.itermax / config.EXPLORATION_CHILD_BASIS
            i += 1
            
        print (self.rootnode.ChildrenToString())
        
        if self.deteministic_play is True:
            move = sorted(self.rootnode.childNodes, key = lambda c: c.N)[-1].move
        else:
            move = np.random.choice(self.rootnode.childNodes, p = self.rootnode.get_child_probs()).move
        print ("Move selected: " + str(move))
        return move, rootstate.get_player_moving()