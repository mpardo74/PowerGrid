player_is_human = {0: 0,
                   1: 0,
                   2: 0,
                   3: 0,
                   4: 0}

NUM_PLAYERS = 5

# Setup
MAX_CONNECTION_COST = 50

# Agents
CURRENT_AGENT = [3, 4, 5, 6, 7, 8, 9, 10]
MCTS_EXPLORATION = 400
MCTS_EXPLORATION_HEURISTIC = 50
EXPANSION_STEPS = 2
EXPLORATION_CHILD_BASIS = 10
SELF_PLAY_BATCH_SIZE = 63

# MCTS
DETERMINISTIC_PLAY = True
DETEMINISTIC_MOVES_THRESHOLD = 3
ETA = 0.7

# Neural Net
MOMENTUM = 0.9
REG_CONST = 0.0001
LEARNING_RATE = 0.01
INPUT_DIM = (686, )

VALIDATION_BATCH_SIZE = 32768
TRAIN_BATCH_SIZE = 32768
TRAINING_LOOPS = 10
EPOCHS = 4

folder_agents = 'agents'
folder_self_play = 'games'

# Resources
COAL = 0
OIL = 1
GARBAGE = 2
NUCLEAR = 3
RENEWABLE = 4
COAL_OIL = 5
STEP_3 = 6

# Round Actions
PLAYER_ORDER = 1
AUCTION = 2
BUY_RESOURCES = 3
BUILDING = 4
BUREAUCRACY = 5

# Game Phase
PHASE_END_GAME = (0, 0)
PHASE_DRAW_PLANT = (0, 1)
START_AUCTION = (AUCTION, 0)
AUCTIONING = (AUCTION, 1)
DISCARD_PLANT = (AUCTION, 2)
DISCARD_RESOURCES = (AUCTION, 3)
BUYING_RESOURCES = (BUY_RESOURCES, 0)
BUILDING_CITIES = (BUILDING, 0)
DRAW_PLANT = (BUREAUCRACY, 0)
FIRING_PLANTS = (BUREAUCRACY, 1)

# Actions
START_PLANT_AUCTION = 0
PASS_IN_AUCTIONS = 1
INCREMENT_BID = 2
DROP_FROM_AUCTION = 3
BUY_RESOURCE = 4
FINISH_BUYING_RESOURCES = 5
BUILD_CITY = 6
FINISH_BUILDING = 7
FIRE_PLANT = 8
NOT_FIRE_PLANT = 9
FINISH_FIRING = 10
DROP_PLANT = 11
DROP_RESOURCE = 12
DRAW_PLANT = 13

MONEY_PAYMENTS = {0: 10,
                  1: 22,
                  2: 33,
                  3: 44,
                  4: 54,
                  5: 64,
                  6: 73,
                  7: 82,
                  8: 90,
                  9: 98,
                  10: 105,
                  11: 112,
                  12: 118,
                  13: 124,
                  14: 129,
                  15: 134,
                  16: 138,
                  17: 142,
                  18: 145,
                  19: 148,
                  20: 150}

NODES_GERMANY = [('FLENSBURG', 0), #0
                 ('KIEL', 0), #1
                 ('CUXHAVEN', 0), #2
                 ('HAMBURG', 0), #3
                 ('WILHELMSHAVEN', 0), #4
                 ('BREMEN', 0), #5
                 ('HANNOVER', 0), #6
                 ('LUBECK', 1), #7
                 ('ROSTOCK', 1), #8
                 ('SCHWERIN', 1), #9
                 ('TORGELOW', 1), #10
                 ('MAGDEBURG', 1), #11
                 ('BERLIN', 1), #12
                 ('FRANKFURT-O', 1), #13
                 ('OSNABRUCK', 2), #14
                 ('DUISBURG', 2), #15
                 ('ESSEN', 2), #16
                 ('MUNSTER', 2), #17
                 ('DORTMUND', 2), #18
                 ('DUSSELDORF', 2), #19
                 ('KASSEL', 2), #20
                 ('HALLE', 3), #21
                 ('LEIPZIG', 3), #22
                 ('ERFURT', 3), #23
                 ('DRESDEN', 3), #24
                 ('FULDA', 3), #25
                 ('WURTZBURG', 3), #26
                 ('NURNBERG', 3), #27
                 ('AACHEN', 4), #28
                 ('KOLN', 4), #29
                 ('FRANFURT-M', 4), #30
                 ('WIESBADEN', 4), #31
                 ('TRIER', 4), #32
                 ('SAARBRUCKEN', 4), #33
                 ('MANNHEIM', 4), #34
                 ('FREIBURG', 5), #35
                 ('STUTTGART', 5), #36
                 ('KONSTANZ', 5), #37
                 ('AUGSBURG', 5), #38
                 ('MUNCHEN', 5), #39
                 ('REGENSBURG', 5), #40
                 ('PASSAU', 5) #41
                 ]
                
