import os
from connectxEnv import ConnectXEnv
from stable_baselines3 import PPO

MODEL_NAME = 'PPO_v1.1'
MODELS_DIR = f"models/{MODEL_NAME}/"
LOGS_DIR = f"logs/"
TIMESTEPS = 10000
MAX_ITERS = 250

if __name__ == '__main__':
    """
    This procedural file is used to train a connect-x agent.
    """

    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    # # PPO_v0.0: 50 iterations of 10000 timesteps. Training as player 1.
    # env = ConnectXEnv(player2='min')
    # env.reset()
    # model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=LOGS_DIR)

    # # PPO_v0.1: 50 iterations of 10000 timesteps. Training as player 2.
    # env = ConnectXEnv(player1='min')
    # env.reset()
    # model = PPO.load('models/PPO_v0.0/PPO_v0.0_500000', env, verbose=1, tensorboard_log=LOGS_DIR)

    # # PPO_v0.2: 100 iterations of 10000 timesteps. Training as player 1.
    # env = ConnectXEnv(player2='rand')
    # env.reset()
    # model = PPO.load('models/PPO_v0.1/PPO_v0.1_500000', env, verbose=1, tensorboard_log=LOGS_DIR)

    # # PPO_v0.3: 100 iterations of 10000 timesteps. Training as player 2.
    # env = ConnectXEnv(player1='rand')
    # env.reset()
    # model = PPO.load('models/PPO_v0.2/PPO_v0.2_1000000', env, verbose=1, tensorboard_log=LOGS_DIR)

    # # PPO_v1.0: 250 iterations of 10000 timesteps. Training as player 2.
    # env = ConnectXEnv(player1='ppo')
    # env.reset()
    # model = PPO.load('models/PPO_v0.3/PPO_v0.3_1000000', env, verbose=1, tensorboard_log=LOGS_DIR)

    # PPO_v1.1: 250 iterations of 10000 timesteps. Training as player 1.
    env = ConnectXEnv(player2='ppo')
    env.reset()
    model = PPO.load('models/PPO_v1.0/PPO_v1.0_2500000', env, verbose=1, tensorboard_log=LOGS_DIR)

    iteration = 0
    while iteration < MAX_ITERS:
        iteration += 1
        model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"{MODEL_NAME}")
        model.save(f"{MODELS_DIR}/{MODEL_NAME+'_'+str(TIMESTEPS*iteration)}")
