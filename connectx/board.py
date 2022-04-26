import warnings
import numpy as np


class Board(object):
    def __init__(self, rows: int = 6,
                 cols: int = 7,
                 winCondition: int = 4):
        """
        This class is used to create and update, during game play, a connect-x board.

        It is typically not used by itself, but instead called by Game class in game.py.

        :param rows: Int value for the number of rows the game board will have.
        :param cols: Int value for the number of columns the game board will have.
        :param winCondition: Int value for the number of counters in a row required to win.
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
    def cols(self):
        return self.__cols

    @property
    def rows(self):
        return self.__rows

    @property
    def winCondition(self):
        return self.__winCondition

    @property
    def maxMoves(self):
        return self.__maxMoves

    def boardArray(self):
        return self._boardArray

    def getBoardArray(self, i: int):
        return self._boardArray[i]

    def setBoardArray(self, i: int, val: int):
        self._boardArray[i] = val

    def colCounters(self):
        return self._colCounters

    def getColCounter(self, i: int):
        return self._colCounters[i]

    def updateColCounter(self, i: int, val: int):
        self._colCounters[i] += val

    def getObservation(self):
        return np.array(list(self.boardArray()) + list(self.colCounters()))

    def updateBoard(self, column: int, player: int):
        """
        Updates the board by placing a new counter in the player chosen column.
        :param column: Int value for column in which the new counter has been dropped.
        :param player: Int for player whose current go it is.
        """
        position = int(((self.rows - self.getColCounter(column) - 1) * self.cols) + column)
        # Numerical value of each counter corresponds to the player number. 0 if no counter present.
        self.setBoardArray(position, player)
        self.updateColCounter(column, 1)

    def _check(self, position: int, player: int, counter: int) -> int:
        """
        Checks counter in current position of board, during a dimensional check for win conditions, and updates
        information regarding the win condition.
        :param position: Int containing position of value currently being inspected.
        :param counter: An array of ints containing information on current line.
        :return counter: Updated values of counter variable.
        """
        pos = self.getBoardArray(position)
        if pos != 0 and pos == player:
            counter += 1
            return counter
        return 0

    def _checkHorizontals(self, player: int, inARow: int = None) -> int:
        """
        Checks all rows of the board to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        totalCount = 0
        for i in range(self.rows):
            # Counter used to keep track of which players counter was in the previous space (0th element) and how many
            # there have been in a row (1st element).
            counter = 0
            for j in range(self.cols):
                # position calculates the next space in the current row being investigated.
                position = (i * self.cols) + j
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1
        return totalCount

    def _checkVerticals(self, player: int, inARow: int = None) -> int:
        """
        Checks all columns of the board to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        totalCount = 0
        for i in range(self.cols):
            counter = 0
            for j in range(self.rows):
                position = (j * self.cols) + i
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1
        return totalCount

    def _checkDiagonalsRL(self, player: int, inARow: int = None) -> int:
        """
        Checks all possible diagonals, going from right to left, to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        totalCount = 0
        for i in range(self.cols - inARow, self.cols - 1):
            counter = 0
            for j in range(i + 1):
                position = (j * self.cols) + i - j
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1
        for m in range(self.rows - inARow + 1):
            counter = 0
            for n in range(self.rows - m):
                position = ((m + n + 1) * self.cols) - n - 1
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1
        return totalCount

    def _checkDiagonalsLR(self, player: int, inARow: int = None) -> int:
        """
        Checks all possible diagonals, going from left to right, to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        totalCount = 0
        for i in range(1, self.cols - inARow + 1):
            counter = 0
            for j in range(self.cols - i):
                position = (j * self.cols) + i + j
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1
        for m in range(self.rows - inARow + 1):
            counter = 0
            for n in range(self.rows - m):
                position = ((m + n) * self.cols) + n
                counter = self._check(position, player, counter)
                if counter == inARow:
                    totalCount += 1
        return totalCount

    def _checkDiagonals(self, player: int, inARow: int) -> int:
        """
        Checks both directions of diagonals to see whether the win condition has been met.
        :return gameOver: Bool indicating whether the win condition has been met.
        """
        return self._checkDiagonalsRL(player, inARow) + self._checkDiagonalsLR(player, inARow)

    def checkXInARow(self, player: int, inARow: int = None) -> int:
        """
        Checks entire board to see whether the win condition has been met.
        :return gameOver: Bool indicating whether the win condition has been met.
        """
        if inARow is None:
            inARow = self.__winCondition

        return self._checkHorizontals(player, inARow) + self._checkVerticals(player, inARow
                                                                             ) + self._checkDiagonals(player, inARow)

    def printBoard(self):
        """
        Prints the board to the console.
        """
        # Print numerical label for each column of board at the top of the board.
        for j in range(self.cols):
            print((j + 1), end=' ')
        print("\n")
        # Prints player 1 counters as 'o' and player 2 counters as 'x'.
        for i in range(self.maxMoves):
            if self.getBoardArray(i) == 1:
                print('o', end=' ')
            elif self.getBoardArray(i) == 2:
                print('x', end=' ')
            else:
                print('-', end=' ')
            if (i + 1) % self.cols == 0:
                print("\n", end='')

    def resetBoard(self):
        """
        Resets information given to the board in the last game.
        """
        self._boardArray = np.zeros(self.maxMoves)
        self._colCounters = np.zeros(self.cols)
