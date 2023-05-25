import os

from connectx.env.connectXEnv import ConnectXEnv
from stable_baselines3 import PPO, A2C


class Learn:
    MODELS_DIR = f"models/"
    LOGS_DIR = f"training-logs/"

    MODEL_TYPES = ['PPO', 'A2C']
    PLAYERS = [1, 2]

    def __init__(self,
                 modelType: str,
                 modelVersion: str,
                 modelFile: str or None = None,
                 modelPlayer: int = 1,
                 opponentName: str = 'rand',
                 rows: int = 6,
                 cols: int = 7,
                 winCondition: int = 4):
        """
        Class that helps to automate bulk training of the agent model.

        :param modelType: String indicating the policy gradient algorithm the agent will use.
        :param modelVersion: Integer value for the version of the model undergoing training.
        :param modelFile: String for filepath of the model being trained.
        :param modelPlayer: Integer player value for the agent being trained.
        :param opponentName: String indicating the opponent the agent is playing against.
        :param rows: Integer value for the number of rows the board will have.
        :param cols: Integer value for the number of columns the board will have.
        :param winCondition: Integer value for the number of counters in a row required to win.
        """

        if modelType not in self.MODEL_TYPES:
            raise ValueError(
                "Model policy specified is either invalid or not supported.")

        if modelPlayer not in self.PLAYERS:
            raise ValueError("Player must be either 1 or 2.")

        if not os.path.exists(self.MODELS_DIR):
            os.makedirs(self.MODELS_DIR)
        if not os.path.exists(self.LOGS_DIR):
            os.makedirs(self.LOGS_DIR)

        self._modelName = f"{modelType}_{rows}-{cols}-{winCondition}_{modelVersion}"
        self._modelPath = self.MODELS_DIR + f"{self._modelName}/"
        self._logsPath = self.LOGS_DIR

        self._env = self._initEnv(
            modelPlayer,
            opponentName,
            rows,
            cols,
            winCondition)
        self._model = self._initModel(modelType, modelFile)

    def _initModel(self, modelType: str, modelFile: str or None) -> PPO or A2C:
        """
        Function to initialise the model that is being trained.

        :param modelType: String indicating the policy gradient algorithm the agent will use.
        :param modelFile: String for filepath of the model being trained.
        :return: Model object that is going to be trained.
        """
        if modelType == 'PPO':
            if modelFile is None:
                # Create default model if no filepath given.
                return PPO('MlpPolicy', self._env, verbose=1,
                           tensorboard_log=self._logsPath)
            else:
                return PPO.load(self.MODELS_DIR + modelFile, self._env,
                                verbose=1, tensorboard_log=self._logsPath)

        if modelType == 'A2C':
            if modelFile is None:
                # Create default model if no filepath given.
                return A2C('MlpPolicy', self._env, verbose=1,
                           tensorboard_log=self._logsPath)
            else:
                return A2C.load(self.MODELS_DIR + modelFile, self._env,
                                verbose=1, tensorboard_log=self._logsPath)

    def updateModel(self, modelType: str, modelFile: str or None):
        """
        Function to update the model that is being trained.

        :param modelType: String indicating the policy gradient algorithm the agent will use.
        :param modelFile: String for filepath of the model being trained.
        :return: Model object that is going to be trained.
        """
        self._model = self._initModel(modelType, modelFile)
        print("\nModel updated.\n")

    @staticmethod
    def _initEnv(modelPlayer: int, opponentName: str,
                 rows: int = 6, cols: int = 7, winCondition: int = 4):
        """
        Function used to initialise the environment, and game, the model will use for training.

        :param modelPlayer: Integer player value for the agent being trained.
        :param opponentName: String indicating the opponent the agent is playing against.
        :param rows: Integer value for the number of rows the board will have.
        :param cols: Integer value for the number of columns the board will have.
        :param winCondition: Integer value for the number of counters in a row required to win.
        :return: Environment object for the Connect-X Environment being used to train the agent.
        """
        if modelPlayer == 1:
            return ConnectXEnv(rows=rows, cols=cols,
                               winCondition=winCondition, player2=opponentName)
        return ConnectXEnv(rows=rows, cols=cols,
                           winCondition=winCondition, player1=opponentName)

    def updateEnv(self, modelPlayer: int, opponentName: str,
                  rows: int = 6, cols: int = 7, winCondition: int = 4):
        """
        Function used to update the environment, and game, the model will use for training.
        Primarily used to change the opponent the agent will face.
        Typically, the rows, cols and winCondition should stay the same.

        :param modelPlayer: Integer player value for the agent being trained.
        :param opponentName: String indicating the opponent the agent is playing against.
        :param rows: Integer value for the number of rows the board will have.
        :param cols: Integer value for the number of columns the board will have.
        :param winCondition: Integer value for the number of counters in a row required to win.
        :return: Environment object for the Connect-X Environment being used to train the agent.
        """
        self._env = self._initEnv(
            modelPlayer,
            opponentName,
            rows,
            cols,
            winCondition)
        print("\nEnvironment updated.\n")

    def train(self, numIterations: int, numTimesteps: int, logIters: int = 5):
        """
        Function used to train the model over a specified number of iterations and timesteps.

        :param numIterations: Integer value for the number of iterations the agent should be trained for.
        :param numTimesteps: Integer value for the number of timesteps in each iteration.
        :param logIters: Integer value for the number of regular iterations at which the model should be exported to a
                         file.
        """
        curIteration = 0
        while curIteration < numIterations:
            curIteration += 1
            self._model.learn(
                total_timesteps=numTimesteps,
                reset_num_timesteps=False,
                tb_log_name=f"{self._modelName}")
            if curIteration % logIters == 0:
                self._model.save(
                    f"{self._modelPath}/{self._modelName}_{str(numTimesteps * curIteration)}")
