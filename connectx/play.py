import argparse
from game import *


if __name__ == '__main__':
    """
    This file is used to play an exhibition game of connect-x.
    
    It can take in a number of command line arguments that specify parameters of the board, game and players/opponents.
    Usage:
    '''sh
    python3 connectx/play.py -r 6 -c 7 -w 4 -p2 rand
    '''
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_false',
                        help='Specify whether information should not be printed to the console.')
    # Really need this? Doesn't make sense to let a game be played without verbose.
    parser.add_argument('-w', '--winCondition', type=int, nargs='?', default=4,
                        help='Specify number of counters in a row needed to win.')
    parser.add_argument('-r', '--rows', type=int, nargs='?', default=6,
                        help='Specify number of rows on board.')
    parser.add_argument('-c', '--columns', type=int, nargs='?', default=7,
                        help='Specify number of columns on board.')
    parser.add_argument('-p1', '--player1', type=str, nargs='?', default=None,
                        help='Specify player 1 as an agent or human.')
    parser.add_argument('-p2', '--player2', type=str, nargs='?', default=None,
                        help='Specify player 2 as an agent or human.')
    args = parser.parse_args()

    game = Game(verbose=args.verbose,
                winCondition=args.winCondition,
                boardRows=args.rows,
                boardCols=args.columns,
                player1=args.player1,
                player2=args.player2
                )
    game.play()
