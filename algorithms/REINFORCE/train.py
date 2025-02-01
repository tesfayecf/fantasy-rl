import os
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

from environment import Environment

def policy(state, w):
    """Compute action probabilities using a softmax policy."""
    z = np.dot(state, w)
    exp = np.exp(z - np.max(z))  # for numerical stability
    return exp / exp.sum()

def select_action(state, w):
    """Select action based on probabilities from the policy."""
    probs = policy(state, w)
    return np.random.choice(len(probs), p=probs)

def train(env: Environment, n_episodes=1000):
    # Create folder for logs
    folder_name = datetime.now().strftime("%Y%m%d%H%M%S")
    os.makedirs(f"Logs/REINFORCE/{folder_name}", exist_ok=True)

    # Initialize parameters
    alpha = 0.01  # learning rate
    gamma = 0.99  # discount factor
    w = np.random.rand(len(env.get_state()), env.action_space.n) * 0.01

    episode_rewards = []

    for episode in range(n_episodes):
        state = env.reset()
        done = False

        states = []
        actions = []
        rewards = []

        # Generate an episode
        while not done:
            action = select_action(state, w)
            next_state, reward, done, _ = env.step(action)
            env.render()

            states.append(state)
            actions.append(action)
            rewards.append(reward)

            state = next_state

        # Compute returns G_t for each timestep
        G = 0
        returns = []
        for reward in reversed(rewards):
            G = reward + gamma * G
            returns.insert(0, G)

        returns = np.array(returns)
        returns = (returns - np.mean(returns)) / (np.std(returns) + 1e-8)  # Normalize returns

        # Policy gradient update
        for t in range(len(states)):
            state_t = states[t]
            action_t = actions[t]
            G_t = returns[t]

            probs = policy(state_t, w)
            grad = -probs
            grad[action_t] += 1  # Increase gradient for the taken action

            w += alpha * G_t * np.outer(state_t, grad)

        # Track progress
        episode_rewards.append(sum(rewards))

        # Print progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            print(f"Episode {episode + 1}/{n_episodes} - Avg Reward: {avg_reward:.2f}")

        # Save progress every 100 episodes
        if (episode + 1) % 10 == 0:
            episode_rewards_avg = np.convolve(np.array(episode_rewards), np.ones(10), mode='valid') / 10
            plt.plot(episode_rewards_avg)
            plt.title('Training Progress')
            plt.xlabel('Episode')
            plt.ylabel('Total Reward')
            plt.savefig(f"Logs/REINFORCE/{folder_name}/rewards.png")

    return
