from board import *
import random


class Agent:
    def __init__(self, board: Board):
        """
        :param board: Board class for the current game's board.
        """
        self.board: Board = board

    def performTurn(self) -> int:
        """
        Agent performs turn by selecting a random non-full column to drop a counter into.
        :return: Int column in which the counter will be dropped.
        """
        return random.choice([i + 1 for i in range(self.board.cols) if self.board.colCounter(i) != self.board.rows])


class MinimumAgent(Agent):
    def performTurn(self) -> int:
        """
        Agent performs turn by selecting non-full column with minimum value to drop a counter into.
        :return: Int column in which the counter will be dropped.
        """
        return min([i + 1 for i in range(self.board.cols) if self.board.colCounter(i) != self.board.rows])


# class PPOAgent(Agent):
#     def __init__(self, board: Board):
#         self.model = loadModel()
#         super().__init__(board)
#
#     def loadModel(self):
#
#     def performTurn(self):
