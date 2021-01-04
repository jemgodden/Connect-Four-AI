class Board:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.maxMoves = self.rows * self.cols
        self.boardArray = [0] * self.maxMoves
        self.colCounters = [0] * self.cols

    def updateBoard(self, column, player):
        arrCol = column - 1
        position = ((self.rows - self.colCounters[arrCol] - 1) * self.cols) + arrCol
        self.boardArray[position] = player
        self.colCounters[arrCol] += 1

    def printBoard(self):
        for j in range(self.cols):
            print((j + 1), end=' ')
        print("\n")

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
        self.board = Board(boardRows, boardCols)
        self.winCondition = winCondition

    def check(self, position, counter):
        if self.board.boardArray[position] != 0:
            if self.board.boardArray[position] == counter[0]:
                counter[1] += 1
                return counter
            else:
                return [self.board.boardArray[position], 1]
        else:
            return [0, 0]

    def checkHorizontals(self):
        for i in range(self.board.rows):
            counter = [0, 0]
            for j in range(self.board.cols):
                position = (i * self.board.cols) + j
                counter = self.check(position, counter)
                if counter[1] == self.winCondition:
                    return True
        return False

    def checkVerticals(self):
        for i in range(self.board.cols):
            counter = [0, 0]
            for j in range(self.board.rows):
                position = (j * self.board.cols) + i
                counter = self.check(position, counter)
                if counter[1] == self.winCondition:
                    return True
        return False

    def checkDiagonalsRL(self):
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

    def checkDiagonalsLR(self):
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

    def checkDiagonals(self):
        gameOver = self.checkDiagonalsRL()
        if gameOver:
            return gameOver
        gameOver = self.checkDiagonalsLR()
        return gameOver

    def checkWinConditions(self):
        gameOver = self.checkHorizontals()
        if gameOver:
            return gameOver
        gameOver = self.checkVerticals()
        if gameOver:
            return gameOver
        gameOver = self.checkDiagonals()
        return gameOver

    def checkColValue(self, column):
        try:
            int(column)
        except ValueError:
            print("This is not a valid column. Please try again.")
            return column

        arrCol = int(column) - 1
        if arrCol > 6 or arrCol < 0:
            print("This is not a valid column. Please try again.")
            return column
        if self.board.colCounters[arrCol] == self.board.rows:
            print("This column is already full. Please try again.")
            return column

        return int(column)

    def takeTurn(self, player):
        column = None
        while type(column) is not int:
            column = input("\nPlayer {}, please choose a column to drop a counter in:\n".format(player))
            column = self.checkColValue(column)

        self.board.updateBoard(column, player)
        self.board.printBoard()
        return self.checkWinConditions()

    def allTurns(self):
        gameOver = False
        self.board.printBoard()
        for i in range(self.board.maxMoves):
            player = (i % 2) + 1
            gameOver = self.takeTurn(player)
            if gameOver:
                print("\nPlayer {} wins!".format(player))
                break

        if not gameOver:
            print("\nIt was a draw!")


if __name__ == '__main__':
    game = Game()
    game.allTurns()

# TODO: Do comments.
