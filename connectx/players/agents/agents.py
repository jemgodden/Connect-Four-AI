from connectx.players.players import Player
from connectx.game.board import Board

import time
import random

from treelib import Tree
import copy

# from stable_baselines3 import PPO, A2C


class Agent(Player):
    def __init__(self, player_num: int, board: Board, verbose: bool):
        """
        Base class for all agents.

        :param verbose: Boolean that tells the agent if it should say what it is doing.
        """
        super().__init__(player_num, board)
        self.verbose = verbose

    def perform_turn(self):
        if self.verbose:
            print("Agent is choosing a move...\n")
            time.sleep(random.uniform(0.8, 1.2))


class RandomAgent(Agent):
    def perform_turn(self) -> int:
        """
        Agent selects a random valid (non-full) column to drop a counter into.
        """
        super().perform_turn()
        return random.choice(
            [i for i in range(self.board.cols) if not self.board.check_col_full(i)])


class MinimumAgent(Agent):
    def perform_turn(self) -> int:
        """
        Agent performs turn by selecting non-full column with minimum value to drop a counter into.
        """
        super().perform_turn()
        return min([i for i in range(self.board.cols)
                    if not self.board.check_col_full(i)])


class LookAheadAgent(Agent):
    def __init__(self, player_num: int, board: Board, verbose: bool, steps: int = 4):
        """
        Agent that uses monte-carlo look-ahead strategy to choose the best action.

        The number of steps ahead the agent looks increases the computational complexity exponentially.

        :param board: A reference to the current board state of the game.
        :param player_num: The player value for the agent.
        :param steps: The number of steps to look ahead.
        """
        super().__init__(player_num, board, verbose)
        self.opp_player_num = 1 if player_num == 2 else 2
        self.steps = steps

    def _calculate_rewards(self, board: Board, player: int = None) -> float:
        """
        Calculate the heuristic rewards for the board state.

        :param board: The board state being evaluated.
        :param player: The player value for whom the reward is being calculated.
        :return: Integer value for the heuristic reward.
        """
        if player is None:
            # Default to agent player value.
            player = self.player_num

        reward = 0
        for i in range(2, board.win_condition):
            # Weighting applied to reward depending on size of connected counters.
            reward += board.check_for_lines(player, i) * (i ** 3)
        reward += board.check_for_lines(player, board.win_condition) * (board.win_condition ** 10)
        return reward

    def _try_action(self, action: int, player: int, board: Board) -> tuple[float, Board]:
        """
        Allows a player's potential action to be done and reward found.

        :param action: Action being taken/tested.
        :param player: Player value for player taking action.
        :param board: Current state of the game's board.
        :return: Integer value for the heuristic reward of action.
        """
        board_copy = copy.deepcopy(board)

        if board_copy.check_col_full(action):
            # Return heavily negative reward if full column chosen.
            return -(10 ** 100), board_copy

        board_copy.update_board(action, player)
        # Track all possible action, reward pair in dictionary.
        return self._calculate_rewards(board_copy, player), board_copy

    def _opposition_optimal_action(self, board: Board) -> tuple[int, float]:
        """
        Finds the opponent's best turn, using the agent's heuristic, and takes it.

        :param board: Current state of the game's board.
        :return: Tuple of the opponent's best action and the reward they would get for it.
        """
        actions = {}
        for i in range(board.cols):
            reward, board_copy = self._try_action(i, self.opp_player_num, board)
            actions[str(i)] = reward

        optimal_action, max_reward = self._choose_optimal_action(actions)
        return optimal_action, max_reward

    def _look_ahead(self, tree: Tree, board: Board, parent: str, parent_reward: float, step: int):
        """
        Recursive function to create the look-ahead tree.
        looks 1 agent turn and 1 opposition turn ahead from the prior board state.

        :param tree: Tree structure storing information the agent's current turn's look-ahead.
        :param board: The state of the board prior to this look-ahead step.
        :param parent: The parent node of the current look-ahead set, being the previous turn.
        :param parent_reward: The reward of the parent/previous turn.
        :param step: The current step of the look-ahead.
        """
        if step < self.steps:
            # Uncoil recursion if number of steps of look-ahead reached.
            for i in range(board.cols):
                step_reward = parent_reward
                # Iterate over all possible actions and adding the new action to the node id.
                nid = parent + str(i)

                reward, board_copy = self._try_action(i, self.player_num, board)
                step_reward += reward * (1 - (step / (10 + self.steps)))

                if step < self.steps - 1:
                    # Whilst number of steps not reached, predict opposition's optimal turn, and add reward
                    # negatively to this node's reward.
                    opp_action, opp_reward = self._opposition_optimal_action(board_copy)
                    board_copy.update_board(opp_action, self.opp_player_num)
                    # Multiplying opponent reward to make agent more defensive.
                    step_reward -= opp_reward * 1.5

                # Add updated copy of previous board with action, and corresponding reward, as a new node from
                # previous action node.
                tree.create_node(step_reward, nid, parent=parent)

                # From this node, look ahead another step.
                self._look_ahead(tree, board_copy, nid, step_reward, step + 1)

    def _look_ahead_N_steps(self) -> dict[str: int]:
        """
        Initialises and constructs the look-ahead tree from the agent's current turn's board state.

        :return: Dictionary containing the set of actions, reward from the leaves of the tree, which correlates to the
        nth step of the look-ahead.
        """
        # Create tree and root node.
        tree = Tree()
        tree.create_node(0, '')

        self._look_ahead(tree, self.board, '', 0, 0)

        return {leaf.identifier: leaf.tag for leaf in tree.leaves()}

    @staticmethod
    def _choose_optimal_action(all_actions: dict[str: int]) -> tuple[int, float]:
        """
        Filter all possible actions down to equally optimal actions.

        :param all_actions: Dictionary containing action, reward pairs for all the agent's possible actions in this
            turn.
        :return: List of strings representing optimal actions, all of which give an equal reward.
        """
        max_reward = max(all_actions.values())
        optimal_actions = [action for action, reward in all_actions.items() if reward == max_reward]
        return int(random.choice(optimal_actions)[0]), max_reward

    def perform_turn(self) -> int:
        """
        Filter all actions retrieved from the look-ahead tree to get the best column.

        :return: Integer value representing the action that the agent will take.
        """
        super().perform_turn()
        all_actions = self._look_ahead_N_steps()
        action, max_reward = self._choose_optimal_action(all_actions)
        print(action)
        return action


