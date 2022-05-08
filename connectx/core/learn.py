import os
from .connectXEnv import ConnectXEnv
from stable_baselines3 import PPO, A2C


class Learn:
    MODELS_DIR = f"core/models/"
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

        if modelType not in self.MODEL_TYPES:
            raise ValueError("Model policy specified is either invalid or not supported.")

        if modelPlayer not in self.PLAYERS:
            raise ValueError("Player must be either 1 or 2.")

        if not os.path.exists(self.MODELS_DIR):
            os.makedirs(self.MODELS_DIR)
        if not os.path.exists(self.LOGS_DIR):
            os.makedirs(self.LOGS_DIR)

        self._modelName = f"{modelType}_{rows}-{cols}-{winCondition}_{modelVersion}"
        self._modelPath = self.MODELS_DIR + f"{self._modelName}/"
        self._logsPath = self.LOGS_DIR

        self._env = self._initEnv(modelPlayer, opponentName, rows, cols, winCondition)
        self._model = self._initModel(modelType, modelFile)

    def _initModel(self, modelType: str, modelFile: str or None):
        if modelType == 'PPO':
            if modelFile is None:
                return PPO('MlpPolicy', self._env, verbose=1, tensorboard_log=self._logsPath)
            else:
                return PPO.load(self.MODELS_DIR + modelFile, self._env, verbose=1, tensorboard_log=self._logsPath)
        if modelType == 'A2C':
            if modelFile is None:
                return A2C('MlpPolicy', self._env, verbose=1, tensorboard_log=self._logsPath)
            else:
                return A2C.load(self.MODELS_DIR + modelFile, self._env, verbose=1, tensorboard_log=self._logsPath)

    def updateModel(self, modelType: str, modelFile: str or None):
        self._model = self._initModel(modelType, modelFile)
        print("\nModel updated.\n")

    @staticmethod
    def _initEnv(modelPlayer: int, opponentName: str, rows: int = 6, cols: int = 7, winCondition: int = 4):
        if modelPlayer == 1:
            return ConnectXEnv(rows=rows, cols=cols, winCondition=winCondition, player2=opponentName)
        return ConnectXEnv(rows=rows, cols=cols, winCondition=winCondition, player1=opponentName)

    def updateEnv(self, modelPlayer: int, opponentName: str, rows: int = 6, cols: int = 7, winCondition: int = 4):
        self._env = self._initEnv(modelPlayer, opponentName, rows, cols, winCondition)
        print("\nEnvironment updated.\n")

    def train(self, numIterations: int, numTimesteps: int):
        iteration = 0
        while iteration < numIterations:
            iteration += 1
            self._model.learn(total_timesteps=numTimesteps, reset_num_timesteps=False, tb_log_name=f"{self._modelName}")
            self._model.save(f"{self._modelPath}/{self._modelName}_{str(numTimesteps * iteration)}")
