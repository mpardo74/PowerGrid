from copy import deepcopy

from mcts_ai import MCTS_AI
import config

class Player:
    def __init__(self, player_id, is_human):
        self.id = player_id
        self.is_human = is_human
    
        self.money = 50
        self.cities = []
        self.plants = []
        self.resources = {config.COAL: 0, config.OIL: 0, config.GARBAGE: 0, config.NUCLEAR: 0}
        
        self.can_auction = 0
        self.plants_to_fire = []
        self.plants_to_decide = []
        
        self.ai = None

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in ["ai"]:
                setattr(result, k, deepcopy(v, memo))
        return result
        
    def final_score(self):
        self.plants_to_fire = []
        self.plants_to_decide = []
        
        self.start_firing()
        max_cities = min(len(self.cities), self.optimal_firing(self.plants_to_fire, self.plants_to_decide, self.resources))
        
        return (max_cities, self.money)
        
    def optimal_firing(self, plants_firing, plants_pending, resources):
        if len(plants_pending) == 0:
            total_cities = 0
            
            for p in plants_firing:
                total_cities += p[0][3]
                
            return total_cities

        max_cities = 0
        
        for p in plants_pending:
            if p[1] == config.COAL_OIL:
                fuel_combinations = self.coal_oil_combination(p[2], resources)
            else:
                fuel_combinations = [[p[1]] * p[2]]
                
            for f in fuel_combinations:
                new_plants_firing = deepcopy(plants_firing)
                new_plants_pending = deepcopy(plants_pending)
                new_resources = deepcopy(resources)
                
                new_plants_firing.append((p, f))
                new_plants_pending.remove(p)
                
                for res in f:
                    new_resources[res] -= 1
                    
                    if new_resources[res] < 0:
                        print (self.id)
                        print (plants_firing)
                        print (plants_pending)
                        print (resources)
                        print (f)
                        raise Exception("MESSS")
                        
                plants_to_remove = []
                for plant in new_plants_pending:
                    if not self.has_resources_to_fire(plant, remaining_resources = new_resources):
                        plants_to_remove.append(plant)
                
                for plant in plants_to_remove:
                    new_plants_pending.remove(plant)
                        
                cities_lit = self.optimal_firing(new_plants_firing, new_plants_pending, new_resources)
                
                if cities_lit > max_cities:
                    max_cities = cities_lit
                    
        return max_cities
    
    def coal_oil_combination(self, number_resources, resources = None):
        if resources is None:
            resources = deepcopy(self.resources)
    
            for firing in self.plants_to_fire:
                for r in firing[1]:
                    resources[r] -= 1
            
        if (resources[config.COAL] + resources[config.OIL]) < number_resources:
            raise Exception("I don't have enough resources")
            
        available_combinations = []    
        for coal in range(number_resources + 1):
            if resources[config.COAL] >= coal and resources[config.OIL] >= (number_resources - coal):
                available_combinations.append([config.COAL] * coal + [config.OIL] * (number_resources - coal))
                
        return available_combinations
        
    def add_power_plant(self, plant, cost):
        self.plants.append(plant)
        self.money -= cost
        
        if self.money <= 0:
            raise Exception("MONEY MESS")
        
    def discard_plant(self, plant):
        self.remove(plant)
        
    def max_cities_fired(self):
        cities = 0
        
        for firing in self.plants_to_fire:
            cities += firing[0][3]
            
        if cities > len(self.cities):
            cities = len(self.cities)
        
        return cities
    
    def has_resources_to_fire(self, p, remaining_resources = None):
        if remaining_resources == None:
            remaining_resources = deepcopy(self.resources)
    
            for firing in self.plants_to_fire:
                for r in firing[1]:
                    remaining_resources[r] -= 1
                
        if p[1] == config.COAL_OIL:
            if (remaining_resources[config.COAL] + remaining_resources[config.OIL]) >= p[2]:
                return True
        
        elif remaining_resources[p[1]] >= p[2]:
            return True
            
        return False
    
    def start_firing(self):
        self.plants_to_fire = []
        
        for p in self.plants:
            if p[1] == config.RENEWABLE:
                self.plants_to_fire.append((p, []))
            elif self.has_resources_to_fire(p):
                self.plants_to_decide.append(p)
            else:
                pass
                
    def remove_resources(self):
        for firing in self.plants_to_fire:
            for r in firing[1]:
                self.resources[r] -= 1
                
                if self.resources[r] < 0:
                    raise Exception("MESS")
        
    def order_value(self):
        max_plant = 0
        
        for p in self.plants:
            if p[0] > max_plant:
                max_plant = p[0]
                
        return 100 * len(self.cities) + max_plant
        
    def max_resources_fit(self):
        max_resources = {config.COAL: 0, config.OIL: 0, config.GARBAGE: 0, config.NUCLEAR: 0, config.COAL_OIL: 0}
    
        for p in self.plants:
            if p[1] == config.COAL:
                max_resources[config.COAL] += 2 * p[2]
                max_resources[config.COAL_OIL] += 2 * p[2]
            elif p[1] == config.OIL:
                max_resources[config.OIL] += 2 * p[2]
                max_resources[config.COAL_OIL] += 2 * p[2]
            elif p[1] == config.GARBAGE:
                max_resources[config.GARBAGE] += 2 * p[2]
            elif p[1] == config.NUCLEAR:
                max_resources[config.NUCLEAR] += 2 * p[2]
            elif p[1] == config.COAL_OIL:
                max_resources[config.COAL] += 2 * p[2]
                max_resources[config.OIL] += 2 * p[2]
                max_resources[config.COAL_OIL] += 2 * p[2]
                
        return max_resources
        
    def resources_fit(self):
        max_resources = self.max_resources_fit()
        
        for r in [config.COAL, config.OIL, config.GARBAGE, config.NUCLEAR]:
            if self.resources[r] > max_resources[r]:
                self.resources[r] = max_resources[r]
                
        if (self.resources[config.COAL] + self.resources[config.OIL]) > max_resources[config.COAL_OIL]:
            return False
        else:
            return True
        
    def can_buy_resources(self):
        max_resources = self.max_resources_fit()
                
        can_buy = []
        
        if self.resources[config.COAL] < max_resources[config.COAL] and (self.resources[config.COAL] + self.resources[config.OIL]) < max_resources[config.COAL_OIL]:
            can_buy.append(config.COAL)
        if self.resources[config.OIL] < max_resources[config.OIL] and (self.resources[config.COAL] + self.resources[config.OIL]) < max_resources[config.COAL_OIL]:
            can_buy.append(config.OIL)
        if self.resources[config.GARBAGE] < max_resources[config.GARBAGE]:
            can_buy.append(config.GARBAGE)
        if self.resources[config.NUCLEAR] < max_resources[config.NUCLEAR]:
            can_buy.append(config.NUCLEAR)
            
        return can_buy