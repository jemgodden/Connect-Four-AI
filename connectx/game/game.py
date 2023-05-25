from connectx.game.board import Board
from connectx.players.players import Player, UserPlayer
from connectx.players.agents.agents import Agent, RandomAgent, MinimumAgent, LookAheadAgent

from colorama import Fore, Style


class Game:

    NO_WIN = 0
    WIN = 1
    FULL_COLUMN_WIN = 2

    def __init__(
            self,
            verbose: bool = True,
            board_rows: int = 6,
            board_cols: int = 7,
            win_condition: int = 4,
            player1: str or None = None,
            player2: str or None = None
    ):
        """
        This class is used to play a game of Connect-X.

        Usage:
        '''python
        from game import *

        game = Game()
        game.play()
        '''

        :param verbose: Bool that indicates whether any information should be printed about that game.
        :param board_rows: Int value for the number of rows the game board will have.
        :param board_cols: Int value for the number of columns the game board will have.
        :param win_condition: Int value for the required number of counters in a row in order to win the game.
        :param player1: String that specifies who will be player 1, or what file should be loaded.
        :param player2: String that specifies who will be player 2, or what file should be loaded.
        """
        self.board: Board = Board(board_rows, board_cols, win_condition)

        if not isinstance(verbose, bool):
            raise TypeError("verbose must be a bool.")
        self.verbose: bool = verbose

        if player1 is not None and not isinstance(player1, str):
            raise TypeError("player1 must be a string or None.")
        if player2 is not None and not isinstance(player2, str):
            raise TypeError("player2 must be a string or None.")

        self.__players: list[Agent or None] = [
            self._initialise_player(player1, 1),
            self._initialise_player(player2, 2)
        ]

    @property
    def players(self) -> list[Player]:
        return self.__players

    def player(self, i: int) -> Player:
        return self.__players[i - 1]

    def _use_agent_file(self, agent_file_path: str, player_num: int) -> Agent:
        """
        Function that uses a model's filepath to load in an agent.

        :param agent_file_path: String for filepath of agent model being loaded.
        :param player_num: Integer value for which player in the game it is.
        :return: Agent being initialised.
        """
        agent_dirs = agent_file_path.split('/')
        # Split the filepath by forward slash and filter to find agent algorithm to load.
        if agent_dirs[-1][:3] == 'PPO':
            return PPOAgent(player_num, self.board, self.verbose, agent_file_path)
        elif agent_dirs[-1][:3] == 'A2C':
            return A2CAgent(player_num, self.board, self.verbose, agent_file_path)
        else:
            raise ValueError(
                f"Specified agent filepath \'{agent_file_path}\' does not exist or is not supported.")

    def _initialise_agent(self, agent_name: str, player_num: int) -> Agent:
        """
        Initialises an agent to play the game.

        :param agent_name: String that specifies the agent that will play, or contains a filepath to an agent model to
            be loaded in.
        :param player_num: Integer value to indicate which player the agent is.
        :return: Agent class for chosen agent.
        """
        if '/' in agent_name:
            return self._use_agent_file(agent_name, player_num)

        agent_name = str.lower(agent_name)
        if agent_name == 'rand':
            return RandomAgent(player_num, self.board, self.verbose)
        elif agent_name == 'min':
            return MinimumAgent(player_num, self.board, self.verbose)
        elif agent_name[:4] == 'look':
            try:
                steps = int(agent_name[4:])
                if steps > 10:
                    raise ValueError(f"It is inadvisable to use more than 10 steps.")
                return LookAheadAgent(player_num, self.board, self.verbose, steps)
            except IndexError():
                return LookAheadAgent(player_num, self.board, self.verbose)
        elif agent_name == 'ppo':
            return PPOAgent(player_num, self.board, self.verbose)
        elif agent_name == 'a2c':
            return A2CAgent(player_num, self.board, self.verbose)
        else:
            raise ValueError(f"Specified agent \'{agent_name}\' is either invalid.")

    def _initialise_player(self, player_name: str or None, player_num: int) -> Player:
        """
        Function to determine if user playing as current player, and initialises specified agent if not.

        :param player_name: String that specifies whether this player is an agent or not (None).
        :param player_num: Integer value to indicate which player the player is.
        :return: None if human player, else Agent class for chosen agent.
        """
        if player_name is not None:
            return self._initialise_agent(player_name, player_num)
        return UserPlayer(player_num, self.board)

    def _turn(self, player: Player) -> int:
        """
        Complete a player's (user o agent) turn within the game.

        :param player: Integer indicating which player's go it is.
        :return player: Boolean representing whether the game is over.
        """
        action = player.perform_turn()

        if self.board.check_col_full(action):
            return self.FULL_COLUMN_WIN

        self.board.update_board(action, player.player_num)
        if self.verbose:
            self.board.print_board(action)

        # Check if win condition has been met at the end of each turn.
        return self.WIN if self.board.check_for_lines(player.player_num) > 0 else self.NO_WIN

    def all_turns(self) -> int or None:
        """
        Iterate over all possible turns in the game, returning information early if the game is won/doesn't end in a
        draw.

        :return: Boolean indicating whether the game is over, and integer value representing which that won,
                 or None if a draw occurred.
        """
        if self.verbose:
            self.board.print_board(None)

        for i in range(self.board.max_moves):
            # Player value switches between 1 and 2.
            cur_player = (i % 2) + 1

            if self.verbose:
                print("\nPlayer {}'s go...".format(cur_player))

            win_flag = self._turn(self.player(cur_player))
            if win_flag is self.WIN:
                return cur_player
            if win_flag is self.FULL_COLUMN_WIN:
                return 1 if cur_player == 2 else 2

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
            winning_player = self.all_turns()

            if self.verbose:
                if winning_player:
                    print("\nPlayer {} wins!".format(winning_player))
                else:
                    print("\nIt was a draw!")

            done = str.upper(input("\nPlay again? (Y/N):\n")) != 'Y'
            if not done:
                print("\n")
                self.board.reset_board()
