import time
from board import *
from agents import *


class Game:
    def __init__(self, winCondition: int = 4, boardRows: int = 6, boardCols: int = 7, agent: str = None):
        """
        :param winCondition: Int value for the required number of counters in a row in order to win the game.
        :param boardRows: Int value for the number of rows the game board will have.
        :param boardCols: Int value for the number of columns the game board will have.
        :param agent: String that specifies agent to play against.
        """
        self.board: Board = Board(boardRows, boardCols)
        self.winCondition: int = winCondition
        self.agent: Agent = self.__initialiseAgent(agent)

    def __initialiseAgent(self, agent: str):
        """
        Initialises an agent to play against.
        :param agent: String that specifies agent to play against.
        :return: Agent class for chosen opponent agent.
        """
        if agent is None:
            return None
        elif str.lower(agent) == 'rand':
            return RandomAgent(self.board)
        else:
            return None

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

    def __playerTurn(self, player: int) -> tuple[bool, bool]:
        """
        Reads in current players choice of column, checks whether it is possible, and executes it.
        :param player: Int value representing which player's go it is.
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

    def __agentTurn(self, player: int) -> tuple[bool, bool]:
        """
        Opponent agent takes their go.
        :param player: Int value representing which player's go it is.
        :return: Bool indicating whether the win condition has been met.
        """
        print("\nAI choosing a move...\n")
        time.sleep(1)
        column = self.agent.__performTurn()
        self.board.updateBoard(column, player)
        self.board.printBoard()
        return self.board.checkWinConditions(self.winCondition), False

    def allTurns(self) -> tuple[bool, bool, int]:
        """
        Iterate over all possible turns in the game, resulting in a draw if no win condition is ever met.
        :return: Bool indicating whether the win condition has been met.
        :return player: Int value representing which player won.
        """
        self.board.printBoard()
        for i in range(self.board.maxMoves):
            player = (i % 2) + 1
            if (self.agent is not None) and (player == 2):
                gameOver, invalidRow = self.__agentTurn(player)
            else:
                gameOver, invalidRow = self.__playerTurn(player)
            if gameOver:
                return gameOver, invalidRow, player

    def exhibitionGame(self):
        """
        Play an exhibition game of connect X.
        """
        done = False
        while not done:
            gameOver, invalidRow, player = self.allTurns()

            if gameOver:
                if invalidRow:
                    print("Player {} selected an invalid column.".format(player))
                    print("Player {} wins!".format((player % 2) + 1))
                else:
                    print("\nPlayer {} wins!".format(player))
            else:
                print("\nIt was a draw!")

            done = str.upper(input("\nPlay again? (Y/N):\n")) != 'Y'
            if not done:
                print("")
                self.board.resetBoard()


if __name__ == '__main__':
    game = Game(agent='rand')
    game.exhibitionGame()
