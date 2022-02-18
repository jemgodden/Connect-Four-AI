class Board:
    def __init__(self, rows: int = 6, cols: int = 7):
        """
        :param rows: Int value for the number of rows the game board will have.
        :param cols: Int value for the number of columns the game board will have.
        """
        self.rows: int = rows
        self.cols: int = cols
        self.maxMoves: int = self.rows * self.cols
        self.boardArray: list[int] = [0] * self.maxMoves
        # Top left position of board is represented by 0th element of 1d matrix.
        self.colCounters: list[int] = [0] * self.cols

    def updateBoard(self, column: int, player: int):
        """
        Updates the board by placing a new counter in the player chosen column.
        :param column: Int value for column in which the new counter has been dropped.
        :param player: Int for player whose current go it is.
        """
        arrCol = column - 1
        position = ((self.rows - self.colCounters[arrCol] - 1) * self.cols) + arrCol
        # Numerical value of each counter corresponds to the player number. 0 if no counter present.
        self.boardArray[position] = player
        self.colCounters[arrCol] += 1

    def __check(self, position: int, counter: list[int]) -> list[int]:
        """
        Checks counter in current position of board, during a dimensional check for win conditions, and updates
        information regarding the win condition.
        :param position: Int containing position of value currently being inspected.
        :param counter: An array of ints containing information on current line.
        :return counter: Updated values of counter variable.
        """
        if self.boardArray[position] != 0:
            if self.boardArray[position] == counter[0]:
                counter[1] += 1
                return counter
            else:
                return [self.boardArray[position], 1]
        else:
            return [0, 0]

    def __checkHorizontals(self, winCondition: int) -> bool:
        """
        Checks all rows of the board to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        for i in range(self.rows):
            # Counter used to keep track of which players counter was in the previous space (0th element) and how many
            # there have been in a row (1st element).
            counter = [0, 0]
            for j in range(self.cols):
                # position calculates the next space in the current row being investigated.
                position = (i * self.cols) + j
                counter = self.__check(position, counter)
                if counter[1] == winCondition:
                    return True
        return False

    def __checkVerticals(self, winCondition: int) -> bool:
        """
        Checks all columns of the board to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        for i in range(self.cols):
            counter = [0, 0]
            for j in range(self.rows):
                position = (j * self.cols) + i
                counter = self.__check(position, counter)
                if counter[1] == winCondition:
                    return True
        return False

    def __checkDiagonalsRL(self, winCondition: int) -> bool:
        """
        Checks all possible diagonals, going from right to left, to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        for i in range(self.cols - winCondition, self.cols - 1):
            counter = [0, 0]
            for j in range(i + 1):
                position = (j * self.cols) + i - j
                counter = self.__check(position, counter)
                if counter[1] == winCondition:
                    return True
        for m in range(self.rows - winCondition + 1):
            counter = [0, 0]
            for n in range(self.rows - m):
                position = ((m + n + 1) * self.cols) - n - 1
                counter = self.__check(position, counter)
                if counter[1] == winCondition:
                    return True
        return False

    def __checkDiagonalsLR(self, winCondition: int) -> bool:
        """
        Checks all possible diagonals, going from left to right, to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        for i in range(1, self.cols - winCondition + 1):
            counter = [0, 0]
            for j in range(self.cols - i):
                position = (j * self.cols) + i + j
                counter = self.__check(position, counter)
                if counter[1] == winCondition:
                    return True
        for m in range(self.rows - winCondition + 1):
            counter = [0, 0]
            for n in range(self.rows - m):
                position = ((m + n) * self.cols) + n
                counter = self.__check(position, counter)
                if counter[1] == winCondition:
                    return True
        return False

    def __checkDiagonals(self, winCondition: int) -> bool:
        """
        Checks both directions of diagonals to see whether the win condition has been met.
        :return gameOver: Bool indicating whether the win condition has been met.
        """
        gameOver = self.__checkDiagonalsRL(winCondition)
        if gameOver:
            return gameOver
        gameOver = self.__checkDiagonalsLR(winCondition)
        return gameOver

    def checkWinConditions(self, winCondition: int) -> bool:
        """
        Checks entire board to see whether the win condition has been met.
        :return gameOver: Bool indicating whether the win condition has been met.
        """
        gameOver = self.__checkHorizontals(winCondition)
        if gameOver:
            return gameOver
        gameOver = self.__checkVerticals(winCondition)
        if gameOver:
            return gameOver
        gameOver = self.__checkDiagonals(winCondition)
        return gameOver

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
            if self.boardArray[i] == 1:
                print('o', end=' ')
            elif self.boardArray[i] == 2:
                print('x', end=' ')
            else:
                print('-', end=' ')
            if (i + 1) % self.cols == 0:
                print("\n", end='')

    def resetBoard(self):
        """
        Resets information given to the board in the last game.
        """
        self.boardArray = [0] * self.maxMoves
        self.colCounters = [0] * self.cols
