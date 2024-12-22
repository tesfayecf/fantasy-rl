from pipeline import Pipeline
from environment import Environment

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

def train():
    # Create the pipeline instance 
    pipeline = Pipeline()
    pipeline.init()
    # Wrap your custom environment in a vectorized environment
    env = make_vec_env(lambda: Environment(pipeline=pipeline), n_envs=1)
    # Initialize the PPO model
    model = PPO("MultiInputPolicy", env, verbose=1)
    # Train the model
    timesteps = 10
    model.learn(total_timesteps=timesteps)

if __name__ == '__main__':
    train()