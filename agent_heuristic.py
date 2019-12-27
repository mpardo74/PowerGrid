import config
import numpy as np

class Agent_Heuristic():
    def __init__(self):
        self.state = None
        self.perspective = None
        self.mcts = None
        
    def purge_cache(self):
        pass
        
    def predict(self, state, perspective, mcts):
        self.state = state
        self.perspective = perspective
        self.mcts = mcts
        
        money = np.array(self.players_money())
        base_values = np.array(self.base_value())
        
        total_monetary_value = money + base_values
        sum_value = np.max([np.sum(total_monetary_value), 0.01])
        
        game_value = total_monetary_value / sum_value
        
        return [[game_value[self.perspective]]]
        
    def players_money(self):
        return [np.minimum(p.money, 175) for p in self.state.players]
        
    def base_value(self):
        base_value = []
        
        for p in range(5):
            b = 0
            
            # Plants
            for plant in self.state.players[p].plants:
                b += 1.5 * plant[0]
                
            # Resources
            for r in [config.COAL, config.OIL, config.GARBAGE, config.NUCLEAR]:
                b += 10 * self.state.players[p].resources[r]
            
            # Cities
            b += 25 * len(self.state.players[p].cities)
            
            base_value.append(b)
            
        return base_value