import os
from .connectXEnv import ConnectXEnv
from stable_baselines3 import PPO


class Learn:
    MODELS_DIR = f"ConnectFour/connectx/models/"
    LOGS_DIR = f"ConnectFour/training-logs/"

    def __init__(self,
                 modelType: str,
                 modelVersion: str,
                 modelFile: str or None = None,
                 rows: int = 6,
                 cols: int = 7,
                 winCondition: int = 4):

        if not os.path.exists(self.MODELS_DIR):
            os.makedirs(self.MODELS_DIR)
        if not os.path.exists(self.LOGS_DIR):
            os.makedirs(self.LOGS_DIR)

        self.modelName = modelType + modelVersion
        self.modelPath = self.MODELS_DIR + f"{self.modelName}/"
        self.logsPath = self.LOGS_DIR

        self.model = self.initModel(modelType, modelFile)
        self.env = self.initEnv(modelPlayer, opponentName, rows, cols, winCondition)

    def initModel(self, modelType: str, modelFile: str):
        if modelType == 'PPO':
            if modelFile is None:
                return PPO('MlpPolicy', self.env, verbose=1, tensorboard_log=self.logsPath)
            else:
                return PPO.load(self.MODELS_DIR + modelFile, self.env, verbose=1, tensorboard_log=self.logsPath)

    @staticmethod
    def initEnv(modelPlayer: int, opponentName: str, rows: int, cols: int, winCondition: int):
        if modelPlayer == 1:
            return ConnectXEnv(rows=rows, cols=cols, winCondition=winCondition, player2=opponentName)
        return ConnectXEnv(rows=rows, cols=cols, winCondition=winCondition, player1=opponentName)

    def train(self, numIterations: int, numTimesteps: int, modelPlayer: int = 1, opponentName: str = 'rand'):
        env = self.initEnv(modelPlayer, opponentName,)

        iteration = 0
        while iteration < numIterations:
            iteration += 1
            self.model.learn(total_timesteps=numTimesteps, reset_num_timesteps=False, tb_log_name=f"{self.modelName}")
            self.model.save(f"{self.modelPath}/{self.modelName}_{str(numTimesteps*iteration)}")
