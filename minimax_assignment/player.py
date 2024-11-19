#!/usr/bin/env python3
import random
import math
from functools import lru_cache

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR


class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate first message (Do not remove this line!)
        first_msg = self.receiver()

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(initial_tree_node=node)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})
    
    @lru_cache(None)  # Cache heuristic calculations
    def heuristic_function(self, current_node):
        (max_hook_x, max_hook_y) = current_node.state.hook_positions[0]
        (min_hook_x, min_hook_y) = current_node.state.hook_positions[1]
        uncaught_fishes = current_node.state.fish_positions
        fish_scores = current_node.state.fish_scores
        
        player_advantage = 0
        opponent_advantage = 0
        for idx, (x, y) in uncaught_fishes.items():
            fish_score = fish_scores[idx]
            p_distance = (max_hook_x - x) ** 2 + (max_hook_y - y) ** 2 
            o_distance = (min_hook_x - x) ** 2 + (min_hook_y - y) ** 2
            
            player_advantage += fish_score / (p_distance + 1)
            opponent_advantage += fish_score / (o_distance + 1)

        return player_advantage - opponent_advantage
            
            
        
    def minmax(self, current_node, depth, a, b, maximizing_player=True):
        current_node.compute_and_get_children()
        if depth == 0 or not current_node.children:
            return self.heuristic_function(current_node=current_node) #static value of this posistion
        
        current_node.children.sort(key=lambda node: self.heuristic_function(node), reverse=maximizing_player)
        
        if maximizing_player:
            max_eval = -9999
            for node in current_node.children:
                _eval = self.minmax(current_node=node, depth=depth-1, a=a, b=b, maximizing_player=False)
                max_eval = max(max_eval, _eval)
                a = max(a, _eval)
                if b <= a:
                    break
            return max_eval
        else:
            min_eval = 9999
            for node in current_node.children:
                _eval = self.minmax(current_node=node, depth=depth-1, a=a, b=b, maximizing_player=True)
                min_eval = min(min_eval, _eval)
                b = min(b, _eval)
                if b <= a:
                    break
            return min_eval
        
    def search_best_next_move(self, initial_tree_node):
        """
        Use minimax (and extensions) to find best possible next move for player 0 (green boat)
        :param initial_tree_node: Initial game tree node
        :type initial_tree_node: game_tree.Node
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE USING MINIMAX ###

        # NOTE: Don't forget to initialize the children of the current node
        #       with its compute_and_get_children() method!
        initial_tree_node.compute_and_get_children()
        max_val = -9999
        next_node = initial_tree_node.children[0]
        for node in initial_tree_node.children:
            val = self.minmax(current_node=node, depth=3, a=-9999, b=9999, maximizing_player=True)
            if(max_val < val):
                max_val = val
                next_node = node

        move = next_node.move
        return ACTION_TO_STR[move] if next_node else 0