CONNECTIONS_GERMANY = [(0, 1, 4), (1, 3, 8), (1, 7, 4), (2, 3, 11), (2, 5, 8), (3, 5, 11),
                       (3, 6, 17), (3, 7, 6), (3, 9, 8), (4, 5, 11), (4, 14, 14), (5, 6, 10),
                       (5, 14, 11), (6, 9, 19), (6, 11, 15), (6, 14, 16), (6, 20, 15), (6, 23, 19), 
                       (7, 9, 6), (8, 9, 6), (8, 10, 19), (9, 10, 19), (9, 11, 16), (9, 12, 18), 
                       (10, 12, 15), (11, 12, 10), (11, 21, 11), (12, 13, 6), (12, 21, 17), (13, 22, 21), 
                       (13, 24, 16), (14, 17, 7), (14, 20, 20), (15, 16, 0), (16, 17, 6), (16, 18, 4), 
                       (16, 19, 2), (17, 18, 2), (18, 20, 18), (18, 29, 10), (18, 30, 20), (19, 28, 9), 
                       (19, 29, 4), (20, 23, 15), (20, 25, 8), (20, 30, 13), (21, 22, 0), (21, 23, 6), 
                       (22, 24, 13), (23, 24, 19), (23, 25, 13), (23, 27, 21), (25, 26, 11), (25, 30, 8), 
                       (26, 27, 8), (26, 30, 13), (26, 34, 10), (26, 36, 12), (26, 38, 19), (27, 38, 18), 
                       (27, 40, 12), (28, 29, 7), (28, 32, 19), (29, 31, 21), (29, 32, 20), (30, 31, 0), 
                       (31, 32, 18), (31, 33, 10), (31, 34, 11), (32, 33, 11), (33, 34, 11), (33, 36, 17), 
                       (34, 36, 6), (35, 36, 16), (35, 37, 14), (36, 37, 16), (36, 38, 15), (37, 38, 17), 
                       (38, 39, 6), (38, 40, 13), (39, 40, 10), (39, 41, 14), (40, 41, 12)
                       ]
                       
ADJACENT_REGIONS_GERMANY = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5)]

# (Plant #, Resource, Num Resources, Cities lit)
PLANTS = [(3, OIL, 2, 1), 
          (4, COAL, 2, 1), 
          (5, COAL_OIL, 2, 1), 
          (6, GARBAGE, 1, 1), 
          (7, OIL, 3, 2), 
          (8, COAL, 3, 2), 
          (9, OIL, 1, 1), 
          (10, COAL, 2, 2), 
          (11, NUCLEAR, 1, 2), 
          (12, COAL_OIL, 2, 2), 
          (13, RENEWABLE, 0, 1), 
          (14, GARBAGE, 2, 2), 
          (15, COAL, 2, 3), 
          (16, OIL, 2, 3), 
          (17, NUCLEAR, 1, 2), 
          (18, RENEWABLE, 0, 2), 
          (19, GARBAGE, 2, 3), 
          (20, COAL, 3, 5), 
          (21, COAL_OIL, 2, 4), 
          (22, RENEWABLE, 0, 2), 
          (23, NUCLEAR, 1, 3), 
          (24, GARBAGE, 2, 4), 
          (25, COAL, 2, 5), 
          (26, OIL, 2, 5), 
          (27, RENEWABLE, 0, 3), 
          (28, NUCLEAR, 1, 4), 
          (29, COAL_OIL, 1, 4), 
          (30, GARBAGE, 3, 6), 
          (31, COAL, 3, 6), 
          (32, OIL, 3, 6), 
          (33, RENEWABLE, 0, 4), 
          (34, NUCLEAR, 1, 5), 
          (35, OIL, 1, 5), 
          (36, COAL, 3, 7), 
          (37, RENEWABLE, 0, 4), 
          (38, GARBAGE, 3, 7), 
          (39, NUCLEAR, 1, 6), 
          (40, OIL, 2, 6), 
          (42, COAL, 2, 6),
          (44, RENEWABLE, 0, 5), 
          (46, COAL_OIL, 3, 7),
          (50, RENEWABLE, 0, 6),  ]

INITIAL_RESOURCES_GERMANY = {COAL: 24,
                             OIL: 18,
                             GARBAGE: 6,
                             NUCLEAR: 3}
                             
STEP_2_HOUSES_GERMANY = {2: 10, 3: 7, 4: 7, 5: 7, 6: 7}
END_HOUSES_GERMANY = {2: 21, 3: 17, 4: 17, 5: 15, 6: 14}

REPLENISH_RESOURCES_GERMANY = {COAL: {2: [3, 4, 3], 3: [4, 5, 3], 4: [5, 6, 4], 5: [5, 7, 5], 6: [7, 9, 6]},
                               OIL: {2: [2, 2, 4], 3: [2, 3, 4], 4: [3, 4, 5], 5: [4, 5, 6], 6: [5, 6, 7]},
                               GARBAGE: {2: [1, 2, 3], 3: [1, 2, 3], 4: [2, 3, 4], 5: [3, 3, 5], 6: [3, 5, 6]},
                               NUCLEAR: {2: [1, 1, 1], 3: [1, 1, 1], 4: [1, 2, 3], 5: [2, 3, 2], 6: [2, 3, 3]}
                               }
                             
NUMBER_PLANTS_NOT_IN_PLAY = {2: 8, 3: 8, 4: 4, 5: 0, 6: 0}
          
MAP_CONFIG = {'GERMANY': {'NODES': NODES_GERMANY,
                          'CONNECTIONS': CONNECTIONS_GERMANY,
                          'ADJACENT': ADJACENT_REGIONS_GERMANY,
                          'INITIAL_RESOURCES': INITIAL_RESOURCES_GERMANY,
                          'STEP_2_HOUSES': STEP_2_HOUSES_GERMANY,
                          'END_HOUSES': END_HOUSES_GERMANY,
                          'REPLENISH_RESOURCES': REPLENISH_RESOURCES_GERMANY}
              }