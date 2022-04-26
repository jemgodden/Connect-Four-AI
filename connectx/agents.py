from abc import ABC
from board import *
import random
import numpy as np
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
        return random.choice([i for i in range(self.board.cols) if self.board.getColCounter(i) != self.board.rows])


class MinimumAgent(Agent):
    def performTurn(self) -> int:
        """
        Agent performs turn by selecting non-full column with minimum value to drop a counter into.
        :return: Int column in which the counter will be dropped.
        """
        return min([i for i in range(self.board.cols) if self.board.getColCounter(i) != self.board.rows])


class LookAheadAgent(Agent):
    def __init__(self, board: Board, player: int, steps: int = 1):
        self.steps = steps
        self.player = player
        super().__init__(board)

    def calculateRewards(self, newBoard: Board) -> int:
        reward = 0
        for i in range(2, newBoard.winCondition):
            reward += newBoard.checkXInARow(self.player, i) * (i ** 3)
        reward += newBoard.checkXInARow(self.player, newBoard.winCondition) * 10000000
        print(reward)
        return reward

    def lookAhead(self) -> list[int]:
        actionRewards = []
        for i in range(self.board.cols):
            boardCopy = copy.deepcopy(self.board)
            boardCopy.updateBoard(i, self.player)
            actionRewards.append(self.calculateRewards(boardCopy))
        return actionRewards

    def filterActions(self, allActions: list[int]) -> list[int]:
        maxReward = max(allActions)
        return [i for i, val in enumerate(allActions) if val == maxReward]

    def chooseAction(self, bestActions) -> int:
        if len(bestActions) != 1:
            return random.choice(bestActions)
        return bestActions[0]

    def performTurn(self) -> int:
        allActionRewards = self.lookAhead()
        bestActions = self.filterActions(allActionRewards)
        action = self.chooseAction(bestActions)
        return action


class PPOAgent(Agent):
    def __init__(self, board: Board):
        self.file_location = 'models/PPO_v1.0/PPO_v1.0_2500000'
        self.model = self.loadModel()
        super().__init__(board)

    def loadModel(self):
        return PPO.load(self.file_location)

    def predictActionProba(self):
        obs = self.model.policy.obs_to_tensor(self.board.getObservation())[0]
        dis = self.model.policy.get_distribution(obs)
        probs = dis.distribution.probs
        probs_np = probs.detach().numpy()
        return probs_np[0]

    def performTurn(self) -> int:
        # action, _state = self.model.predict(self.board.getObservation(), deterministic=True)
        actionProba = self.predictActionProba()
        action = np.argmax(actionProba)
        while self.board.getColCounter(int(action)) == self.board.rows:
            actionProba[action] = 0
            action = np.argmax(actionProba)
        return int(action)
