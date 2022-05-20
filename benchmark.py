import argparse
from connectx import Game


if __name__ == '__main__':
    """
    This file is used to benchmark an agent against another agent.
    Command line arguments can be used to configure the benchmarking, specifying parameters of the board, game and 
    players.
    Use command -h or --help to see available arguments.

    Usage:
    '''sh
    python3 play.py -g 100 -a connectx/models/PPO_6-7-4_v0.1/PPO_6-7-4_v0.1_50000
    '''
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--games', type=int, nargs='?', default=20,
                        help='Number of games to be played between the agents in each player position.')
    parser.add_argument('-w', '--winCondition', type=int, nargs='?', default=4,
                        help='Specify number of counters in a row needed to win.')
    parser.add_argument('-r', '--rows', type=int, nargs='?', default=6,
                        help='Specify number of rows on board.')
    parser.add_argument('-c', '--columns', type=int, nargs='?', default=7,
                        help='Specify number of columns on board.')
    parser.add_argument('-a', '--agent', type=str, nargs='?', default='look3',
                        help='The agent being tested.')
    parser.add_argument('-b', '--benchmarkAgent', type=str, nargs='?', default='look3',
                        help='The agent being benchmarked against.')
    args = parser.parse_args()

    outcomes = {
        "win": 0,
        "draw": 0,
        "loss": 0
    }

    print(f"Agent being benchmarked: {args.agent}")
    print(f"Benchmark agent: {args.benchmarkAgent}\n\n")

    game1 = Game(
        verbose=False,
        winCondition=args.winCondition,
        boardRows=args.rows,
        boardCols=args.columns,
        player1=args.agent,
        player2=args.benchmarkAgent
    )
    print("Running games as player 1...")
    for _ in range(args.games):
        result = game1.allTurns()
        if result == 1:
            outcomes["win"] += 1
        elif result == 2:
            outcomes["loss"] += 1
        else:
            outcomes["draw"] += 1
        game1.board.resetBoard()
    print("Player 1 games complete.\n")
    print(f"Agent record as player 1: {outcomes['win']} Wins, {outcomes['draw']} Draws, {outcomes['loss']} Losses\n")

    game2 = Game(
        verbose=False,
        winCondition=args.winCondition,
        boardRows=args.rows,
        boardCols=args.columns,
        player1=args.benchmarkAgent,
        player2=args.agent
    )
    print("Running games as player 2...")
    for _ in range(args.games):
        result = game2.allTurns()
        if result == 2:
            outcomes["win"] += 1
        elif result == 1:
            outcomes["loss"] += 1
        else:
            outcomes["draw"] += 1
        game2.board.resetBoard()
    print("Player 2 games complete.\n")

    print(f"Agent overall win percentage: {(outcomes['win']/(2 * args.games)) * 100}%")
    print(f"Agent overall record: {outcomes['win']} Wins, {outcomes['draw']} Draws, {outcomes['loss']} Losses")
