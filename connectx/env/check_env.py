from connectx.env.connect_x_env import ConnectXEnv

from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils

NUM_GAMES = 10


if __name__ == '__main__':
    """
    Procedural script used to test that the Connect-X Gym Environment is working as expected.
    Prints information to console so user and confirm environment working as expected.
    """

    # Create basic environment with random opponent for agent.
    py_env = ConnectXEnv()
    utils.validate_py_environment(py_env, episodes=5)

    env = tf_py_environment.TFPyEnvironment(py_env)

    # for game in range(NUM_GAMES):
    #     done = False
    #
    #     # Reset environment before each use.
    #     obs = env.reset()
    #     env.render()
    #
    #     while not done:
    #         # Make agent do a random action.
    #         random_action = env.action_space.sample()
    #         print("action", random_action)
    #
    #         obs, reward, done, info = env.step(random_action)
    #         print('reward', reward)
    #         env.render()
