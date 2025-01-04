import torch
import matplotlib.pyplot as plt

from algorithms.DQN.train import train
from pipeline import Pipeline
from environment import Environment

# Example usage:
if __name__ == "__main__":
     # Initialize your pipeline
    pipeline = Pipeline() 
    pipeline.init()
    # Initialize your environment
    env = Environment(pipeline)
    # Train the agent
    agent, rewards = train(env, n_episodes=5000)
    # Save the trained model
#     torch.save(agent.policy_net.state_dict(), "trained_model.pth")