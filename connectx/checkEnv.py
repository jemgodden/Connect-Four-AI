from core import ConnectXEnv


if __name__ == '__main__':
    """
    This procedural file is used to test the connect-x gym environment.
    """
    env = ConnectXEnv(player2='rand')
    episodes = 10

    for episode in range(episodes):
        done = False
        obs = env.reset()
        env.render()
        while not done:
            random_action = env.action_space.sample()
            print("action", random_action)
            obs, reward, done, info = env.step(random_action)
            print('reward', reward)
            env.render()
