import time
from board import *
from agents import *


class Game:
    def __init__(self, winCondition: int = 4, boardRows=6, boardCols=7):
        """
        :param winCondition: Int value for the required number of counters in a row in order to win the game.
        :param boardRows: Int value for the number of rows the game board will have.
        :param boardCols: Int value for the number of columns the game board will have.
        """
        self.board = Board(boardRows, boardCols)
        self.winCondition = winCondition

    def __checkColValue(self, column: int) -> int:
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

        return int(column)

    def __playerTurn(self, player):
        """
        Reads in current players choice of column, checks whether it is possible, and executes it.
        :param player: Int value representing which players go it is.
        :return: Bool indicating whether the win condition has been met.
        """
        column = None
        while type(column) is not int:
            column = input("\nPlayer {}, please choose a column to drop a counter in:\n".format(player))
            column = self.__checkColValue(column)

        if self.board.colCounters[column-1] == self.board.rows:
            return True, True

        self.board.updateBoard(column, player)
        self.board.printBoard()
        return self.board.checkWinConditions(self.winCondition), False

    def __aiTurn(self, player_val):
        print("\nAI choosing a move...\n")
        time.sleep(0.5)
        column = random_agent(self.board)
        self.board.updateBoard(column, player_val)
        self.board.printBoard()
        return self.board.checkWinConditions(self.winCondition), False

    def allTurns(self, ai):
        """
        Iterate over all possible turns in the game, resulting in a draw if no win condition is ever met.
        """
        self.board.printBoard()
        for i in range(self.board.maxMoves):
            player = (i % 2) + 1
            if ai and player == 2:
                gameOver, invalidRow = self.__aiTurn(player)
            else:
                gameOver, invalidRow = self.__playerTurn(player)
            if gameOver:
                return gameOver, invalidRow, player

    def exhibitionGame(self, ai=False):
        done = False
        while not done:
            gameOver, invalidRow, player = self.allTurns(ai)

            if gameOver:
                if invalidRow:
                    print("Player {} selected an invalid column.".format(player))
                    print("Player {} wins!".format((player % 2) + 1))
                else:
                    print("\nPlayer {} wins!".format(player))
            else:
                print("\nIt was a draw!")

            done = input("\nPlay again? (Y/N):\n") != 'Y'
            if not done:
                self.board.resetBoard()


if __name__ == '__main__':
    game = Game()
    game.exhibitionGame(ai=True)

# TODO: Sort more effective way of restarting game.
# TODO: Clean up of playing AI.
