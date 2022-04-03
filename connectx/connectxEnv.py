import gym
from gym import spaces
from game import *
from collections import deque


class ConnectXEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, opponent: str):
        """
        This class is used to create a connect-x environment for the agents to use to train.
        
        :param opponent: A string to specify which opponent the agent should train against.
        """
        super(ConnectXEnv, self).__init__()
        self.game = TrainingGame(player1=opponent)
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(self.game.board.cols)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=-1, high=self.game.board.rows, shape=(self.game.board.maxMoves + len(
            self.game.board.colCounters()) + 20,), dtype=np.float64)
        self.prev_actions = None
        self.observation = None
        self.reward = None
        self.done = False

    def step(self, action: int):
        """
        Take a step within the environment.

        :param action: The action that the player/agent is taking.

        Should make it possible for the agent to go first too:
                Use action to take turn.
            Opponent takes turn (After THEN statements).

        Opponent takes turn.
        Use action to take turn.
        THEN
        Append action.
        Update observation.
        Check for sub-rewards and allocate.
        Check if done and allocate rewards.
        """
        done = False
        reward = 0.0

        if self.game.board.getColCounter(action) == self.game.board.rows:
            reward = -10.0
            done = True

        if not done:
            self.game.trainingAgentTurn(action, int(self.game.player(2) is None)+1)

            self.prev_actions.append(action)
            if self.game.board.checkXInARow(int(self.game.player(2) is None)+1) > 0:
                reward += 10.0
                done = True
            else:
                threeInARow = self.game.board.checkXInARow(int(self.game.player(2) is None)+1, 3)
                twoInARow = self.game.board.checkXInARow(int(self.game.player(2) is None)+1, 2)
                if threeInARow > 0:
                    reward += threeInARow * 0.05
                elif twoInARow > 0:
                    reward += twoInARow * 0.01

            self.game.opponentTurn(int(self.game.player(1) is None)+1)
            if self.game.board.checkXInARow(int(self.game.player(1) is None)+1) > 0:
                reward = -10.0
                done = True

        observation = list(self.game.board.boardArray()) + list(self.game.board.colCounters()) + list(self.prev_actions)
        info = {}
        return np.array(observation), reward, done, info

    def reset(self):
        """
        Reset the board so the environment can be reused.

        :return observation: Return the observation of the reset board.
        """
        self.game.board.resetBoard()

        self.prev_actions = deque(maxlen=20)
        for _ in range(20):
            self.prev_actions.append(-1)

        if self.game.player(1) is not None:
            self.game.opponentTurn(int(self.game.player(1) is None)+1)

        observation = list(self.game.board.boardArray()) + list(self.game.board.colCounters()) + list(self.prev_actions)
        return np.array(observation)  # reward, done, info can't be included

    def render(self, mode='human'):
        """
        Show the board during the game.

        :param mode: The type of render to display.
        """
        self.game.board.printBoard()

    # def close (self):
