import os
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

from environment import Environment
from DQN.agent import Agent

def train(env: Environment, n_episodes=1000, batch_size=64, target_update=10):
    # Create folder for logs
    folder_name = datetime.now().strftime("%Y%m%d%H%M%S")
    os.makedirs(f"logs/DQN/{folder_name}", exist_ok=True)

    # Initialize agent
    agent = Agent(env)
    epsilon_start = 1.0
    epsilon_end = 0.01
    epsilon_decay = 0.995
    epsilon = epsilon_start
    episode_rewards = []
    
    for episode in range(n_episodes):
        state = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            # Select and perform action
            action = agent.select_action(state, epsilon)
            next_state, reward, done, _ = env.step(action)
            # env.render()
            
            # Store transition and train
            agent.store_transition(state, action, reward, next_state, done)
            loss = agent.train_step(batch_size)
            
            total_reward += reward
            state = next_state
            
        # Update target network
        if episode % target_update == 0:
            agent.target_net.load_state_dict(agent.policy_net.state_dict())
        
        # Decay epsilon
        epsilon = max(epsilon_end, epsilon * epsilon_decay)
        
        # Track progress
        episode_rewards.append(total_reward)
        
        # Print progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            print(f"Episode {episode + 1}/{n_episodes} - Avg Reward: {avg_reward:.2f} - Epsilon: {epsilon:.3f}")

        # Every 500 episodes, save the model and rewards plot
        if (episode + 1) % 10 == 0:
            plt.plot(episode_rewards)
            plt.title('Training Progress')
            plt.xlabel('Episode')
            plt.ylabel('Total Reward')
            plt.savefig(f"logs/DQN/{folder_name}/rewards.png")
    
    return agent, episode_rewards