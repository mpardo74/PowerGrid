import numpy as np

import config
from model import Residual_CNN

class Agent_NN:
    def __init__(self, enable_cache = False):
        self.nn = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, config.INPUT_DIM)
        
        self.enable_cache = enable_cache
        self.cache = {}
        
    def purge_cache(self):
        self.cache = {}
        
    def nn_read(self, name):
        self.nn.read(name)
        
    def nn_write(self, name):
        self.nn.write(name)
    
    def predict(self, state, perspective):
        network = self.build_nn_input(state, perspective)
        return self.nn.predict(network)

    def build_nn_input(self, state, perspective):        
        nn_input = np.zeros((1, config.INPUT_DIM[0]), dtype=np.float32)
        
        # Cities
        for p in range(5):
            p_order = (5 + p - perspective) % 5
            for c in range(42): # 42 is number of nodes in map
                if c in state.players[p].cities:
                    nn_input[:, p_order * 42 + c] = 1.0
                    
        # Plants
        for p in range(5):
            p_order = (5 + p - perspective) % 5
            for i, plant in enumerate(config.PLANTS):
                if plant in state.players[p].plants:
                    nn_input[:, 210 + p_order * len(config.PLANTS) + i] = 1.0
                    
        # Resources
        for p in range(5):
            p_order = (5 + p - perspective) % 5
            for r in range(4):
                for i in range(7):
                    if state.players[p].resources[r] > (i - 0.01) and state.players[p].resources[r] < (i + 0.01):
                        nn_input[:, 420 + 4 * 7 * p_order + 7 * r + i] = 1.0
                        
        # Money
        for p in range(5):
            p_order = (5 + p - perspective) % 5
            nn_input[:, 560 + p_order] = float(state.players[p].money) / 150.0
        
        # Player Order
        for i, o in enumerate(state.player_order):
            p_order = (5 + o - perspective) % 5
            nn_input[:, 565 + p_order * 5 + i] = 1.0
        
        # Step
        nn_input[:, 590 + state.game_step - 1] = 1.0
        
        # Phase
        if state.game_phase == config.PHASE_DRAW_PLANT:
            nn_input[:, 593] = 1.0
        if state.game_phase == config.START_AUCTION:
            nn_input[:, 594] = 1.0
        if state.game_phase == config.AUCTIONING:
            nn_input[:, 595] = 1.0
        if state.game_phase == config.DISCARD_PLANT:
            nn_input[:, 596] = 1.0
        if state.game_phase == config.DISCARD_RESOURCES:
            nn_input[:, 597] = 1.0
        if state.game_phase == config.BUYING_RESOURCES:
            nn_input[:, 598] = 1.0
        if state.game_phase == config.BUILDING_CITIES:
            nn_input[:, 599] = 1.0
        if state.game_phase == config.DRAW_PLANT:
            nn_input[:, 600] = 1.0
        if state.game_phase == config.FIRING_PLANTS:
            nn_input[:, 601] = 1.0
            
        # Plants Market
        for i, plant in enumerate(config.PLANTS):
            if state.game_step < 3:
                if plant in state.plants_market[:4]:
                    nn_input[:, 602 + i] = 1.0
                if plant in state.plants_market[4:]:
                    nn_input[:, 602 + len(config.PLANTS) + i] = 1.0
            else:
                if plant in state.plants_market:
                    nn_input[:, 602 + i] = 1.0
            
        return nn_input