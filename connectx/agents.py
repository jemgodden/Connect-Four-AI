from board import *
import random


class Agent:
    def __init__(self, board: Board):
        """
        :param board: Board class for the current game's board.
        """
        self.board: Board = board


class RandomAgent(Agent):
    def performTurn(self) -> int:
        """
        Agent performs turn by selecting column to drop counter into.
        :return: Int column in which the counter will be dropped.
        """
        return random.choice([i + 1 for i in range(self.board.cols) if self.board.colCounter(i) != self.board.rows])


# class PPOAgent(Agent):
#     def __init__(self, board: Board):
#         self.model = loadModel()
#         super().__init__(board)
#
#     def loadModel(self):
#
#     def performTurn(self):
