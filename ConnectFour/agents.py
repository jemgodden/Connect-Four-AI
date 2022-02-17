import random
# from stable_baseline import PPO2


def random_agent(board) -> int:
    return random.choice([i + 1 for i in range(board.cols) if board.colCounters != board.rows])
