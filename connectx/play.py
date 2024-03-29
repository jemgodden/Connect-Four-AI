import os
from datetime import datetime
import logging
import argparse
from connectx import Game


if __name__ == '__main__':
    """
    This file is used to play an exhibition game of Connect-X.
    Command line arguments can be used to configure the game, specifying parameters of the board, game and players.
    Use command -h or --help to see available arguments.

    Usage:
    '''sh
    python3 play.py -p1 rand -p2 connectx/core/models/PPO_6-7-4_v0.1/PPO_6-7-4_v0.1_50000
    '''
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--win_condition', type=int, nargs='?', default=4,
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

    logs_path = "logs/play"
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    logging.basicConfig(
        filename=f"{logs_path}/session_{datetime.now().strftime('%d-%m-%Y_%H:%M:%S')}.log",
        format='%(asctime)s %(message)s',
        filemode='w',
        level=logging.INFO
    )
    logger = logging.getLogger("playLogger")

    game = Game(
        win_condition=args.win_condition,
        board_rows=args.rows,
        board_cols=args.columns,
        player1=args.player1,
        player2=args.player2
    )
    game.play()
