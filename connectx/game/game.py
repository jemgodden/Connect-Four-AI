import random
import time

from connectx.game.board import Board
from connectx.agents.agents import Agent, RandomAgent, MinimumAgent, LookAheadAgent, PPOAgent, A2CAgent

from colorama import Fore, Style


class Game:
    def __init__(self,
                 verbose: bool = True,
                 boardRows: int = 6,
                 boardCols: int = 7,
                 winCondition: int = 4,
                 player1: str or None = None,
                 player2: str or None = None):
        """
        This class is used to play a game of Connect-X.

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
        :param player1: String that specifies who will be player 1, or what file should be loaded.
        :param player2: String that specifies who will be player 2, or what file should be loaded.
        """
        self.board: Board = Board(boardRows, boardCols, winCondition)

        if not isinstance(verbose, bool):
            raise TypeError("verbose must be a bool.")
        self.verbose: bool = verbose

        if player1 is not None and not isinstance(player1, str):
            raise TypeError("player1 must be a string or None.")
        if player2 is not None and not isinstance(player2, str):
            raise TypeError("player2 must be a string or None.")
        self.__players: list[Agent or None] = [
            self._assignPlayer(player1, 1), self._assignPlayer(player2, 2)]

    @property
    def players(self) -> list[Agent or None]:
        return self.__players

    def player(self, i: int) -> Agent or None:
        return self.__players[i - 1]

    def _userPlayer(self, player: int) -> bool:
        """
        Function used to determine if player is a user or an agent.

        :param player: Integer player value for specific player.
        :return: Boolean to indicate if player value given represents a user player. True if user player.
        """
        return self.player(player) is None

    def _useAgentFile(self, agentFilePath: str) -> Agent:
        """
        Function that uses a model's filepath to load in an agent.

        :param agentFilePath: String for filepath of agent model being loaded.
        :return: Agent being initialised.
        """
        agentDirs = agentFilePath.split('/')
        # Split the filepath by forward slash and filter to find agent
        # algorithm to load.
        if agentDirs[-1][:3] == 'PPO':
            return PPOAgent(self.board, agentFilePath)
        elif agentDirs[-1][:3] == 'A2C':
            return A2CAgent(self.board, agentFilePath)
        else:
            raise ValueError(
                f"Specified agent filepath \'{agentFilePath}\' does not exist or is not supported.")

    def _initialiseAgent(self, agent: str, player: int) -> Agent:
        """
        Initialises an agent to play the game.

        :param agent: String that specifies the agent that will play, or contains a filepath to an agent model to be
                      loaded in.
        :return: Agent class for chosen agent.
        """
        if '/' in agent:
            return self._useAgentFile(agent)

        agentLower = str.lower(agent)
        if agentLower == 'rand':
            return RandomAgent(self.board)
        elif agentLower == 'min':
            return MinimumAgent(self.board)
        elif agentLower[:4] == 'look':
            try:
                steps = int(agentLower[4:])
                return LookAheadAgent(self.board, player, steps)
            except IndexError():
                return LookAheadAgent(self.board, player)
        elif agentLower == 'ppo':
            return PPOAgent(self.board)
        elif agentLower == 'a2c':
            return A2CAgent(self.board)
        else:
            raise ValueError(f"Specified agent \'{agent}\' is either invalid.")

    def _assignPlayer(self, playerName: str or None,
                      player: int) -> Agent or None:
        """
        Function to determine if user playing as current player, and initialises specified agent if not.

        :param player: String that specifies whether this player is an agent or not (None).
        :return: None if human player, else Agent class for chosen agent.
        """
        if playerName is not None:
            return self._initialiseAgent(playerName, player)
        return None

    def _checkColValue(self, column: str) -> str or int:
        """
        Checks whether user column choice is possible.
        Forces user to re-enter column choice if not possible, until it is.

        :param column: Integer value for current players choice of column.
        :return column: Integer value of column if it is viable, else return string input by the user.
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

        if self.board.fullColCounter(arrCol):
            print("This is column is full. Please try again.")
            return column

        return int(column)

    def _playerTurn(self, player: int) -> int:
        """
        Function that allows the user to take a turn.

        :param player: Integer value representing which player's go it is.
        :return: Boolean indicating whether the win condition has been met.
        """
        column = None
        while not isinstance(column, int):
            # Reads in current players choice of column, checks whether it is possible, and executes it if so.
            # Forces user to re-enter column choice if not possible, until it
            # is.
            column = input("Please choose a column to drop a counter in:\n")
            column = self._checkColValue(column)

        # Convert column choice to an action (the correct format for the
        # program).
        action = column - 1
        self.board.updateBoard(action, player)
        return action

    def _agentTurn(self, player: int) -> tuple[bool, int]:
        """
        Agent (non-user) takes their turn.

        :param player: Integer value representing which player's go it is.
        :return: Boolean indicating whether the win condition has been met.
        """
        if self.verbose:
            print("Agent is choosing a move...\n")
            time.sleep(random.uniform(0.8, 1.2))

        column = self.player(player).performTurn()
        if self.board.fullColCounter(column):
            # If agent chooses a full column, end the game.
            return True, column

        self.board.updateBoard(column, player)
        return False, column

    def _turn(self, player: int) -> bool:
        """
        Complete a player's (user o agent) turn within the game.

        :param player: Integer indicating which player's go it is.
        :return player: Boolean representing whether the game is over.
        """
        if not self._userPlayer(player):
            fullColumn, action = self._agentTurn(player)
            if fullColumn:
                # End game if a full column is chosen.
                return True
        else:
            action = self._playerTurn(player)

        if self.verbose:
            self.board.printBoard(action)

        # Check if win condition has been met at the end of each turn.
        return self.board.checkXInARow(player) > 0

    def allTurns(self) -> int or None:
        """
        Iterate over all possible turns in the game, returning information early if the game is won/doesn't end in a
        draw.

        :return: Boolean indicating whether the game is over, and integer value representing which that won,
                 or None if a draw occurred.
        """
        if self.verbose:
            self.board.printBoard(None)

        for i in range(self.board.maxMoves):
            # Player value switches between 1 and 2.
            player = (i % 2) + 1

            if self.verbose:
                print("\nPlayer {}'s go...".format(player))

            gameOver = self._turn(player)
            if gameOver:
                return player

        return None

    def play(self):
        """
        Runes through the entirety of a game, allowing for a new game to played after one has finished.
        """
        done = False

        if self.verbose:
            # Show information on how each player can be identified.
            print(
                f"\nPlayer 1: {Fore.YELLOW}o{Style.RESET_ALL}\nPlayer 2: {Fore.RED}x{Style.RESET_ALL}\n")

        while not done:
            player = self.allTurns()

            if player:
                print("\nPlayer {} wins!".format(player))
            else:
                print("\nIt was a draw!")

            done = str.upper(input("\nPlay again? (Y/N):\n")) != 'Y'
            if not done:
                print("\n")
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
        Child class of Game used by RL agents to run Connect-X games for training purposes.

        :param verbose: Bool that indicates whether any information should be printed about that game.
        :param boardRows: Int value for the number of rows the game board will have.
        :param boardCols: Int value for the number of columns the game board will have.
        :param winCondition: Int value for the required number of counters in a row in order to win the game.
        :param player1: String that specifies who will be player 1, or what file should be loaded.
        :param player2: String that specifies who will be player 2, or what file should be loaded.
        """
        super().__init__(verbose=verbose,
                         boardRows=boardRows,
                         boardCols=boardCols,
                         winCondition=winCondition,
                         player1=player1,
                         player2=player2)

        if (player1 is None and player2 is None) or (
                player1 is not None and player2 is not None):
            raise Exception("Exactly one player must be a predefined agent.")

    def opponentTurn(self, oppPlayer: int = 1):
        """
        Function used to allow training agent's opponent to take their turn.

        :param oppPlayer: Integer player value for the agent's opponent.
        """
        self._turn(oppPlayer)

    def trainingAgentTurn(self, action: int, agentPlayer: int):
        """
        Update the board with the training agent's action, on its turn.

        :param action: Integer representing the action the agent will take (column it will drop a counter in) on its
                       turn.
        :param agentPlayer: Integer player value for the training agent.
        """
        self.board.updateBoard(action, agentPlayer)
