from stable_baselines3 import PPO
import os
from connectxEnv import ConnectXEnv
import time


TIMESTEPS = 10000

if __name__ == '__main__':
    """
    This procedural file is used to train a connect-x agent.
    """
    models_dir = f"models/{int(time.time())}/"
    logdir = f"logs/{int(time.time())}/"

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    env = ConnectXEnv('rand')
    env.reset()

    model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir)

    iters = 0
    while iters < 100:
        iters += 1
        model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"PPO")
        model.save(f"{models_dir}/{TIMESTEPS*iters}")