# class RLAgent(Agent):
#     def __init__(self, player_num: int, board: Board, verbose: bool, filepath: str):
#         """
#         Base class for reinforcement learning agents.
#
#         :param board: Reference to the game board.
#         :param filepath: Filepath for the agent's model.
#         """
#         super().__init__(player_num, board, verbose)
#         self.model = self._load_model(filepath)
#
#     @staticmethod
#     def _load_model(filePath):
#         """
#         Load the agent's model from a file.
#
#         :param filePath: Filepath that the agent's model is stored in.
#         """
#         pass
#
#     def _predict_action_proba(self) -> np.float:
#         """
#         Retrieve the probability of the model taking each possible action in action space depending on current board.
#         See: https://stackoverflow.com/questions/66428307/how-to-get-action-propability-in-stable-baselines-3
#
#         :return: Array of floats indicating probability of each action in the action space.
#         """
#         obs = self.model.policy.obs_to_tensor(self.board.get_observation())[0]
#         dis = self.model.policy.get_distribution(obs)
#         probs = dis.distribution.probs
#         probs_np = probs.detach().numpy()
#         return probs_np[0]
#
#     def perform_turn(self) -> int:
#         """
#         Agent uses action space probabilities to decide on its action.
#         """
#         super().perform_turn()
#         action_proba = self._predict_action_proba()
#         action = np.argmax(action_proba)
#         while self.board.get_col_counter(int(action)) == self.board.rows:
#             # Selects action with the highest probability that doesn't correspond to a full column.
#             action_proba[action] = 0
#             action = np.argmax(action_proba)
#         return int(action)
#
#
# class PPOAgent(RLAgent):
#     def __init__(self, player_num: int, board: Board, verbose: bool,
#                  filepath: str = 'connectx/models/PPO_6-7-4_v0.1/PPO_6-7-4_v0.1_50000'):
#         """
#         Agent that uses a Proximal Policy Optimisation policy gradient method.
#         """
#         super().__init__(player_num, board, verbose, filepath)
#
#     @staticmethod
#     def _loadModel(filepath) -> PPO:
#         return PPO.load(filepath)
#
#
# class A2CAgent(RLAgent):
#     def __init__(self, player_num: int, board: Board, verbose: bool,
#                  filepath: str = 'connectx/models/A2C_6-7-4_v0.1/A2C_6-7-4_v0.1_50000'):
#         """
#         Agent that uses an Advantage Actor Critic policy gradient method.
#         """
#         super().__init__(player_num, board, verbose, filepath)
#
#     @staticmethod
#     def _loadModel(filepath) -> A2C:
#         return A2C.load(filepath)
