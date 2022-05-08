import argparse
from core import Learn

MODEL_TYPE = 'PPO'
MODEL_VERSION = 0
MODEL_FILE = None
MODEL_PLAYER = 1

OPPONENT_NAME = 'rand'

ROWS = 6
COLS = 7
WIN_CONDITION = 4

"""
Use command below in venv terminal to show model training logs.

tensorboard --logdir=connectx/training-logs
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--modelType', type=str, nargs='?', default=MODEL_TYPE,
                        help='Policy used by model being trained.')
    parser.add_argument('-v', '--modelVersion', type=int, nargs='?', default=MODEL_VERSION,
                        help='Version of the model being trained.')
    parser.add_argument('-f', '--modelFile', type=str, nargs='?', default=MODEL_FILE,
                        help='File being used to load in the model being trained.')
    parser.add_argument('-p', '--modelPlayer', type=str, nargs='?', default=MODEL_PLAYER,
                        help='Which player the model being trained will be.')
    parser.add_argument('-', '--opponentName', type=str, nargs='?', default=OPPONENT_NAME,
                        help='Which opponent the model will train against.')
    parser.add_argument('-r', '--rows', type=int, nargs='?', default=ROWS,
                        help='Specify number of rows on board.')
    parser.add_argument('-c', '--columns', type=int, nargs='?', default=COLS,
                        help='Specify number of columns on board.')
    parser.add_argument('-w', '--winCondition', type=int, nargs='?', default=WIN_CONDITION,
                        help='Specify number of counters in a row needed to win.')
    args = parser.parse_args()

    subVersion = 1
    modelVersion = f"v{args.modelVersion}.{subVersion}"

    learn = Learn(modelType=args.modelType,
                  modelVersion=modelVersion,
                  modelFile=args.modelFile,
                  modelPlayer=args.modelPlayer,
                  opponentName=args.opponentName,
                  rows=args.rows,
                  cols=args.columns,
                  winCondition=args.winCondition)

    learn.train(5, 10000)
    learn.updateEnv(modelPlayer=2, opponentName=args.opponentName)
    learn.train(5, 10000)
