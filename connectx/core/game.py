import time
from .board import Board
from .agents import Agent, RandomAgent, MinimumAgent, LookAheadAgent, PPOAgent


class Game:
    def __init__(self,
                 verbose: bool = True,
                 boardRows: int = 6,
                 boardCols: int = 7,
                 winCondition: int = 4,
                 player1: str or None = None,
                 player2: str or None = None):
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
        self.board: Board = Board(boardRows, boardCols, winCondition)

        if type(verbose) is not bool:
            raise TypeError("verbose must be a bool.")
        self.verbose: bool = verbose

        if player1 is not None and type(player1) is not str:
            raise TypeError("player1 must be a string or None.")
        if player2 is not None and type(player2) is not str:
            raise TypeError("player2 must be a string or None.")
        self.__players: list[Agent] = [self._assignPlayer(player1, 1), self._assignPlayer(player2, 2)]

    @property
    def players(self):
        return self.__players

    def player(self, i: int):
        return self.__players[i-1]

    def _initialiseAgent(self, agent: str, player: int) -> Agent:
        """
        Initialises an agent to play the game.
        :param agent: String that specifies the agent that will play.
        :return: Agent class for chosen agent.
        """
        if str.lower(agent) == 'rand':
            return RandomAgent(self.board)
        elif str.lower(agent) == 'min':
            return MinimumAgent(self.board)
        elif str.lower(agent) == 'look':
            return LookAheadAgent(self.board, player)
        elif str.lower(agent) == 'ppo':
            return PPOAgent(self.board)
        else:
            raise ValueError("Specified agent \"{}\" is either invalid or not supported.".format(agent))

    def _assignPlayer(self, playerName: str or None, player: int) -> Agent or None:
        """
        Initialises an agent to play against.
        :param player: String that specifies whether this player is an agent or not (None).
        :return: None if human player, else Agent class for chosen agent.
        """
        if playerName is not None:
            return self._initialiseAgent(playerName, player)
        return None

    def _checkColValue(self, column: str) -> str or int:
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
        if self.board.getColCounter(arrCol) == self.board.rows:
            print("This is column is full. Please try again.")
            return column

        return int(column)

    def _playerTurn(self, player: int) -> int:
        """
        Reads in current players choice of column, checks whether it is possible, and executes it.
        :param player: Int value representing which player's go it is.
        :return: Bool indicating whether the win condition has been met.
        """
        column = None
        while type(column) is not int:
            column = input("Please choose a column to drop a counter in:\n")
            column = self._checkColValue(column)
        action = column - 1
        self.board.updateBoard(action, player)  # Subtract 1 from column to get correct array index.
        return action

    def _agentTurn(self, player: int) -> tuple[bool, int]:
        """
        Opponent agent takes their go.
        :param player: Int value representing which player's go it is.
        :return: Bool indicating whether the win condition has been met.
        """
        if self.verbose:
            print("Agent is choosing a move...\n")
            time.sleep(0.3)
        column = self.player(player).performTurn()
        if self.board.getColCounter(column) == self.board.rows:
            return True, column
        self.board.updateBoard(column, player)
        return False, column

    def _turn(self, player: int) -> bool:
        """
        Complete a single turn in the game.
        :param player: int indicating which player's go it is.
        :return player: bool representing whether the game is over.
        """
        if self.player(player) is not None:
            fullColumn, action = self._agentTurn(player)
            if fullColumn:
                return True
        else:
            action = self._playerTurn(player)
        if self.verbose:
            self.board.printBoard(action)
        return self.board.checkXInARow(player) > 0

    def _allTurns(self) -> tuple[bool, int or None]:
        """
        Iterate over all possible turns in the game, resulting in a draw if no win condition is ever met.
        :return: Bool indicating whether the win condition has been met.
        :return player: Int value representing which player won.
        """
        if self.verbose:
            self.board.printBoard(None)
        for i in range(self.board.maxMoves):
            player = (i % 2) + 1
            if self.verbose:
                print("\nPlayer {}'s go...".format(player))
            gameOver = self._turn(player)
            if gameOver:
                return gameOver, player
        return False, None

    def play(self):
        """
        Play an exhibition game of connect X.
        """
        done = False
        while not done:
            gameOver, player = self._allTurns()

            if gameOver:
                print("\nPlayer {} wins!".format(player))
            else:
                print("\nIt was a draw!")

            done = str.upper(input("\nPlay again? (Y/N):\n")) != 'Y'
            if not done:
                print("")
                self.board.resetBoard()


class TrainingGame(Game):
    def __init__(self,
                 verbose: bool = False,
                 boardRows: int = 6,
                 boardCols: int = 7,
                 winCondition: int = 4,
                 player1: str or None = 'rand',
                 player2: str or None = None):
        """
        Class used to run connect-x games for the agents to train with.

        :param verbose:
        :param boardRows:
        :param boardCols:
        :param winCondition:
        :param player1:
        :param player2:
        """
        super().__init__(verbose=verbose,
                         boardRows=boardRows,
                         boardCols=boardCols,
                         winCondition=winCondition,
                         player1=player1,
                         player2=player2)

        if (player1 is None and player2 is None) or (player1 is not None and player2 is not None):
            raise Exception("Exactly one player must be a predefined agent.")

    def opponentTurn(self, oppOrder: int = 1):
        """
        Training agent's opponent will make its turn.

        :return: Int for the player who won the game, or 0 if it was a draw.
        """
        self._turn(oppOrder)

    def trainingAgentTurn(self, action: int, agentOrder: int = 2):
        """
        Update the board with the training agents action, on its turn.

        :param action: The action the agent will take (column it will drop a counter in) on its turn.
        :param agentOrder: Which player the training agent is.
        """
        self.board.updateBoard(action, agentOrder)
