"""
This file contains the code to model the playing board and play one full game of Connect Four.
"""

# TODO: Move checking functions from game to board. Can pass the winCondition value into Board functions to check.
# TODO: Make new files for each class.


class Board:
    def __init__(self, rows=6, cols=7):
        """
        :param rows: Int value for the number of rows the game board will have.
        :param cols: Int value for the number of columns the game board will have.
        """
        self.rows = rows
        self.cols = cols
        self.maxMoves = self.rows * self.cols
        self.boardArray = [0] * self.maxMoves
        # Top left position of board is represented by 0th element of 1d matrix.
        self.colCounters = [0] * self.cols

    def updateBoard(self, column, player):
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


class Game:
    def __init__(self, winCondition=4, boardRows=6, boardCols=7):
        """
        :param winCondition: Int value for the required number of counters in a row in order to win the game.
        :param boardRows: Int value for the number of rows the game board will have.
        :param boardCols: Int value for the number of columns the game board will have.
        """
        self.board = Board(boardRows, boardCols)
        self.winCondition = winCondition
        # TODO: Move counter variables to their own object variables?

    def __check(self, position, counter):
        """
        Checks counter in current position of board, during a dimensional check for win conditions, and updates
        information regarding the win condition.
        :param position: Int containing position of value currently being inspected.
        :param counter: An array of ints containing information on current line.
        :return counter: Updated values of counter variable.
        """
        if self.board.boardArray[position] != 0:
            if self.board.boardArray[position] == counter[0]:
                counter[1] += 1
                return counter
            else:
                return [self.board.boardArray[position], 1]
        else:
            return [0, 0]

    def __checkHorizontals(self):
        """
        Checks all rows of the board to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        for i in range(self.board.rows):
            # Counter used to keep track of which players counter was in the previous space (0th element) and how many
            # there have been in a row (1st element).
            counter = [0, 0]
            for j in range(self.board.cols):
                # position calculates the next space in the current row being investigated.
                position = (i * self.board.cols) + j
                counter = self.__check(position, counter)
                if counter[1] == self.winCondition:
                    return True
        return False

    def __checkVerticals(self):
        """
        Checks all columns of the board to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        for i in range(self.board.cols):
            counter = [0, 0]
            for j in range(self.board.rows):
                position = (j * self.board.cols) + i
                counter = self.check(position, counter)
                if counter[1] == self.winCondition:
                    return True
        return False

    def __checkDiagonalsRL(self):
        """
        Checks all possible diagonals, going from right to left, to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        for i in range(self.board.cols - self.winCondition, self.board.cols - 1):
            counter = [0, 0]
            for j in range(i + 1):
                position = (j * self.board.cols) + i - j
                counter = self.check(position, counter)
                if counter[1] == self.winCondition:
                    return True

        for m in range(self.board.rows - self.winCondition + 1):
            counter = [0, 0]
            for n in range(self.board.rows - m):
                position = ((m + n + 1) * self.board.cols) - n - 1
                counter = self.check(position, counter)
                if counter[1] == self.winCondition:
                    return True

        return False

    def __checkDiagonalsLR(self):
        """
        Checks all possible diagonals, going from left to right, to see if the win condition has been met.
        :return: Bool indicating whether the win condition has been met.
        """
        for i in range(1, self.board.cols - self.winCondition + 1):
            counter = [0, 0]
            for j in range(self.board.cols - i):
                position = (j * self.board.cols) + i + j
                counter = self.check(position, counter)
                if counter[1] == self.winCondition:
                    return True

        for m in range(self.board.rows - self.winCondition + 1):
            counter = [0, 0]
            for n in range(self.board.rows - m):
                position = ((m + n) * self.board.cols) + n
                counter = self.check(position, counter)
                if counter[1] == self.winCondition:
                    return True

        return False

    def __checkDiagonals(self):
        """
        Checks both directions of diagonals to see whether the win condition has been met.
        :return gameOver: Bool indicating whether the win condition has been met.
        """
        gameOver = self.__checkDiagonalsRL()
        if gameOver:
            return gameOver
        gameOver = self.__checkDiagonalsLR()
        return gameOver

    def checkWinConditions(self):
        """
        Checks entire board to see whether the win condition has been met.
        :return gameOver: Bool indicating whether the win condition has been met.
        """
        gameOver = self.__checkHorizontals()
        if gameOver:
            return gameOver
        gameOver = self.__checkVerticals()
        if gameOver:
            return gameOver
        gameOver = self.__checkDiagonals()
        return gameOver

    def __checkColValue(self, column):
        """
        Checks whether current column choice is possible.
        :param column: Int value for current players choice of column.
        :return column: Returns integer value of column if it is viable, else returns str input by the user.
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
        if self.board.colCounters[arrCol] == self.board.rows:
            print("This column is already full. Please try again.")
            return column

        return int(column)

    def __takeTurn(self, player):
        """
        Reads in current players choice of column, checks whether it is possible, and executes it.
        :param player: Int value representing which players go it is.
        :return: Bool indicating whether the win condition has been met.
        """
        column = None
        while type(column) is not int:
            column = input("\nPlayer {}, please choose a column to drop a counter in:\n".format(player))
            column = self.__checkColValue(column)

        self.board.updateBoard(column, player)
        self.board.printBoard()
        return self.checkWinConditions()

    def allTurns(self):
        """
        Iterate over all possible turns in the game, resulting in a draw if no win condition is ever met.
        """
        gameOver = False
        self.board.printBoard()
        for i in range(self.board.maxMoves):
            player = (i % 2) + 1
            gameOver = self.__takeTurn(player)
            if gameOver:
                print("\nPlayer {} wins!".format(player))
                break

        if not gameOver:
            print("\nIt was a draw!")


if __name__ == '__main__':
    game = Game()
    game.allTurns()
