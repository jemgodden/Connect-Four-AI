from abc import ABC
from connectx.game.board import Board

import random
import numpy as np

from treelib import Tree
import copy

from stable_baselines3 import PPO, A2C


class Agent(ABC):
    def __init__(self, board: Board):
        """
        Base class for all agents.

        :param board: Reference to the game board.
        """
        self.board: Board = board

    def performTurn(self) -> int:
        """
        Outputs agent's action each turn for the game object.

        :return: Integer value for column in which the counter will be dropped.
        """
        pass


class RandomAgent(Agent):
    def performTurn(self) -> int:
        """
        Agent selects a random valid (non-full) column to drop a counter into.
        """
        return random.choice(
            [i for i in range(self.board.cols) if not self.board.fullColCounter(i)])


class MinimumAgent(Agent):
    def performTurn(self) -> int:
        """
        Agent performs turn by selecting non-full column with minimum value to drop a counter into.
        """
        return min([i for i in range(self.board.cols)
                   if not self.board.fullColCounter(i)])


class LookAheadAgent(Agent):
    def __init__(self, board: Board, player: int, steps: int = 4):
        """
        Agent that uses monte-carlo look-ahead strategy to choose the best action.

        The number of steps ahead the agent looks increases the computational complexity exponentially.

        :param board: A reference to the current board state of the game.
        :param player: The player value for the agent.
        :param steps: The number of steps to look ahead.
        """
        self.steps = steps
        self.player = player
        self.oppPlayer = 1 if player == 2 else 1
        super().__init__(board)

    def _calculateRewards(self, board: Board, player: int = None) -> float:
        """
        Calculate the heuristic rewards for the board state.

        :param board: The board state being evaluated.
        :param player: The player value for whom the reward is being calculated.
        :return: Integer value for the heuristic reward.
        """
        if player is None:
            # Default to agent player value.
            player = self.player

        reward = 0
        for i in range(2, board.winCondition):
            # Weighting applied to reward depending on size of connected
            # counters.
            reward += board.checkXInARow(player, i) * (i ** 3)
        reward += board.checkXInARow(player, board.winCondition) * (board.winCondition ** 10)
        return reward

    def _tryAction(self, action: int, player: int, board: Board) -> tuple[float, Board]:
        """
        Allows a player's potential action to be done and reward found.

        :param action: Action being taken/tested.
        :param player: Player value for player taking action.
        :param board: Current state of the game's board.
        :return: Integer value for the heuristic reward of action.
        """
        if board.fullColCounter(action):
            # Return heavily negative reward if full column chosen.
            return -(10 ** 100), board
        boardCopy = copy.deepcopy(board)
        boardCopy.updateBoard(action, player)
        # Track all possible action, reward pair in dictionary.
        return self._calculateRewards(boardCopy, player), boardCopy

    def _oppositionBestTurn(self, board: Board) -> tuple[int, float]:
        """
        Finds the opponent's best turn, using the agent's heuristic, and takes it.

        :param board: Current state of the game's board.
        :return: Tuple of the opponent's best action and the reward they would get for it.
        """
        actions = {}
        for i in range(board.cols):
            reward, boardCopy = self._tryAction(i, self.oppPlayer, board)
            actions[i] = reward

        maxReward = max(actions.values())
        bestActions = [key for key, value in actions.items()
                       if value == maxReward]
        bestAction = random.choice(bestActions)
        return bestAction, maxReward

    def _lookAhead(self, tree: Tree, board: Board,
                   parent: str, parentReward: float, step: int):
        """
        Recursive function to create the look-ahead tree.
        looks 1 agent turn and 1 opposition turn ahead from the prior board state.

        :param tree: Tree structure storing information the agent's current turn's look-ahead.
        :param board: The state of the board prior to this look-ahead step.
        :param parent: The parent node of the current look-ahead set, being the previous turn.
        :param parentReward: The reward of the parent/previous turn.
        :param step: The current step of the look-ahead.
        """
        if step < self.steps:
            # Uncoil recursion if number of steps of look-ahead reached.
            for i in range(board.cols):
                stepReward = parentReward
                # Iterating over all possible actions and adding the new action
                # to the node id.
                nid = parent + str(i)

                reward, boardCopy = self._tryAction(i, self.player, board)
                stepReward += reward * (1 - (step/(10 + self.steps)))
                # Add updated copy of previous board with action, and corresponding reward, as a new node from
                # previous action node.
                tree.create_node(reward, nid, parent=parent)

                if step < self.steps - 1:
                    # Whilst number of steps not reached, predict opposition's optimal turn, and add reward
                    # negatively to this node's reward.
                    oppAction, oppReward = self._oppositionBestTurn(boardCopy)
                    boardCopy.updateBoard(oppAction, self.oppPlayer)
                    # Multiplying opponent reward to make agent more defensive.
                    reward -= oppReward * 1.2

                # From this node, look ahead another step.
                self._lookAhead(tree, boardCopy, nid, reward, step + 1)

    def _lookAheadNSteps(self) -> dict[str: int]:
        """
        Initialises and constructs the look-ahead tree from the agent's current turn's board state.

        :return: Dictionary containing the set of actions, reward from the leaves of the tree, which correlates to the
        nth step of the look-ahead.
        """
        # Create tree and root node.
        tree = Tree()
        tree.create_node(0, '')

        self._lookAhead(tree, self.board, '', 0, 0)

        return {leaf.identifier: leaf.tag for leaf in tree.leaves()}

    @staticmethod
    def _filterActions(allActions: dict[str: int]) -> list[str]:
        """
        Filter all possible actions down to equally optimal actions.

        :param allActions: Dictionary containing action, reward pairs for all the agent's possible actions in this turn.
        :return: List of strings representing optimal actions, all of which give an equal reward.
        """
        maxReward = max(allActions.values())
        return [action for action, reward in allActions.items()
                if reward == maxReward]

    @staticmethod
    def _chooseAction(optimalActions: list[str]) -> int:
        """
        Choose an action randomly from the set of equally optimal actions.

        :param optimalActions: List of strings representing optimal set of actions across n step, all of which give an
        equal reward.
        :return: Integer corresponding to the action being chosen, and found from the first action from the set of
        optimal actions.
        """
        bestAction = random.choice(optimalActions)
        return int(bestAction[0])

    def performTurn(self) -> int:
        """
        Filter all actions retrieved from the look-ahead tree to get the best column.

        :return: Integer value representing the action that the agent will take.
        """
        allActions = self._lookAheadNSteps()
        optimalActions = self._filterActions(allActions)
        action = self._chooseAction(optimalActions)
        return action


