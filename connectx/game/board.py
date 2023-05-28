import warnings
import logging
from colorama import Fore, Style
import numpy as np


class Board:
    def __init__(self, rows: int = 6, cols: int = 7, win_condition: int = 4):
        """
        This class is used to create and update the game board during a connect-x game.

        :param rows: Integer value for the number of rows the board will have.
        :param cols: Integer value for the number of columns the board will have.
        :param win_condition: Integer value for the number of counters in a row required to win.
        """
        if type(rows) is not int:
            raise TypeError("rows must be an integer.")
        if rows <= 0:
            raise ValueError("rows must be larger than 0.")
        self.__rows: int = rows

        if type(cols) is not int:
            raise TypeError("cols must be an integer.")
        if cols <= 0:
            raise ValueError("cols must be larger than 0.")
        self.__cols: int = cols

        if type(win_condition) is not int:
            raise TypeError("win_condition must be an integer.")
        if cols <= 0:
            raise ValueError("win_condition must be larger than 0.")
        self.__win_condition: int = win_condition

        if win_condition > (rows and cols):
            raise ValueError("The win condition cannot be larger than the number of rows and columns.")
        if rows > 20 or cols > 20:
            warnings.warn("The specified board size is quite large, consider making it smaller.")

        self.__max_moves: int = self.rows * self.cols
        self._board_array: np.ndarray = np.zeros(self.max_moves)
        # Top left position of board is represented by 0th element of 1d matrix.
        self._col_counters: np.ndarray = np.zeros(self.cols)

    @property
    def cols(self) -> int:
        return self.__cols

    @property
    def rows(self) -> int:
        return self.__rows

    @property
    def win_condition(self) -> int:
        return self.__win_condition

    @property
    def max_moves(self) -> int:
        return self.__max_moves

    def board_array(self) -> np.ndarray:
        return self._board_array

    def get_board_element(self, i: int) -> int:
        return self._board_array[i]

    def set_board_element(self, i: int, val: int):
        self._board_array[i] = val

    def col_counters(self) -> np.ndarray:
        return self._col_counters

    def get_col_counter(self, i: int) -> int:
        return self._col_counters[i]

    def check_col_full(self, i: int) -> bool:
        return self.get_col_counter(i) == self.rows

    def update_col_counter(self, i: int, val: int):
        self._col_counters[i] += val

    def get_observation(self) -> np.array:
        """
        Method used to return the observation of the game state for RL agents to use when training/playing.

        :return: Numpy array of the current board and column counters.
        """
        return np.array(list(self.board_array()) + list(self.col_counters()))

    def update_board(self, column: int, player: int):
        """
        Updates the board by placing a players counter in the specified column.

        :param column: Integer value for column in which the counter is being dropped.
        :param player: Integer value for player whose counter is being placed.
        """
        # Construct the position of the new counter for the 1D board array using column counters.
        position = int(((self.rows - self.get_col_counter(column) - 1) * self.cols) + column)

        self.set_board_element(position, player)
        self.update_col_counter(column, 1)

        logging.info(f"Player {player} put a counter in column {column + 1}.")

    def _check(self, position: int, player: int, running_total: int) -> int:
        """
        Checks if counter is present in specific board position and what player's it is.

        :param position: Integer corresponding to position currently being inspected.
        :param player: Integer value representing player whose counters are currently being checked.
        :param running_total: Integer for number of player's counters currently found in a row.
        :return: Updated value of runningTotal variable.
        """
        pos_counter = self.get_board_element(position)
        if pos_counter == player:
            return running_total + 1
        return 0

    def _checkHorizontals(self, player: int, line_len: int = None) -> int:
        """
        Checks all horizontal rows of the board to see how many times the specified number of counters in a row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param line_len: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        total_count = 0
        for i in range(self.rows):
            # counter represents a running total for number of counters in a row, for each row.
            counter = 0
            for j in range(self.cols):
                # position is constructed from iterators.
                position = (i * self.cols) + j
                counter = self._check(position, player, counter)
                if counter == line_len:
                    total_count += 1
        return total_count

    def _check_verticals(self, player: int, line_len: int = None) -> int:
        """
        Checks all vertical columns of the board to see how many times the specified number of counters in a row was
        met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param line_len: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        total_count = 0
        for i in range(self.cols):
            # counter represents a running total for number of counters in a
            # row, for each column.
            counter = 0
            for j in range(self.rows):
                # position is constructed from iterators.
                position = (j * self.cols) + i
                counter = self._check(position, player, counter)
                if counter == line_len:
                    total_count += 1
        return total_count

    def _check_diagonals_RL(self, player: int, line_len: int = None) -> int:
        """
        Checks all possible diagonals, going from right to left, to see how many times the specified number of counters
        in a row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param line_len: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        total_count = 0

        for i in range(self.cols - line_len, self.cols - 1):
            # Iterating along the base (columns) of the board, where diagonal is large enough for number of counters in
            # a row being looked for.
            counter = 0
            for j in range(i + 1):
                position = (j * self.cols) + i - j
                counter = self._check(position, player, counter)
                if counter == line_len:
                    total_count += 1

        for m in range(self.rows - line_len + 1):
            # Iterating along the sides of the board, where diagonal is large enough for number of counters in a row
            # being looked for.
            counter = 0
            for n in range(self.rows - m):
                position = ((m + n + 1) * self.cols) - n - 1
                counter = self._check(position, player, counter)
                if counter == line_len:
                    total_count += 1

        return total_count

    def _check_diagonals_LR(self, player: int, line_len: int = None) -> int:
        """
        Checks all possible diagonals, going from left to right, to see how many times the specified number of counters
        in a row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param line_len: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        total_count = 0

        for i in range(1, self.cols - line_len + 1):
            # Iterating along the base (columns) of the board, where diagonal is large enough for number of counters in
            # a row being looked for.
            counter = 0
            for j in range(self.cols - i):
                position = (j * self.cols) + i + j
                counter = self._check(position, player, counter)
                if counter == line_len:
                    total_count += 1

        for m in range(self.rows - line_len + 1):
            # Iterating along the sides of the board, where diagonal is large enough for number of counters in a row
            # being looked for.
            counter = 0
            for n in range(self.rows - m):
                position = ((m + n) * self.cols) + n
                counter = self._check(position, player, counter)
                if counter == line_len:
                    total_count += 1

        return total_count

    def _check_diagonals(self, player: int, line_len: int) -> int:
        """
        Checks all possible diagonals in both directions, to see how many times the specified number of counters in a
        row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param line_len: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        return self._check_diagonals_RL(player, line_len) + self._check_diagonals_LR(player, line_len)

    def check_for_lines(self, player: int, line_len: int = None) -> int:
        """
        Checks entire board to see how many times the specified number of counters in a row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param line_len: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        if line_len is None:
            # Default value for the number of counters in a row being looked for is the win condition.
            line_len = self.__win_condition

        num_lines_found = self._checkHorizontals(player, line_len) + self._check_verticals(
            player, line_len) + self._check_diagonals(player, line_len)

        logging.info(f"{num_lines_found} lines of {line_len} counters in a row found.")
        return num_lines_found

    def print_board(self, latest_move: int or None):
        """
        Prints a view of the current game board to the console.

        :param latest_move: Integer value indicating the last move made, so this can be indicated whilst printing to the
        console.
        """
        # Print numerical label for each column of board at the top of the board.
        for j in range(self.cols):
            print((j + 1), end=' ')

        if latest_move is None:
            print('\n')
        else:
            # If latest move is given, can print an arrow indicating in which column the latest counter was dropped.
            print('\n', end='')
            for k in range(self.cols):
                if k != latest_move:
                    print(' ', end=' ')
                else:
                    print('^', end=' ')
            print('\n', end='')

        # Prints player 1 counters as yellow 'o's and player 2 counters as red 'x's.
        # Empty positions are marked with a dash.
        for i in range(self.max_moves):
            if self.get_board_element(i) == 1:
                print(f"{Fore.YELLOW}o{Style.RESET_ALL}", end=' ')
            elif self.get_board_element(i) == 2:
                print(f"{Fore.RED}x{Style.RESET_ALL}", end=' ')
            else:
                print('-', end=' ')
            if (i + 1) % self.cols == 0:
                print("\n", end='')

    def reset_board(self):
        """
        Resets all information in the class relevant to a game, so that the board can be reused.
        """
        self._board_array = np.zeros(self.max_moves)
        self._col_counters = np.zeros(self.cols)
        logging.info(f"The board has been reset.")
