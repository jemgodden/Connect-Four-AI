import time
from board import *
from agents import *


class Game:
    def __init__(self, verbose: bool = True,
                 boardRows: int = 6,
                 boardCols: int = 7,
                 winCondition: int = 4,
                 player1: str = None,
                 player2: str = None):
        """
        This class is used to play a game of connect-x.

        Usage:
        '''python
        from game import *
        game = Game()
        game.play()
        '''

        :param verbose: Bool that indicates whether any information should be printed about that game.
        :param boardRows: Int value for the number of rows the game board will have.
        :param boardCols: Int value for the number of columns the game board will have.
        :param winCondition: Int value for the required number of counters in a row in order to win the game.
        :param player1: String that specifies who will be player 1.
        :param player2: String that specifies who will be player 2.
        """
        if type(verbose) is not bool:
            raise TypeError("verbose must be a bool.")
        self.verbose: bool = verbose

        if player1 is not None and type(player1) is not str:
            raise TypeError("player1 must be a string or None.")
        if player2 is not None and type(player2) is not str:
            raise TypeError("player2 must be a string or None.")
        self.board: Board = Board(boardRows, boardCols, winCondition)
        self.players: list[Agent] = [self.__assignPlayer(player1), self.__assignPlayer(player2)]

    def __initialiseAgent(self, agent: str) -> Agent:
        """
        Initialises an agent to play the game.
        :param agent: String that specifies the agent that will play.
        :return: Agent class for chosen agent.
        """
        if str.lower(agent) == 'rand':
            return RandomAgent(self.board)
        else:
            raise ValueError("Specified agent \"{}\" does not exist.".format(agent))

    def __assignPlayer(self, player: str) -> Agent:
        """
        Initialises an agent to play against.
        :param player: String that specifies whether this player is an agent or not (None).
        :return: None if human player, else Agent class for chosen agent.
        """
        if player is not None:
            return self.__initialiseAgent(player)
        return None

    def __checkColValue(self, column: int) -> int:
        """
        Checks whether current column choice is possible.
        :param column: Int value for current players choice of column.
        :return column: Returns integer value of column if it is viable, else return str input by the user.
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
            print("This is column is full. Please try again.")
            return column

        return int(column)

    def __playerTurn(self, player: int) -> bool:
        """
        Reads in current players choice of column, checks whether it is possible, and executes it.
        :param player: Int value representing which player's go it is.
        :return: Bool indicating whether the win condition has been met.
        """
        column = None
        while type(column) is not int:
            column = input("Please choose a column to drop a counter in:\n")
            column = self.__checkColValue(column)

        self.board.updateBoard(column, player)
        if self.verbose:
            self.board.printBoard()
        return self.board.checkWinConditions()

    def __agentTurn(self, agent: Agent, player: int) -> bool:
        """
        Opponent agent takes their go.
        :param player: Int value representing which player's go it is.
        :return: Bool indicating whether the win condition has been met.
        """
        if self.verbose:
            print("Agent is choosing a move...\n")
            time.sleep(1)
        column = agent.performTurn()
        self.board.updateBoard(column, player)
        if self.verbose:
            self.board.printBoard()
        return self.board.checkWinConditions()

    def __turn(self, player: int) -> bool:
        """
        Complete a single turn in the game.
        :param player: int indicating which player's go it is.
        :return player: bool representing whether the game is over.
        """
        curPlayer = self.players[player - 1]
        if curPlayer is not None:
            return self.__agentTurn(curPlayer, player)
        else:
            return self.__playerTurn(player)

    def __allTurns(self) -> tuple[bool, int]:
        """
        Iterate over all possible turns in the game, resulting in a draw if no win condition is ever met.
        :return: Bool indicating whether the win condition has been met.
        :return player: Int value representing which player won.
        """
        if self.verbose:
            self.board.printBoard()
        for i in range(self.board.maxMoves):
            player = (i % 2) + 1
            if self.verbose:
                print("\nPlayer {}'s go...".format(player))
            gameOver = self.__turn(player)
            if gameOver:
                return gameOver, player

    def exhibitionGame(self):
        """
        Play an exhibition game of connect X.
        """
        done = False
        while not done:
            gameOver, player = self.__allTurns()

            if gameOver:
                print("\nPlayer {} wins!".format(player))
            else:
                print("\nIt was a draw!")

            done = str.upper(input("\nPlay again? (Y/N):\n")) != 'Y'
            if not done:
                print("")
                self.board.resetBoard()
