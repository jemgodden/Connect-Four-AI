import gym
from connectx.game.game import TrainingGame

import numpy as np


class ConnectXEnv(gym.Env):
    """
    Custom Environment for Connect X that follows gym interface.
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
        This class is used to create a Connect-X Environment for the agents to use to train.

        :param verbose: Flag for whether information is printed to the console.
        :param rows: Integer value for the number of rows the board will have.
        :param cols: Integer value for the number of columns the board will have.
        :param winCondition: Integer value for the number of counters in a row required to win.
        :param player1: String indicating the player taking the role of player 1.
        :param player2: String indicating the player taking the role of player 2.
        """
        super(ConnectXEnv, self).__init__()

        # Use a child of game specifically made for agent training.
        self.game = TrainingGame(verbose=verbose,
                                 boardRows=rows,
                                 boardCols=cols,
                                 winCondition=winCondition,
                                 player1=player1,
                                 player2=player2)
        self.agentNum = self._getAgentVal()
        self.opponentNum = 1 if self.agentNum == 2 else 2

        self.action_space = gym.spaces.Discrete(self.game.board.cols)

        # self.prev_actions = None
        # Removed this feature this can be classified as a Markov state game
        # where history is irrelevant.
        self.observation_space = gym.spaces.Box(low=-1, high=self.game.board.rows,
                                                shape=(
                                                    self.game.board.maxMoves + len(self.game.board.col_counters()),),
                                                dtype=np.float64)

        self.firstTurn = True

    def _getAgentVal(self) -> int:
        """
        Function to obtain the player value for the agent.

        :return: Integer defining the player value of the agent being trained.
        """
        return [i + 1 for i,
                name in enumerate(self.game.players) if name is None][0]

    def _calculateSubReward(self, player: int) -> float:
        """
        Calculates the sub-rewards specified for the agents.
        That being any number of counters in the following range: 1 < x < winCondition.

        :param player: Integer player value for player whose reward is being calculated.
        :return: Float value for the sub-reward.
        """
        reward = 0
        for i in range(2, self.game.board.winCondition):
            reward += self.game.board.check_for_lines(
                player, i) * ((i ** 2) * 0.001)
        return reward

    def _trainingStep(self, action: int):
        """
        Function that allows the agent to undergo a step, and take a turn, during training.

        :param action: The action that the agent is taking.
        :return: Tuple containing the observation, reward, game-over flag, and info.
        """
        done = False
        reward = 0.0

        if self.game.board.get_col_counter(action) == self.game.board.rows:
            # Ends game if column full.
            reward = -10.0
            done = True

        if not done:
            # Agent being trained takes its turn.
            self.game.trainingAgentTurn(action, self.agentNum)
            # Checks if action caused game to end in a win for training agent.
            if self.game.board.check_for_lines(self.agentNum) > 0:
                reward += 10.0
                done = True
            else:
                # Calculates sub-reward if game not ended.
                reward += self._calculateSubReward(self.agentNum)

                # Opponent gets to take turn.
                self.game.opponentTurn(self.opponentNum)
                # Check if opponent's turn ended game.
                if self.game.board.check_for_lines(self.opponentNum) > 0:
                    reward = -10.0
                    done = True
                else:
                    # Calculate negative rewards.
                    reward -= self._calculateSubReward(self.opponentNum)

        # Create observation space and return relevant information.
        observation = self.game.board.get_observation()
        info = {}
        return observation, reward, done, info

    def step(self, action: int) -> tuple:
        """
        Take a step within the environment.

        :param action: The action that the agent is taking.
        :return: Tuple containing the observation, reward, game-over flag, and info.
        """
        if self.firstTurn and self.opponentNum == 1:
            # Check if first turn in the game is being played, and make the
            # opponent take a turn if they are player 1.
            self.game.opponentTurn(self.opponentNum)
            self.firstTurn = False

        return self._trainingStep(action)

    def reset(self) -> np.array:
        """
        Reset the board so the environment can be reused.

        :return observation: Return the observation of the reset board.
        """
        self.game.board.reset_board()
        self.firstTurn = True

        observation = self.game.board.get_observation()
        return observation  # reward, done, info can't be included

    def render(self, mode='human'):
        """
        Show the board during the game.

        :param mode: The type of render to display.
        """
        self.game.board.print_board(None)

    # def close (self):
