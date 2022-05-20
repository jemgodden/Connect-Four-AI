import argparse
from connectx import Learn

MODEL_TYPE = 'PPO'
MODEL_VERSION = 1
MODEL_FILE = None
MODEL_PLAYER = 1

OPPONENT_NAME = 'min'

ROWS = 6
COLS = 7
WIN_CONDITION = 4


if __name__ == '__main__':
    """
    Procedural file used to conduct bulk training of models.
    Can be configured from the command line. Use -h or --help to see the available arguments.

    Use command below in venv terminal to show model training logs:
    tensorboard --logdir=connectx/training-logs
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--modelType', type=str, nargs='?', default=MODEL_TYPE,
                        help='Policy gradient method used by the model being trained.')
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

    learn.train(25, 10000)
    learn.updateEnv(modelPlayer=2, opponentName='min')
    learn.train(25, 10000)

    learn.updateEnv(modelPlayer=1, opponentName='rand')
    learn.train(50, 10000)
    learn.updateEnv(modelPlayer=2, opponentName='rand')
    learn.train(50, 10000)

    learn.updateEnv(modelPlayer=1, opponentName='look')
    learn.train(100, 10000)
    learn.updateEnv(modelPlayer=2, opponentName='look')
    learn.train(100, 10000)

    # learn.updateEnv(modelPlayer=1, opponentName='models/PPO_6-7-4_v1.1/PPO_6-7-4_v1.1_1750000')
    # learn.train(200, 10000)
    # learn.updateEnv(modelPlayer=2, opponentName='models/PPO_6-7-4_v1.1/PPO_6-7-4_v1.1_1750000')
    # learn.train(200, 10000)
