import warnings
from colorama import Fore, Style
import numpy as np


class Board:
    def __init__(self, rows: int = 6,
                 cols: int = 7,
                 winCondition: int = 4):
        """
        This class is used to create and update the game board during a connect-x game.

        :param rows: Integer value for the number of rows the board will have.
        :param cols: Integer value for the number of columns the board will have.
        :param winCondition: Integer value for the number of counters in a row required to win.
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

        if type(winCondition) is not int:
            raise TypeError("winCondition must be an integer.")
        if cols <= 0:
            raise ValueError("winCondition must be larger than 0.")
        self.__winCondition: int = winCondition

        if winCondition > (rows and cols):
            raise ValueError("The win condition cannot be larger than the number of rows and columns.")
        if rows > 20 or cols > 20:
            warnings.warn("The specified board size is quite large, consider making it smaller.")

        self.__maxMoves: int = self.rows * self.cols
        self._boardArray: np.ndarray = np.zeros(self.maxMoves)
        # Top left position of board is represented by 0th element of 1d matrix.
        self._colCounters: np.ndarray = np.zeros(self.cols)

    @property
    def cols(self) -> int:
        return self.__cols

    @property
    def rows(self) -> int:
        return self.__rows

    @property
    def winCondition(self) -> int:
        return self.__winCondition

    @property
    def maxMoves(self) -> int:
        return self.__maxMoves

    def boardArray(self) -> np.ndarray:
        return self._boardArray

    def getBoardArrayElement(self, i: int) -> int:
        return self._boardArray[i]

    def setBoardArrayElement(self, i: int, val: int):
        self._boardArray[i] = val

    def colCounters(self) -> np.ndarray:
        return self._colCounters

    def getColCounter(self, i: int) -> int:
        return self._colCounters[i]

    def fullColCounter(self, i: int) -> bool:
        return self.getColCounter(i) == self.rows

    def updateColCounter(self, i: int, val: int):
        self._colCounters[i] += val

    def getObservation(self) -> np.array:
        """
        Method used to return the observation of the game state for RL agents to use when training/playing.

        :return: Numpy array of the current board and column counters.
        """
        return np.array(list(self.boardArray()) + list(self.colCounters()))

    def updateBoard(self, column: int, player: int):
        """
        Updates the board by placing a players counter in the specified column.

        :param column: Integer value for column in which the counter is being dropped.
        :param player: Integer value for player whose counter is being placed.
        """
        # Construct the position of the new counter for the 1D board array using column counters.
        position = int(((self.rows - self.getColCounter(column) - 1) * self.cols) + column)

        self.setBoardArrayElement(position, player)
        self.updateColCounter(column, 1)

    def _check(self, position: int, player: int, runningTotal: int) -> int:
        """
        Checks if counter is present in specific board position and what player's it is.

        :param position: Integer corresponding to position currently being inspected.
        :param player: Integer value representing player whose counters are currently being checked.
        :param runningTotal: Integer for number of player's counters currently found in a row.
        :return: Updated value of runningTotal variable.
        """
        posCounter = self.getBoardArrayElement(position)
        if posCounter == player:
            return runningTotal + 1
        return 0

    def _checkHorizontals(self, player: int, inARow: int = None) -> int:
        """
        Checks all horizontal rows of the board to see how many times the specified number of counters in a row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param inARow: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        totalCount = 0
        for i in range(self.rows):
            # counter represents a running total for number of counters in a row, for each row.
            counter = 0
            for j in range(self.cols):
                # position is constructed from iterators.
                position = (i * self.cols) + j
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1
        return totalCount

    def _checkVerticals(self, player: int, inARow: int = None) -> int:
        """
        Checks all vertical columns of the board to see how many times the specified number of counters in a row was
        met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param inARow: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        totalCount = 0
        for i in range(self.cols):
            # counter represents a running total for number of counters in a row, for each column.
            counter = 0
            for j in range(self.rows):
                # position is constructed from iterators.
                position = (j * self.cols) + i
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1
        return totalCount

    def _checkDiagonalsRL(self, player: int, inARow: int = None) -> int:
        """
        Checks all possible diagonals, going from right to left, to see how many times the specified number of counters
        in a row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param inARow: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        totalCount = 0

        for i in range(self.cols - inARow, self.cols - 1):
            # Iterating along the base (columns) of the board, where diagonal is large enough for number of counters in
            # a row being looked for.
            counter = 0
            for j in range(i + 1):
                position = (j * self.cols) + i - j
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1

        for m in range(self.rows - inARow + 1):
            # Iterating along the sides of the board, where diagonal is large enough for number of counters in a row
            # being looked for.
            counter = 0
            for n in range(self.rows - m):
                position = ((m + n + 1) * self.cols) - n - 1
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1

        return totalCount

    def _checkDiagonalsLR(self, player: int, inARow: int = None) -> int:
        """
        Checks all possible diagonals, going from left to right, to see how many times the specified number of counters
        in a row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param inARow: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        totalCount = 0

        for i in range(1, self.cols - inARow + 1):
            # Iterating along the base (columns) of the board, where diagonal is large enough for number of counters in
            # a row being looked for.
            counter = 0
            for j in range(self.cols - i):
                position = (j * self.cols) + i + j
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1

        for m in range(self.rows - inARow + 1):
            # Iterating along the sides of the board, where diagonal is large enough for number of counters in a row
            # being looked for.
            counter = 0
            for n in range(self.rows - m):
                position = ((m + n) * self.cols) + n
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1

        return totalCount

    def _checkDiagonals(self, player: int, inARow: int) -> int:
        """
        Checks all possible diagonals in both directions, to see how many times the specified number of counters in a
        row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param inARow: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        return self._checkDiagonalsRL(player, inARow) + self._checkDiagonalsLR(player, inARow)

    def checkXInARow(self, player: int, inARow: int = None) -> int:
        """
        Checks entire board to see how many times the specified number of counters in a row was met.

        :param player: Integer value representing player whose counters are currently being checked.
        :param inARow: Integer for the number of counters in a row being looked for.
        :return: Integer for how many times the specified number of counters in a row were found.
        """
        if inARow is None:
            # Default value for the number of counters in a row being looked for is the win condition.
            inARow = self.__winCondition

        return self._checkHorizontals(player, inARow) + self._checkVerticals(player, inARow
                                                                             ) + self._checkDiagonals(player, inARow)

    def printBoard(self, latestMove: int or None):
        """
        Prints a view of the current game board to the console.

        :param latestMove: Integer value indicating the last move made, so this can be indicated whilst printing to the
        console.
        """
        # Print numerical label for each column of board at the top of the board.
        for j in range(self.cols):
            print((j + 1), end=' ')

        if latestMove is None:
            print('\n')
        else:
            # If latest move is given, can print an arrow indicating in which column the latest counter was dropped.
            print('\n', end='')
            for k in range(self.cols):
                if k != latestMove:
                    print(' ', end=' ')
                else:
                    print('^', end=' ')
            print('\n', end='')

        # Prints player 1 counters as yellow 'o's and player 2 counters as red 'x's.
        # Empty positions are marked with a dash.
        for i in range(self.maxMoves):
            if self.getBoardArrayElement(i) == 1:
                print(f"{Fore.YELLOW}o{Style.RESET_ALL}", end=' ')
            elif self.getBoardArrayElement(i) == 2:
                print(f"{Fore.RED}x{Style.RESET_ALL}", end=' ')
            else:
                print('-', end=' ')
            if (i + 1) % self.cols == 0:
                print("\n", end='')

    def resetBoard(self):
        """
        Resets all information in the class relevant to a game, so that the board can be reused.
        """
        self._boardArray = np.zeros(self.maxMoves)
        self._colCounters = np.zeros(self.cols)
