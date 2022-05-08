import gym
from .game import TrainingGame

import numpy as np


class ConnectXEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 verbose: bool = False,
                 rows: int = 6,
                 cols: int = 7,
                 winCondition: int = 4,
                 player1: str or None = None,
                 player2: str or None = None):
        """
        This class is used to create a connect-x environment for the agents to use to train.

        :param verbose: 
        :param winCondition: 
        :param boardRows: 
        :param boardCols: 
        :param player1: 
        :param player2: 
        """
        super(ConnectXEnv, self).__init__()

        self.game = TrainingGame(verbose=verbose,
                                 boardRows=rows,
                                 boardCols=cols,
                                 winCondition=winCondition,
                                 player1=player1,
                                 player2=player2)
        self.action_space = gym.spaces.Discrete(self.game.board.cols)
        self.observation_space = gym.spaces.Box(low=-1, high=self.game.board.rows, shape=(self.game.board.maxMoves + len(
            self.game.board.colCounters()),), dtype=np.float64)
        # self.prev_actions = None # Removed as it may not be adding much.
        self.observation = None
        self.reward = None
        self.done = False
        self.firstTurn = True
        self.agentNum = self._getAgentVal()
        self.opponentNum = 1 if self.agentNum == 2 else 2

    def _getAgentVal(self):
        return [i+1 for i, name in enumerate(self.game.players) if name is None][0]

    def _getPlayerVal(self, player: int) -> int:
        return int(self.game.player(player) is None)+1

    def calculateSubReward(self, player: int, polarity: int = 1) -> float:
        reward = 0
        for i in range(2, self.game.board.winCondition):
            reward += self.game.board.checkXInARow(self._getPlayerVal(player), i) * (((i - 1) ** 2) * 0.005) * polarity
        return reward

    # def trainingStep(self, action: int):
    #     """
    #     Should make it possible for the agent to go first too:
    #         Opponent takes turn (After THEN statements).
    #
    #     Opponent takes turn.
    #     Use action to take turn.
    #     THEN
    #     Append action.
    #     Update observation.
    #     Check for sub-rewards and allocate.
    #     Check if done and allocate rewards.
    #
    #     :param action:
    #     :return:
    #     """
    #     done = False
    #     reward = 0.0
    #
    #     if self.game.board.getColCounter(action) == self.game.board.rows:
    #         # Ends game if column full.
    #         reward = -10.0
    #         done = True
    #
    #     if not done:
    #         # Agent being trained takes its turn.
    #         self.game.trainingAgentTurn(action, self._getPlayerVal(2))
    #         # Checks if action caused game to end in a win for training agent.
    #         if self.game.board.checkXInARow(self._getPlayerVal(2)) > 0:
    #             reward += 10.0
    #             done = True
    #         else:
    #             # Calculates sub-reward if game not ended.
    #             reward += self.calculateSubReward(2)
    #
    #         # Opponent gets to take turn.
    #         self.game.opponentTurn(self._getPlayerVal(1))
    #         # Check if opponent's turn ended game.
    #         if self.game.board.checkXInARow(self._getPlayerVal(1)) > 0:
    #             reward = -10.0
    #             done = True
    #         # Calculate negative rewards.
    #         reward -= self.calculateSubReward(1)
    #
    #     # Create observation space and return relevant information.
    #     observation = self.game.board.getObservation()
    #     info = {}
    #     return observation, reward, done, info

    # def step(self, action: int):
    #     """
    #     Take a step within the environment.
    #
    #     :param action: The action that the player/agent is taking.
    #     """
    #     # If first turn and training agent is player 2: player 1 takes turn.
    #     return self.trainingStep(action)

    def trainingStep(self, action: int):
        """
        temp

        :param action:
        :return:
        """
        done = False
        reward = 0.0

        if self.game.board.getColCounter(action) == self.game.board.rows:
            # Ends game if column full.
            reward = -10.0
            done = True

        if not done:
            # Agent being trained takes its turn.
            self.game.trainingAgentTurn(action, self.agentNum)
            # Checks if action caused game to end in a win for training agent.
            if self.game.board.checkXInARow(self.agentNum) > 0:
                reward += 10.0
                done = True
            else:
                # Calculates sub-reward if game not ended.
                reward += self.calculateSubReward(self.agentNum)

                # Opponent gets to take turn.
                self.game.opponentTurn(self.opponentNum)
                # Check if opponent's turn ended game.
                if self.game.board.checkXInARow(self.opponentNum) > 0:
                    reward = -10.0
                    done = True
                else:
                    # Calculate negative rewards.
                    reward -= self.calculateSubReward(self.opponentNum, -1)

        # Create observation space and return relevant information.
        observation = self.game.board.getObservation()
        info = {}
        return observation, reward, done, info

    def step(self, action: int):
        """
        Take a step within the environment.

        :param action: The action that the player/agent is taking.
        """
        if self.firstTurn and self.opponentNum == 1:
            self.game.opponentTurn(self.opponentNum)
            self.firstTurn = False
        return self.trainingStep(action)

    def reset(self):
        """
        Reset the board so the environment can be reused.

        :return observation: Return the observation of the reset board.
        """
        self.game.board.resetBoard()

        self.firstTurn = True

        # Put this into step?
        if self.game.player(1) is not None:
            self.game.opponentTurn(self._getPlayerVal(1))

        observation = self.game.board.getObservation()
        return observation  # reward, done, info can't be included

    def render(self, mode='human'):
        """
        Show the board during the game.

        :param mode: The type of render to display.
        """
        self.game.board.printBoard(None)

    # def close (self):
