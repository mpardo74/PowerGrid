import uuid
import pickle
import numpy as np
from random import shuffle, choice
from copy import deepcopy

import config
from player import Player
from mcts_ai import MCTS_AI

class GameState:
    def __init__(self, map = 'GERMANY', agents_obj = None, game_config = None):
        self.uuid = uuid.uuid1()
        
        ############
        self.num_players = config.NUM_PLAYERS
        if self.num_players > 2:
            self.MAX_POWER_PLANTS = 3
        else:
            self.MAX_POWER_PLANTS = 4
        ############
        
        self.map = map
        
        self.plants_market, self.plants_stack = self.generate_plants(self.num_players)
        self.regions_available = self.select_regions(config.MAP_CONFIG[map]['ADJACENT'], self.num_players)
        self.nodes = config.MAP_CONFIG[map]['NODES']
        self.connections = config.MAP_CONFIG[map]['CONNECTIONS']
        self.nodes_not_in_play = self.check_not_in_play()
        self.shortest_paths = self.initialize_short_path(config.MAP_CONFIG[map]['NODES'], config.MAP_CONFIG[map]['CONNECTIONS'], self.nodes_not_in_play)
        
        self.CITIES_STEP_2 = config.MAP_CONFIG[map]['STEP_2_HOUSES'][self.num_players]
        self.CITIES_END = config.MAP_CONFIG[map]['END_HOUSES'][self.num_players]
        self.REPLENISH_RESOURCES = config.MAP_CONFIG[map]['REPLENISH_RESOURCES']
        
        self.players = []
        for p in range(self.num_players):
            self.players.append(Player(p, config.player_is_human[p]))

            if config.player_is_human[p] == 0:
                selected_agent = choice(agents_obj)
                
                if selected_agent[0] == "h":
                    mcts_exploration = config.MCTS_EXPLORATION_HEURISTIC
                else:
                    mcts_exploration = config.MCTS_EXPLORATION
                    
                self.players[p].ai = MCTS_AI(p, mcts_exploration, selected_agent[1], selected_agent[0])
                self.players[p].ai.initialize_potential_plants()
            
        self.player_order = list(range(self.num_players))
        np.random.shuffle(self.player_order)
        self.player_turn = self.player_order[0]
        
        self.game_step = 1
        self.round_step = config.AUCTION
        self.num_rounds = 0
        self.game_phase = config.START_AUCTION
        self.step_3_to_start = 0
        self.previous_state_drawing = 0
        self.next_action_drawing = 0
        
        self.configure_start_auction()
        
        # Start resources
        self.resources_market = self.initialize_resources_market()
        for resource, amount in config.MAP_CONFIG[map]['INITIAL_RESOURCES'].items():
            self.add_resources_to_market(resource, amount)
        
        self.current_bid = (0, 0, 0)
        self.player_in_bid = []
        self.plants_bought_in_round = 0
        
        self.ai_rollout = 0
        
        self.winner = None

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)

        result.__dict__ = self.__dict__.copy(  )
        
        #result.__dict__["players"] = []
        #for i in range(4):
        #    result.__dict__["players"].append(copy(self.__dict__["players"][i]))
        
        for key in ["plants_market", "plants_stack", "player_in_bid", "player_order"]:
            result.__dict__[key] = self.__dict__[key][:]
        
        for key in ["players", "resources_market"]:
            result.__dict__[key] = deepcopy(self.__dict__[key])
        
        return result
    
    def print_game_state(self):
        print ("*************************************************")
        print ("GAME STATE: (Round " + str(self.num_rounds) + ")")
        
        for p in self.players:
            print("Player " + str(p.id) + ", (" + str(p.ai.agent_name) + "):")
            print("Plants: " + str(p.plants))
            print("Resources: " + str(p.resources))
            print("Money: " + str(p.money))
            print("Cities: " + str(p.cities))
            
        print("Plants Market: " + str(self.plants_market))
    
    def check_not_in_play(self):
        not_in_play = []
        
        for i, n in enumerate(self.nodes):
            if n[1] not in self.regions_available:
                not_in_play.append(i)
            
        return not_in_play
    
    @staticmethod
    def initialize_short_path(nodes, connections, nodes_not_in_play):
        def get_expansion_nodes(current_node, connections, visited_nodes):
            expansion_nodes = []
            
            for c in connections:
                if c[0] == current_node:
                    if c[1] not in visited_nodes:
                        expansion_nodes.append((c[1], c[2]))
                if c[1] == current_node:
                    if c[0] not in visited_nodes:
                        expansion_nodes.append((c[0], c[2]))
                        
            return expansion_nodes
    
        shortest_routes = np.zeros((len(nodes), len(nodes)))
        
        for i in range(len(nodes)):
            if i not in nodes_not_in_play:
                visited_nodes = nodes_not_in_play + [i]
                frontier = []
                current_node = i
                current_cost = 0
                
                while len(visited_nodes) < len(nodes):
                    expand_nodes = get_expansion_nodes(current_node, connections, visited_nodes)
                    for n in expand_nodes:
                        node_in_frontier = False
                        
                        for k, f in enumerate(frontier):
                            if f[0] == n[0]:
                                node_in_frontier = True
                                
                                if (n[1] + current_cost) < f[1]:
                                    frontier[k] = (f[0], n[1] + current_cost)
                                    
                                break
                                
                        if node_in_frontier is False:
                            frontier.append((n[0], n[1] + current_cost))
                            
                    frontier = sorted(frontier, key = lambda j: j[1], reverse = True)
                    min_node = frontier.pop()
                    
                    shortest_routes[i][min_node[0]] = min_node[1]
                    shortest_routes[min_node[0]][i] = min_node[1]
                    
                    visited_nodes.append(min_node[0])
                    current_node = min_node[0]
                    current_cost = min_node[1]
                
        return shortest_routes
    
    @staticmethod
    def generate_plants(num_players):
        plants_market = config.PLANTS[:8]
        plants_remaining = config.PLANTS[8:]
        
        for i, plant in enumerate(plants_remaining):
            if plant[0] == 13:
                plant_13 = plants_remaining.pop(i)
                break
                
        np.random.shuffle(plants_remaining)
                
        for i in range(config.NUMBER_PLANTS_NOT_IN_PLAY[num_players]):
            plants_remaining.pop()
        
        plants_stack = [plant_13] + plants_remaining + [(999, config.STEP_3, 0, 0)]
        
        return plants_market, plants_stack
        
    @staticmethod
    def select_regions(adjacent_regions, num_players):
        total_regions = min(5, max(3, num_players))
        regions = [np.random.randint(6)]
        
        while len(regions) < total_regions:
            link_num = np.random.choice(len(adjacent_regions))
            link = adjacent_regions[link_num]
            
            if link[0] in regions and link[1] not in regions:
                regions.append(link[1])
            if link[0] not in regions and link[1] in regions:
                regions.append(link[0])
                
        return np.sort(regions)
        
    @staticmethod
    def initialize_resources_market():
        empty_market = {config.COAL: [], config.OIL: [], config.GARBAGE: [], config.NUCLEAR: []}
        
        for resource in [config.COAL, config.OIL, config.GARBAGE]:
            for price in range(8, 0, -1):
                for _ in range(3):
                    empty_market[resource].append([price, 0])
                    
        # Nucelar
        for price in [16, 14, 12, 10, 8, 7, 6, 5, 4, 3, 2, 1]:
            empty_market[config.NUCLEAR].append([price, 0])
            
        return empty_market
    
    def ai_add_plant_below(self, plant):
        if self.ai_rollout == 0:
            for p in range(5):
                if self.players[p].ai != None:
                    self.players[p].ai.add_plant_below_3(plant)
                    
    def ai_draft_plant(self, plant):
        if self.ai_rollout == 0:
            for p in range(5):
                if self.players[p].ai != None:
                    self.players[p].ai.remove_potential_plant(plant)        
    
    def add_resources_to_market(self, resource_type, amount):
        first_empty_space = 9999
        
        # Look for first empty space
        for i in range(len(self.resources_market[resource_type])):
            if self.resources_market[resource_type][i][1] == 0:
                first_empty_space = i
                break
                
        # Fill subsequent spaces
        for j in range(first_empty_space, first_empty_space + amount):
            if j >= len(self.resources_market[resource_type]):
                break
                
            self.resources_market[resource_type][j][1] = 1
        
    def available_resource_1(self, resource_type):
        if self.resources_market[resource_type][0][1] == 0:
            return False
        else:
            return True        
    
    def get_first_empty_resource(self, resource_type):
        if self.available_resource_1(resource_type):
            for i in range(len(self.resources_market[resource_type])):
                if self.resources_market[resource_type][i][1] == 0:
                    return i
                
        return len(self.resources_market[resource_type])
    
    def remove_1_resource_from_market(self, resource_type):
        first_empty = self.get_first_empty_resource(resource_type)             
        self.resources_market[resource_type][first_empty - 1][1] = 0
        
    def get_cheapest_price(self, resource_type):
        first_empty = self.get_first_empty_resource(resource_type)
        
        if first_empty == 0:
            return 999999999
        else:
            return self.resources_market[resource_type][first_empty - 1][0]
    
    def order_players(self):
        self.player_order = sorted(self.player_order, key = lambda i: self.players[i].order_value(), reverse = True)
    
    def configure_start_auction(self):
        self.game_phase = config.START_AUCTION
        self.player_turn = self.player_order[0]
        self.plants_bought_in_round = 0
        
        for p in self.players:
            p.can_auction = 1
            
    def find_plant_description(self, plant_id):
        for p in self.plants_market:
            if p[0] == plant_id:
                return p
            
    def start_plant_auction(self, player_id, plant_id):
        if self.players[player_id].money >= plant_id:
            if self.ai_rollout == 0:
                print("Player " + str(self.player_turn) + ": Start Auction in plant " + str(plant_id))
            
            plant = self.find_plant_description(plant_id)
            self.current_bid = (player_id, plant, plant_id)
            
            self.player_in_bid = [player_id]
            for p in self.players:
                if p.id != player_id and p.can_auction == 1 and p.money >= self.current_bid[2]:
                    self.player_in_bid.append(p.id)
            
            if len(self.player_in_bid) > 1:
                self.game_phase = config.AUCTIONING
                self.player_to_bid = self.player_in_bid[1]
            else:
                self.execute_buy_plant()
                
    def increase_bid_plant(self, amount):
        if self.players[self.player_to_bid].money >= (self.current_bid[2] + amount):
            if self.ai_rollout == 0:
                print("Player " + str(self.player_to_bid) + ": Increase bid to " + str(self.current_bid[2] + amount))
            
            self.current_bid = (self.player_to_bid, self.current_bid[1], self.current_bid[2] + amount)
            
            idx_player = self.player_in_bid.index(self.player_to_bid)
            self.player_to_bid = self.player_in_bid[(idx_player + 1) % len(self.player_in_bid)]
            
    def drop_from_auction(self):
        if self.ai_rollout == 0:
            print("Player " + str(self.player_to_bid) + ": Drops from auction")
            
        idx_player = self.player_in_bid.index(self.player_to_bid)
        self.player_in_bid.remove(self.player_to_bid)
        
        if len(self.player_in_bid) == 1:
            self.execute_buy_plant()
            
        else:
            self.player_to_bid = self.player_in_bid[idx_player % len(self.player_in_bid)]
    
    def pass_in_auction(self):
        if self.ai_rollout == 0:
            print("Player " + str(self.player_turn) + ": Does not auction any plant")
        
        self.players[self.player_turn].can_auction = 0
        self.check_auctions_finished()
        
    def check_auctions_finished(self):
        auctions_finished = True
        
        for p in self.players:
            if p.can_auction == 1:
                auctions_finished = False
                break
                
        if auctions_finished:
            if self.num_rounds == 0:
                self.order_players()
                self.start_buying_resources()
            else:
                if self.plants_bought_in_round == 0 and len(self.plants_market) > 0:
                    self.plants_market.pop(0)
                    self.initiate_draw_plant(3)
                else:
                    self.start_buying_resources()
                
        else:
            self.game_phase = config.START_AUCTION
            for p_id in self.player_order:
                if self.players[p_id].can_auction == 1:
                    self.player_turn = p_id
                    self.player_to_bid = p_id
                    break                
    
    def execute_buy_plant(self):
        player_id = self.current_bid[0]
        
        if len(self.players[player_id].plants) >= self.MAX_POWER_PLANTS:
            self.game_phase = config.DISCARD_PLANT
            
        else:
            self.players[player_id].add_power_plant(self.current_bid[1], self.current_bid[2])
            self.players[player_id].can_auction = 0
            self.plants_bought_in_round = 1
            
            self.plants_market.remove(self.current_bid[1])
            
            if not self.players[player_id].resources_fit():
                self.game_phase = config.DISCARD_RESOURCES
                
            else:
                self.initiate_draw_plant(4)
                    
    def drop_plant(self, plant_id):
        for p in self.players[self.current_bid[0]].plants:
            if p[0] == plant_id:
                self.players[self.current_bid[0]].plants.remove(p)
                
        self.game_phase = config.AUCTIONING
        self.execute_buy_plant()
        
    def drop_resource(self, player_id, resource_type):
        if self.ai_rollout == 0:
            print("Player " + str(self.player_turn) + " discards resource " + str(resource_type))
        
        self.players[player_id].resources[resource_type] -= 1
        
        if self.players[player_id].resources[resource_type] < -0.1:
            raise Exception("MESS")
        
        if self.players[player_id].resources_fit():
            self.initiate_draw_plant(4)
    
    def initiate_draw_plant(self, next_event):
        # Events: 0 - None
        #         1 - start_firing_plants
        #         2 - configure_start_auction
        #         3 - start_buying_resources
        #         4 - check_auctions_finished
        
        self.previous_state_drawing = self.game_phase
        self.next_action_drawing = next_event
        
        self.game_phase = config.PHASE_DRAW_PLANT
    
    def draw_plant(self):
        if len(self.plants_stack) > 0:
            new_plant = self.plants_stack.pop(0)
            
            if new_plant[1] == config.STEP_3:
                np.random.shuffle(self.plants_stack)
                
                if self.previous_state_drawing[0] == config.AUCTION:
                    self.step_3_to_start = 1
                    self.plants_market.append(new_plant)
                    self.plants_market = sorted(self.plants_market, key = lambda x: x[0])
                    
                elif self.previous_state_drawing[0] == config.BUILDING:
                    self.step_3_to_start = 1
                    self.plants_market.pop(0)
                    
                elif self.previous_state_drawing[0] == config.BUREAUCRACY:
                    self.game_step = 3
                    self.plants_market.pop(0)
                    
            else:
                self.plants_market.append(new_plant)
                self.plants_market = sorted(self.plants_market, key = lambda x: x[0])
                
        self.game_phase = self.previous_state_drawing
        self.previous_state_drawing = 0
        
        if self.next_action_drawing == 1:
            self.start_firing_plants()
        elif self.next_action_drawing == 2:
            self.configure_start_auction()
        elif self.next_action_drawing == 3:
            self.start_buying_resources()
        elif self.next_action_drawing == 4:
            self.game_phase = config.AUCTIONING
            self.check_auctions_finished()
    
    def start_buying_resources(self):
        if self.step_3_to_start == 1:
            self.plants_market.pop(0)
            self.plants_market.pop(-1)
            self.game_step = 3
            self.step_3_to_start = 0
    
        self.round_step = config.BUY_RESOURCES
        self.game_phase = config.BUYING_RESOURCES
        self.player_turn = self.player_order[-1]
        
    def buy_resource(self, resource_type):
        if self.ai_rollout == 0:
            print("Player " + str(self.player_turn) + " buys resource " + str(resource_type))
            
        price = self.get_cheapest_price(resource_type)
        
        if self.players[self.player_turn].money >= price and resource_type in self.players[self.player_turn].can_buy_resources():
            self.players[self.player_turn].money -= price
            self.players[self.player_turn].resources[resource_type] += 1
            self.remove_1_resource_from_market(resource_type)
            
            if self.players[self.player_turn].money < -0.01:
                raise Exception("MONEY MESS")
            
    def end_buying_resources(self):
        if self.ai_rollout == 0:
            print("Player " + str(self.player_turn) + " finished buying")
        
        idx_player = self.player_order.index(self.player_turn)
        
        if idx_player == 0:
            self.start_building()
        else:
            self.player_turn = self.player_order[idx_player - 1]
            
    def start_building(self):
        self.round_step = config.BUILDING
        self.game_phase = config.BUILDING_CITIES
        self.player_turn = self.player_order[-1]
        
    def number_buildings_city(self, city_id):
        total_buildings = 0
    
        for p in self.players:
            if city_id in p.cities:
                total_buildings += 1
                
        return total_buildings
        
    def check_player_can_build(self, city_id):
        region = self.nodes[city_id][1]
        
        if region not in self.regions_available:
            return False, 0
        if self.players[self.player_turn].money < 10:
            return False, 0
        if city_id in self.players[self.player_turn].cities:
            return False, 0
    
        cost = 0
        buildings = self.number_buildings_city(city_id)
        
        if self.game_step == 1:
            if buildings > 0:
                return False, 0
            else:
                cost += 10
        elif self.game_step == 2:
            if buildings > 1:
                return False, 0
            else:
                cost += 10 + 5 * buildings
        elif self.game_step == 3:
            if buildings > 2:
                return False, 0
            else:
                cost += 10 + 5 * buildings
                
        # First location?
        if len(self.players[self.player_turn].cities) == 0:
            return True, cost
            
        # Add cost from nearest city
        min_connection_cost = 999
        for c in self.players[self.player_turn].cities:
            connection_cost = self.shortest_paths[city_id, c]
            
            if connection_cost < min_connection_cost:
                min_connection_cost = connection_cost
                
        cost += min_connection_cost
        
        if min_connection_cost <= config.MAX_CONNECTION_COST and cost <= self.players[self.player_turn].money:
            return True, cost
        else:
            return False, 0
            
    def build_city(self, city_id):
        if self.ai_rollout == 0:
            print("Player " + str(self.player_turn) + " builds city " + str(self.nodes[city_id][0]))
        
        can_build, cost = self.check_player_can_build(city_id)
        
        if can_build:
            self.players[self.player_turn].cities.append(city_id)
            self.players[self.player_turn].money -= cost
            
            self.check_if_remove_power_plant()
            
    def max_cities_built(self):
        max_cities = 0
        
        for p in self.players:
            if len(p.cities) > max_cities:
                max_cities = len(p.cities)
                
        return max_cities
            
    def end_building_cities(self):
        if self.ai_rollout == 0:
            print("Player " + str(self.player_turn) + " finished building")
        
        idx_player = self.player_order.index(self.player_turn)
        
        if idx_player == 0:
            if self.max_cities_built() >= self.CITIES_END:
                self.end_game()
                
            else:
                if self.game_step == 1 and self.max_cities_built() > self.CITIES_STEP_2:
                    self.game_step = 2
                    self.plants_market.pop(0)
                    self.initiate_draw_plant(1)
                
                else:
                    self.start_firing_plants()
        else:
            self.player_turn = self.player_order[idx_player - 1]
    
    def start_firing_plants(self):
        if self.step_3_to_start == 1:
            self.game_step = 3
            self.step_3_to_start = 0
            
        self.round_step = config.BUREAUCRACY
        self.game_phase = config.FIRING_PLANTS
        self.player_turn = self.player_order[0]
        
        self.players[self.player_turn].start_firing()
        
    def fire_plants(self):
        max_cities_to_fire = self.players[self.player_turn].max_cities_fired()
        
        money = config.MONEY_PAYMENTS[max_cities_to_fire]
        self.players[self.player_turn].money += money
        
        self.players[self.player_turn].remove_resources()
        
    def add_power_plant_to_fire(self, plant_id, resources):
        if self.ai_rollout == 0:
            print("Player " + str(self.player_turn) + " firing plant " + str(plant_id))
        
        for i, p in enumerate(self.players[self.player_turn].plants_to_decide):
            if p[0] == plant_id:
                plant = self.players[self.player_turn].plants_to_decide.pop(i)
                break
                
        self.players[self.player_turn].plants_to_fire.append((plant, resources))
        
    def discard_power_plant_to_fire(self, plant_id):
        for i, p in enumerate(self.players[self.player_turn].plants_to_decide):
            if p[0] == plant_id:
                plant = self.players[self.player_turn].plants_to_decide.pop(i)
                break
    
    def end_firing_plants(self):
        if self.ai_rollout == 0:
            print("Player " + str(self.player_turn) + " finished firing")
        
        self.fire_plants()
        
        idx_player = self.player_order.index(self.player_turn)
        
        if idx_player == (self.num_players - 1):
            self.replenish_resources()
        else:
            self.player_turn = self.player_order[idx_player + 1]     
            self.players[self.player_turn].start_firing()   
    
    def check_if_remove_power_plant(self):
        num_cities_player = len(self.players[self.player_turn].cities)
        
        if len(self.plants_market) > 0:
            if num_cities_player >= self.plants_market[0][0]:
                self.plants_market.pop(0)
                self.initiate_draw_plant(0)
            
    def replenish_resources(self):
        for resource, amounts in self.REPLENISH_RESOURCES.items():
            self.add_resources_to_market(resource, amounts[self.num_players][self.game_step - 1])
        
        if self.ai_rollout == 0:
            self.print_game_state()
        
        self.num_rounds += 1
        self.order_players()
            
        if self.game_step < 3:
            try:
                plant = self.plants_market.pop(-1)
            except:
                raise Exception("This is impossible?")
            self.plants_stack.append(plant)
            self.ai_add_plant_below(plant)
            self.initiate_draw_plant(2)
        
        else:
            self.configure_start_auction()
            
    def get_player_moving(self):
        if self.game_phase == config.AUCTIONING:
            return self.player_to_bid
        elif self.game_phase == config.DISCARD_PLANT or self.game_phase == config.DISCARD_RESOURCES:
            return self.current_bid[0]
        else:
            return self.player_turn
            
    def end_game(self):
        self.game_phase = config.PHASE_END_GAME
        
        self.final_score = []
        for p in self.players:
            self.final_score.append(p.final_score())
        
        if self.ai_rollout == 0:
            print (self.final_score)
            
        winner = 0
        best_result = self.final_score[0]
        for i in range(1, self.num_players):
            if self.final_score[i][0] > best_result[0]:
                winner = i
                best_result = self.final_score[i]
            elif self.final_score[i][0] == best_result[0]:
                if self.final_score[i][1] > best_result[1]:
                    winner = i
                    best_result = self.final_score[i]
                    
        self.winner = winner
                    
        if self.ai_rollout == 0:
            print ("Player " + str(self.winner) + " is the winner with " + str(best_result[0]) + " cities lit")
        
    def ai_get_result(self, player):
        if self.game_phase == config.PHASE_END_GAME:
            if self.winner == player:
                return 1.0
            else:
                return float(self.final_score[player][0] / 10.0) - 1.0
        else:
            return 0.0
        
    
    def ai_get_moves(self):
        #input()
        moves = []
        
        if self.game_phase == config.START_AUCTION:
            if self.game_step < 3:
                available_plants = 4
            else:
                available_plants = 6
                
            available_plants = min(available_plants, len(self.plants_market))
                
            for i in range(available_plants):
                if self.players[self.player_turn].money > self.plants_market[i][0]:
                    moves.append((config.START_PLANT_AUCTION, self.plants_market[i][0]))
                    
            if len(self.players[self.player_turn].plants) > 0:
                moves.append((config.PASS_IN_AUCTIONS, ))
            
        elif self.game_phase == config.AUCTIONING:
            # Increments of 1 or 2
            for increment in range(1, 3):
                if self.players[self.player_to_bid].money > (self.current_bid[2] + increment):
                    moves.append((config.INCREMENT_BID, increment))
                    
            moves.append((config.DROP_FROM_AUCTION, ))
            
        elif self.game_phase == config.DISCARD_PLANT:
            for p in self.players[self.current_bid[0]].plants:
                moves.append((config.DROP_PLANT, p[0]))
            
        elif self.game_phase == config.DISCARD_RESOURCES:
            moves.append((config.DROP_RESOURCE, config.COAL))
            moves.append((config.DROP_RESOURCE, config.OIL))
            
        elif self.game_phase == config.BUYING_RESOURCES:
            for r in self.players[self.player_turn].can_buy_resources():
                if self.players[self.player_turn].money >= self.get_cheapest_price(r):
                    moves.append((config.BUY_RESOURCE, r))
                
            moves.append((config.FINISH_BUYING_RESOURCES,))
            
        elif self.game_phase == config.BUILDING_CITIES:
            for i, _ in enumerate(self.nodes):
                can_build, _ = self.check_player_can_build(i)
                if can_build:
                    moves.append((config.BUILD_CITY, i))
                
            moves.append((config.FINISH_BUILDING,))
            
        elif self.game_phase == config.FIRING_PLANTS:
            discard_plants = []
        
            for i, p in enumerate(self.players[self.player_turn].plants_to_decide):
                if self.players[self.player_turn].has_resources_to_fire(p):
                    if p[1] == config.COAL_OIL:
                        for resource_combination in self.players[self.player_turn].coal_oil_combination(p[2]):
                            moves.append((config.FIRE_PLANT, p[0], resource_combination))
                    else:
                        moves.append((config.FIRE_PLANT, p[0], [p[1]] * p[2]))
                        
                    moves.append((config.NOT_FIRE_PLANT, p[0]))
                else:
                    discard_plants.append(p)
                
            for p in discard_plants:
                self.players[self.player_turn].plants_to_decide.remove(p)
                
            if moves == []:
                moves.append((config.FINISH_FIRING,))
            
        elif self.game_phase == config.PHASE_DRAW_PLANT:
            moves.append((config.DRAW_PLANT,))
            
        return moves

    def ai_do_move(self, move):
        if move[0] == config.START_PLANT_AUCTION:
            self.start_plant_auction(self.player_turn, move[1])
        
        elif move[0] == config.PASS_IN_AUCTIONS:
            self.pass_in_auction()
        
        elif move[0] == config.INCREMENT_BID:
            self.increase_bid_plant(move[1])
        
        elif move[0] == config.DROP_FROM_AUCTION:
            self.drop_from_auction()
        
        elif move[0] == config.DROP_PLANT:
            self.drop_plant(move[1])
        
        elif move[0] == config.DROP_RESOURCE:
            self.drop_resource(self.current_bid[0], move[1])
        
        elif move[0] == config.BUY_RESOURCE:
            self.buy_resource(move[1])
        
        elif move[0] == config.FINISH_BUYING_RESOURCES:
            self.end_buying_resources()
        
        elif move[0] == config.BUILD_CITY:
            self.build_city(move[1])
        
        elif move[0] == config.FINISH_BUILDING:
            self.end_building_cities()
        
        elif move[0] == config.FIRE_PLANT:
            self.add_power_plant_to_fire(move[1], move[2])
        
        elif move[0] == config.NOT_FIRE_PLANT:
            self.discard_power_plant_to_fire(move[1])
        
        elif move[0] == config.FINISH_FIRING:
            self.end_firing_plants()
        
        elif move[0] == config.DRAW_PLANT:
            self.draw_plant()