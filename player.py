#!/usr/bin/env python3
import time
from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR

class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()
        self.history_states = {}
        self.best_positions_dict = {}

    def player_loop(self):
        # Generate game tree object
        first_msg = self.receiver()
        # Initialize your minimax model
        model = self.initialize_model(initial_data=first_msg)

        while True:
            msg = self.receiver()
            self.history_states.clear()
            # Create the root node of the game tree
            node = Node(message=msg, player=0)
    
            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(
                model=model, initial_tree_node=node)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def initialize_model(self, initial_data):

        return initial_data

    def search_best_next_move(self, model, initial_tree_node):
        first_level = 0

        # best state punctuation currently in iterative deepening
        current_best = float("-inf") 

        #start counting time
        initial_time = time.time() 

        # best next move until now in iterative deepening, inizialized randomly 
        current_best_move = 0 
        
        #for move ordering
        self.best_positions_dict.clear()
        self.best_positions = {"n":0}
        key = "n"

        #loop that does iterative deepening
        for level in [1,3,5,7,9,11,13,15,17,19]: 
            best = self.alphabeta_iter(initial_tree_node, 0, first_level, level, initial_time, float("-inf"), float("+inf"),  key)
            
            if(best[1]>current_best):
                current_best = best[1]
                current_best_move = best[0]

            time_diff = time.time()-initial_time
            if(time_diff>0.055):
                break

        return ACTION_TO_STR[current_best_move]


    def alphabeta_iter(self, node, player, depth, iter_limit, start_time, alpha, beta, key):
        if (depth == iter_limit) or ((time.time()-start_time) > 0.055):
            heuristica_value = self.heuristic(node)
            return (node.move, heuristica_value)

        children = node.compute_and_get_children()
        num_children = len(children)
        movement = node.move
        best_move = self.get_best_move(key)
        order1  = [x for x in range(num_children) if x is not best_move]
        order = [best_move] + order1
        if(num_children == 1):
            order = [0]

        if(player == 0):
            bestPossible = float("-inf")
            for child in order:
                v = self.alphabeta_iter(children[child], 1, depth +1, iter_limit, start_time, alpha, beta, key+ACTION_TO_STR[children[child].move][0])
                if(v[1]>bestPossible):
                    bestPossible = v[1]
                    movement = children[child].move
                if (v[1]>alpha):
                    alpha = v[1]  
                if (beta<=alpha):
                    break
            self.best_positions_dict[key] = movement
            return (movement, bestPossible)

        if(player == 1):
            bestPossible = float("inf")
            for child in order:
                v = self.alphabeta_iter(children[child], 0, depth +1, iter_limit, start_time, alpha, beta, key+ACTION_TO_STR[children[child].move][0])
                if(v[1]<bestPossible):
                    bestPossible = v[1]
                    movement = children[child].move
                if (v[1]<beta):
                    beta = v[1]
                if (beta<=alpha):
                    break
            self.best_positions_dict[key] = movement
            return (movement, bestPossible)

    def heuristic_basic(self, node):
        return node.state.player_scores[0] - node.state.player_scores[1]

    def heuristic(self, node):
        hooks = node.state.get_hook_positions()
        fish = node.state.get_fish_positions()
        fish_values = node.state.get_fish_scores()  
        max_score = node.state.player_scores[0]
        min_score = node.state.player_scores[1]
        caught_fish_value = 0
        fish_cought = False

        f1 = max_score-min_score
        f2 = 0.0

        best_value_close = 0
        for key, value in fish.items():
            valuex = value[0]
            hooksx = hooks[0][0]
            x = min(abs(hooksx-valuex), abs(hooksx+20-valuex), abs(hooksx-20-valuex))
            y = abs(hooks[0][1] - value[1])
            dist = x+y

            if (dist < 3) and (dist > 0) and (fish_values[key]>best_value_close):
                best_value_close = fish_values[key]           
            if dist == 0:
                fish_cought = True
                caught_fish_value = fish_values[key]
                
            f2 = f2 + fish_values[key]/(dist+0.01)

        if (fish_cought) and (best_value_close > caught_fish_value+5):
            f2 = f2-100000

        return 1*f1+0.01*f2

    def get_best_move(self, key):
        if key not in self.best_positions_dict:
            self.best_positions_dict[key] = 0
        return self.best_positions_dict[key]
