from copy import deepcopy

from game_state import GameState
from game_memory import GameMemory
import config
import traceback

from agent_heuristic import Agent_Heuristic
from agent_nn import Agent_NN

def play_game(agents_obj):
    game = GameState(agents_obj = agents_obj)
    game_memory = GameMemory(game.uuid)
    
    while game.game_phase != config.PHASE_END_GAME:
        player_moving = game.get_player_moving()
        move, player_moving = game.players[player_moving].ai.move(game)
        if player_moving > -1:
            save_game = deepcopy(game)
            game_memory.add_to_memory_states(player_moving, save_game)
        
        game.ai_do_move(move)

    game_result = []
    for p in range(5):
        game_result.append(game.ai_get_result(p))
    game_memory.add_game_result(game_result)

    game_memory.dump_to_file()
    
    # Write result
    with open('results.txt', 'a') as output:
        players = []
        for p in range(5):
            players.append(game.players[p].ai.agent_name)
            
        output.write(repr(players) + ": " + str(game.winner) + "\n")
    
agents = config.CURRENT_AGENT
games_played = 0
agents_obj = []

for a in agents:
    print ("Loading Agent: " + str(a))
    if a == "h":
        net = Agent_Heuristic()
    else:
        net = Agent_NN(enable_cache = True)
        net.nn_read(a)
    
    agents_obj.append((str(a), net))

while games_played < config.SELF_PLAY_BATCH_SIZE:
    try:
        play_game(agents_obj)
        games_played += 1
    except Exception as e:
        with open('log.txt', 'a') as output:
            traceback.print_exc(file = output)
            output.write("\n\n *****************************************************************\n")
