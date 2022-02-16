import random
# from stable_baseline import PPO2


def random_agent(board):
    return random.choice([i for i in range(board.cols) if board.colCounters != board.rows])
