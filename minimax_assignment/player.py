#!/usr/bin/env python3
import random
import math
import time
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
    
    def isInstantWin(self, hook_positions, fish_positions):
        return hook_positions == fish_positions
    
    def state_to_str(self, state):
        return str(state.get_hook_positions()) + str(state.get_fish_positions())
    
    @lru_cache(None)  # Cache heuristic calculations
    def heuristic_function(self, current_node):
        p_score = current_node.state.player_scores[0]
        o_score = current_node.state.player_scores[1]
        
        (p_hook_x, p_hook_y) = current_node.state.hook_positions[0]
        (o_hook_x, o_hook_y) = current_node.state.hook_positions[1]
        
        fish_positions = current_node.state.fish_positions
        fish_scores = current_node.state.fish_scores
        
        value = 0
        
        for idx, (fish_x, fish_y) in fish_positions.items():
            fish_value = fish_scores[idx]
            p_distance = min(abs(p_hook_x - fish_x), 20 - abs(p_hook_x - fish_x)) + abs(p_hook_y - fish_y)
            # o_distance = min(abs(o_hook_x - fish_x), 20 - abs(o_hook_x - fish_x)) + abs(o_hook_y - fish_y)
            
            # Instant win check
            if fish_value > 0 and self.isInstantWin((p_hook_x, p_hook_y), (fish_x, fish_y)):
                return math.inf
            if fish_value > 0 and self.isInstantWin((o_hook_x, o_hook_y), (fish_x, fish_y)):
                value -= math.inf
            
            value = max(fish_value * math.exp(-p_distance), value)
        
        s_diff = 3
        
        return s_diff * (p_score - o_score) + value

            
        
    def minmax(self, current_node, depth, a, b, visited_nodes, maximizing_player=True, start_time=0):
        if time.time() - start_time > 0.05:
            raise TimeoutError
        
        MAX = math.inf
        v = 0
        k = self.state_to_str(current_node.state)
        if k in visited_nodes and visited_nodes[k][0] >= depth:
            return visited_nodes[k][1]
        
        nodes = current_node.compute_and_get_children()
        nodes.sort(key=lambda node: self.heuristic_function(node), reverse=True)
        
        if depth == 0 or len(nodes) == 0:
            v = self.heuristic_function(current_node) #static value of this posistion
        elif maximizing_player:
            max_eval = -MAX
            for node in nodes:
                _eval = self.minmax(node, depth-1, a, b, visited_nodes, False, start_time)
                v = max(max_eval, _eval)
                a = max(a, _eval)
                if b <= a:
                    break
        else:
            min_eval = MAX
            for node in nodes:
                _eval = self.minmax(node, depth-1, a, b, visited_nodes, True, start_time)
                v = min(min_eval, _eval)
                b = min(b, _eval)
                if b <= a:
                    break
        
        visited_nodes.update({k:[depth,v]})
        return v
        
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
        start_time = time.time()
        initial_tree_node.compute_and_get_children()
        max_val = -math.inf
        best_move = 0
        depth = 0
        visited_nodes = dict()
        
        while True:
            try:
                for node in initial_tree_node.children:
                    val = self.minmax(node, depth, -math.inf, math.inf, visited_nodes, False, start_time)
                    if(val == math.inf): # Marked as a instant win
                        best_move = node.move
                        return ACTION_TO_STR[best_move]
                    if(max_val < val):
                        max_val = val
                        best_move = node.move
                depth = depth + 1
            except:
                break

        
        return ACTION_TO_STR[best_move]
