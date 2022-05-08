from abc import ABC
from .board import Board

import random
import numpy as np

from treelib import Tree
import copy

from stable_baselines3 import PPO


class Agent(ABC):
    def __init__(self, board: Board):
        """
        :param board: Board class for the current game's board.
        """
        self.board: Board = board

    def performTurn(self) -> int:
        pass


class RandomAgent(Agent):
    def performTurn(self) -> int:
        """
        Agent performs turn by selecting a random non-full column to drop a counter into.
        :return: Int column in which the counter will be dropped.
        """
        return random.choice([i for i in range(self.board.cols) if not self.board.fullColCounter(i)])


class MinimumAgent(Agent):
    def performTurn(self) -> int:
        """
        Agent performs turn by selecting non-full column with minimum value to drop a counter into.
        :return: Int column in which the counter will be dropped.
        """
        return min([i for i in range(self.board.cols) if not self.board.fullColCounter(i)])


class LookAheadAgent(Agent):
    def __init__(self, board: Board, player: int, steps: int = 4):
        self.steps = steps
        self.player = player
        self.oppPlayer = 1 if player == 2 else 1
        super().__init__(board)

    def calculateRewards(self, board: Board, player: int = None) -> int:
        if player is None:
            player = self.player
        reward = 0
        for i in range(2, board.winCondition):
            reward += board.checkXInARow(player, i) * (i ** 3)
        reward += board.checkXInARow(player, board.winCondition) * (board.winCondition ** 5)
        return reward

    def oppositionBestTurn(self, board: Board, player: int) -> tuple[int, int]:
        actions = {}
        for i in range(board.cols):
            if board.fullColCounter(i):
                actions[i] = -(10 ** 10)
            else:
                boardCopy = copy.deepcopy(board)
                boardCopy.updateBoard(i, player)
                actions[i] = self.calculateRewards(boardCopy, player)
        maxReward = max(actions.values())
        bestActions = [key for key, value in actions.items() if value == maxReward]
        bestAction = random.choice(bestActions)
        return bestAction, maxReward

    def lookAhead(self, tree: Tree, board: Board, parent: str, parentReward: int, step: int):
        if step != self.steps:
            for i in range(board.cols):
                nid = parent + str(i)
                if board.fullColCounter(i):
                    tree.create_node(-(10 ** 10), nid, parent=parent)
                else:
                    nid = parent + str(i)
                    boardCopy = copy.deepcopy(board)
                    boardCopy.updateBoard(i, self.player)
                    reward = parentReward + self.calculateRewards(boardCopy)
                    tree.create_node(reward, nid, parent=parent)

                    if step != self.steps - 1:
                        oppAction, oppReward = self.oppositionBestTurn(boardCopy, self.oppPlayer)
                        boardCopy.updateBoard(oppAction, self.oppPlayer)
                        reward -= oppReward * 2

                    self.lookAhead(tree, boardCopy, nid, reward, step+1)

    def lookAheadNSteps(self) -> dict[str: int]:
        tree = Tree()
        tree.create_node(0, '')  # Creating root node.
        self.lookAhead(tree, self.board, '', 0, 0)
        return {leaf.identifier: leaf.tag for leaf in tree.leaves()}

    def filterActions(self, allActions: dict[str: int]) -> list[str]:
        maxReward = max(allActions.values())
        return [action for action, reward in allActions.items() if reward == maxReward]

    def chooseAction(self, bestActions: list[str]) -> int:
        bestAction = random.choice(bestActions)
        return int(bestAction[0])

    def performTurn(self) -> int:
        allActions = self.lookAheadNSteps()
        bestActions = self.filterActions(allActions)
        action = self.chooseAction(bestActions)
        return action


class PPOAgent(Agent):
    def __init__(self, board: Board, filePath: str = 'connectx/models/PPO_v0.1/PPO_v0.1_200000'):
        self.model = self.loadModel(filePath)
        super().__init__(board)

    @staticmethod
    def loadModel(filePath):
        return PPO.load(filePath)

    def predictActionProba(self):
        obs = self.model.policy.obs_to_tensor(self.board.getObservation())[0]
        dis = self.model.policy.get_distribution(obs)
        probs = dis.distribution.probs
        probs_np = probs.detach().numpy()
        return probs_np[0]

    def performTurn(self) -> int:
        actionProba = self.predictActionProba()
        action = np.argmax(actionProba)
        while self.board.getColCounter(int(action)) == self.board.rows:
            actionProba[action] = 0
            action = np.argmax(actionProba)
        return int(action)
