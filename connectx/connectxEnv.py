import gym
from gym import spaces
from game import *
from collections import deque


class ConnectXEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 # training: bool = False,
                 verbose: bool = False,
                 winCondition: int = 4,
                 boardRows: int = 6,
                 boardCols: int = 7,
                 player1: str or None = None,
                 player2: str or None = None):
        """
        This class is used to create a connect-x environment for the agents to use to train.
        
        :param training: 
        :param verbose: 
        :param winCondition: 
        :param boardRows: 
        :param boardCols: 
        :param player1: 
        :param player2: 
        """
        super(ConnectXEnv, self).__init__()
        # self.training = training
        self.game = TrainingGame(verbose=verbose,
                                 winCondition=winCondition,
                                 boardCols=boardCols,
                                 boardRows=boardRows,
                                 player1=player1,
                                 player2=player2)
        # if training else Game(verbose=verbose,
        #                                                             winCondition=winCondition,
        #                                                             boardCols=boardCols,
        #                                                             boardRows=boardRows,
        #                                                             player1=player1,
        #                                                             player2=player2)
        self.action_space = spaces.Discrete(self.game.board.cols)
        self.observation_space = spaces.Box(low=-1, high=self.game.board.rows, shape=(self.game.board.maxMoves + len(
            self.game.board.colCounters()),), dtype=np.float64)
        # self.prev_actions = None # Removed as it may not be adding much.
        self.observation = None
        self.reward = None
        self.done = False

    def calculateSubReward(self, player: int):
        reward = 0
        for i in range(2, self.game.board.winCondition):
            reward += self.game.board.checkXInARow(int(self.game.player(player) is None)+1, i) * (((i - 1) ** 2) * 0.005)
        return reward
        # threeInARow = self.game.board.checkXInARow(int(self.game.player(player) is None)+1, 3)
        # twoInARow = self.game.board.checkXInARow(int(self.game.player(player) is None)+1, 2)
        # return (threeInARow * 0.005) + (twoInARow * 0.001)

    def getPlayerVal(self, player: int):
        return int(self.game.player(player) is None)+1

    def trainingStep(self, action: int):
        """
        Should make it possible for the agent to go first too:
            Opponent takes turn (After THEN statements).

        Opponent takes turn.
        Use action to take turn.
        THEN
        Append action.
        Update observation.
        Check for sub-rewards and allocate.
        Check if done and allocate rewards.

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
            self.game.trainingAgentTurn(action, self.getPlayerVal(2))
            # # Action appended to list.
            # self.prev_actions.append(action)
            # Checks if action caused game to end in a win for training agent.
            if self.game.board.checkXInARow(self.getPlayerVal(2)) > 0:
                reward += 10.0
                done = True
            else:
                # Calculates sub-reward if game not ended.
                reward += self.calculateSubReward(2)
            # Opponent gets to take turn.
            self.game.opponentTurn(self.getPlayerVal(1))
            # Check if opponent's turn ended game.
            if self.game.board.checkXInARow(self.getPlayerVal(1)) > 0:
                reward = -10.0
                done = True

        # Create observation space and return relevant information.
        observation = self.game.board.getObservation()
        info = {}
        return observation, reward, done, info

    # def normalStep(self):
    #     done = False
    #     for player in [1, 2]:
    #         observation = self.calculateObservation()
    #         gameDone = self.game._turn(player, observation)
    #         if gameDone:
    #             return self.calculateObservation(), 0, gameDone, {}
    #     return self.calculateObservation(), 0, done, {}

    def step(self, action: int):
        """
        Take a step within the environment.

        :param action: The action that the player/agent is taking.
        """
        # if self.training:
        #     return self.trainingStep(action)
        # else:
        #     return self.normalStep()
        return self.trainingStep(action)

    def reset(self):
        """
        Reset the board so the environment can be reused.

        :return observation: Return the observation of the reset board.
        """
        self.game.board.resetBoard()

        # self.prev_actions = deque(maxlen=20)
        # for _ in range(20):
        #     self.prev_actions.append(-1)

        # Put this into step.
        if self.game.player(1) is not None:
            self.game.opponentTurn(self.getPlayerVal(1))

        observation = self.game.board.getObservation()
        return observation  # reward, done, info can't be included

    def render(self, mode='human'):
        """
        Show the board during the game.

        :param mode: The type of render to display.
        """
        self.game.board.printBoard()

    # def close (self):