class RLAgent(Agent):
    def __init__(self, board: Board, filepath: str):
        """
        Base class for reinforcement learning agents.

        :param board: Reference to the game board.
        :param filepath: Filepath for the agent's model.
        """
        super().__init__(board)
        self.model = self._loadModel(filepath)

    @staticmethod
    def _loadModel(filePath):
        """
        Load the agent's model from a file.

        :param filePath: Filepath that the agent's model is stored in.
        """
        pass

    def _predictActionProba(self) -> np.float:
        """
        Retrieve the probability of the model taking each possible action in action space depending on current board.
        See: https://stackoverflow.com/questions/66428307/how-to-get-action-propability-in-stable-baselines-3

        :return: Array of floats indicating probability of each action in the action space.
        """
        obs = self.model.policy.obs_to_tensor(self.board.getObservation())[0]
        dis = self.model.policy.get_distribution(obs)
        probs = dis.distribution.probs
        probs_np = probs.detach().numpy()
        return probs_np[0]

    def performTurn(self) -> int:
        """
        Agent uses action space probabilities to decide on its action.
        """
        actionProba = self._predictActionProba()
        action = np.argmax(actionProba)
        while self.board.getColCounter(int(action)) == self.board.rows:
            # Selects action with the highest probability that doesn't
            # correspond to a full column.
            actionProba[action] = 0
            action = np.argmax(actionProba)
        return int(action)


class PPOAgent(RLAgent):
    def __init__(self, board: Board,
                 filePath: str = 'connectx/models/PPO_6-7-4_v0.1/PPO_6-7-4_v0.1_50000'):
        """
        Agent that uses a Proximal Policy Optimisation policy gradient method.
        """
        super().__init__(board, filePath)

    @staticmethod
    def _loadModel(filePath) -> PPO:
        return PPO.load(filePath)


class A2CAgent(RLAgent):
    def __init__(self, board: Board,
                 filePath: str = 'connectx/models/A2C_6-7-4_v0.1/A2C_6-7-4_v0.1_50000'):
        """
        Agent that uses an Advantage Actor Critic policy gradient method.
        """
        super().__init__(board, filePath)

    @staticmethod
    def _loadModel(filePath) -> A2C:
        return A2C.load(filePath)
