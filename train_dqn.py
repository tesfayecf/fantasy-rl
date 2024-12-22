import torch
import matplotlib.pyplot as plt

from DQN.train import train
from pipeline import Pipeline
from environment import Environment

# Example usage:
if __name__ == "__main__":
     # Initialize your pipeline
    pipeline = Pipeline() 
    pipeline.init()
    env = Environment(pipeline)
    
    # Train the agent
    agent, rewards = train(env, n_episodes=100)
    
    # Save the trained model
    torch.save(agent.policy_net.state_dict(), "trained_model.pth")
    
    # Plot training progress
    plt.plot(rewards)
    plt.title('Training Progress')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.show()