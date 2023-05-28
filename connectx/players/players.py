from abc import ABC
from connectx.game.board import Board


class Player(ABC):
    def __init__(self, player_num: int, board: Board):
        """
        Base class for all players.

        :param board: Reference to the game board.
        """
        self.player_num: int = player_num
        self.board: Board = board

    def perform_turn(self) -> int:
        """
        Outputs player's action each turn for the game object.

        :return: Integer value for column in which the counter will be dropped.
        """
        pass


class UserPlayer(Player):
    def _check_col_value(self, column: str) -> str or int:
        """
        Checks whether user column choice is possible.
        Forces user to re-enter column choice if not possible, until it is.

        :param column: Integer value for current players choice of column.
        :return column: Integer value of column if it is viable, else return string input by the user.
        """
        try:
            int(column)
        except ValueError:
            print("This is not a numerical input. Please try again.")
            return column

        arrCol = int(column) - 1

        if arrCol > (self.board.cols - 1) or arrCol < 0:
            print("This is not a valid column. Please try again.")
            return column

        if self.board.check_col_full(arrCol):
            print("This is column is full. Please try again.")
            return column

        return int(column)

    def perform_turn(self) -> int:
        """
        Function that allows a user player to take a turn.
        """
        column = None
        while not isinstance(column, int):
            # Reads in current players choice of column, checks whether it is possible, and executes it if so.
            # Forces user to re-enter column choice if not possible, until it is.
            column = input("Please choose a column to drop a counter in:\n")
            column = self._check_col_value(column)

        # Convert column choice to a value in the action space.
        action = column - 1
        return action
