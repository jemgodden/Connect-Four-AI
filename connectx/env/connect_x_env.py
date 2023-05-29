import logging
import random

import numpy as np
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts

from connectx.game.game import Board
from connectx.players.agents.agents import Agent, RandomAgent, MinimumAgent, LookAheadAgent


class ConnectXEnv(py_environment.PyEnvironment):
    """
    Custom Environment for Connect X that follows gym interface.
    """

    DISCOUNT = 1.0

    def __init__(
            self,
            rows: int = 6,
            cols: int = 7,
            win_condition: int = 4,
            opponent: str = 'rand'
    ):
        """
        This class is used to create a Connect-X Environment for the agents to use to train.

        :param rows: Integer value for the number of rows the board will have.
        :param cols: Integer value for the number of columns the board will have.
        :param win_condition: Integer value for the number of counters in a row required to win.
        :param opponent: String indicating the opposition agent.
        """
        super().__init__()

        self.board = Board(
            rows=rows,
            cols=cols,
            win_condition=win_condition,
        )

        self._agent_player_num = None
        self._opp_player_num = None
        self._assign_player_nums()

        self.opponent = self._assign_opponent(opponent)

        self._action_spec = array_spec.BoundedArraySpec(
            shape=(),
            dtype=np.int32,
            minimum=0,
            maximum=cols-1,
            name='play'
        )

        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(1, self.board.max_moves),
            dtype=np.int32,
            minimum=0,
            maximum=2,
            name='board'
        )
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _use_agent_file(self, agent_file_path: str) -> Agent:
        pass

    def _assign_opponent(self, opponent_name: str) -> Agent:
        """
        Initialises an agent to play the game.

        :param opponent_name: String that specifies the opponent that the agent will play, or contains a filepath to an
            agent model to be loaded in.
        :return: Agent class for chosen agent.
        """
        if '/' in opponent_name:
            return self._use_agent_file(opponent_name)

        opponent_name = str.lower(opponent_name)
        if opponent_name == 'rand':
            return RandomAgent(self._agent_player_num, self.board, self.verbose)
        elif opponent_name == 'min':
            return MinimumAgent(self._agent_player_num, self.board, self.verbose)
        elif opponent_name[:4] == 'look':
            try:
                steps = int(opponent_name[4:])
                if steps > 10:
                    raise ValueError(f"It is inadvisable to use more than 10 steps.")
                return LookAheadAgent(self._agent_player_num, self.board, self.verbose, steps)
            except IndexError():
                return LookAheadAgent(self._agent_player_num, self.board, self.verbose)
        else:
            raise ValueError(f"Specified agent \'{opponent_name}\' is either invalid.")

    def _assign_player_nums(self):
        self._agent_player_num = random.randint(1, 2)
        self._opp_player_num = 1 if self._agent_player_num == 2 else 2

    def _opponent_turn(self):
        action = self.opponent.perform_turn()
        self.board.update_board(action, self._opp_player_num)

    def _calculate_reward(self, player: int) -> float:
        """
        Calculates the sub-rewards specified for the agents.
        That being any number of counters in the following range: 1 < x < winCondition.

        :param player: Integer player value for player whose reward is being calculated.
        :return: Float value for the sub-reward.
        """
        reward = 0
        for i in range(2, self.board.win_condition):
            reward += self.board.check_for_lines(player, i) * ((i ** 2) * 0.001)
        return reward

    def _step(self, action: int) -> tuple:
        """
        Take a step within the environment.

        :param action: The action that the agent is taking.
        :return: Tuple containing the observation, reward, game-over flag, and info.
        """

        reward = 0

        if self.board.check_col_full(action):
            reward -= 100
            self._episode_ended = True
            return ts.termination(self.board.board_array(), reward)

        else:
            self.board.update_board(action, self._agent_player_num)

            if self.board.check_for_lines(self._agent_player_num) > 0:
                reward += 100
                self._episode_ended = True
                return ts.termination(self.board.board_array(), reward)

            else:
                reward += self._calculate_reward(self._agent_player_num)

                self._opponent_turn()

                if self.board.check_for_lines(self._opp_player_num) > 0:
                    reward -= 100
                    self._episode_ended = True
                    return ts.termination(self.board.board_array(), reward)

                else:
                    reward += self._calculate_reward(self._agent_player_num)

        return ts.transition(self.board.board_array(), reward, self.DISCOUNT)

    def _reset(self) -> tuple:
        """
        Reset the board so the environment can be reused.

        :return observation: Return the observation of the reset board.
        """
        self.board.reset_board()
        self._episode_ended = False
        self._assign_player_nums()

        if self.agent_player_num != 1:
            self._opponent_turn()

        return ts.restart(self.board.board_array())
