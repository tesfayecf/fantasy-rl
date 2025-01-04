import os
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from itertools import count

from environment import Environment

def select_action(state, w, epsilon, actions):
    if np.random.uniform(0, 1) < epsilon:
        return np.random.choice(range(actions))
    else:
        return np.argmax(np.dot(np.transpose(w), state))

def train(env: Environment, n_episodes=1000):
    # Create folder for logs
    folder_name = datetime.now().strftime("%Y%m%d%H%M%S")
    os.makedirs(f"Logs/SARSA/{folder_name}", exist_ok=True)

    # Initialize agent
    alpha = 0.3
    n = 1
    gamma = 1
    epsilon = (0.75)  # B/c 'everything looks bad', exploration is natural, so this can be 0.
    exploration_limit = 0.6
    episode_rewards = []
    # w = np.random.random((len(env.get_state()), env.action_space.n))
    w = np.zeros((
        env.observation_space.sample().shape[0],
        env.action_space.n
    ))
    
    for episode in range(n_episodes):
        state = env.reset()
        env.render()
        done = False
        epsilon_t = (epsilon) * (1 - episode/(n_episodes*exploration_limit))
        
        # Select first action
        action = select_action(state, w, epsilon_t, env.action_space.n)
        states = [state]  # S_0
        rewards = []  # reward[4] is the reward at t=5
        actions = [action]  # A_0
        T = np.inf

        for t in count(0, 1):
            if t < T:
                next_state, reward, done, _ = env.step(action)
                env.render()
                states.append(next_state)
                rewards.append(reward)
                if done:  # terminal
                    T = t + 1
                    actions.append(None)  # Otherwise actions and states won't have the same length.
                else:
                    action = select_action(next_state, w, epsilon_t, env.action_space.n)
                    actions.append(action)
            
            tau = t - n + 1
            if tau >= 0:
                g = sum([(gamma**i) * r for i, r in enumerate(rewards[tau:])])
                if tau + n < T:
                    state_curr = states[tau + n]
                    action_curr = actions[tau + n]
                    g += (gamma**n) * np.dot(w[:, action_curr], state_curr)
                state_tau = states[tau]
                action_tau = actions[tau]
                qsa_tau = np.dot(w[:, action_tau].transpose(), state_tau)
                w[:, action_tau] += (alpha * (g - qsa_tau) * state_tau)
            if tau == T - 1:
                break
            
        # Track progress
        episode_rewards.append(sum(rewards))
        
        # Print progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            print(f"Episode {episode + 1}/{n_episodes} - Avg Reward: {avg_reward:.2f} - Epsilon: {epsilon:.3f}")

        # Every 500 episodes, save the model and rewards plot
        if (episode + 1) % 10 == 0:
            episode_rewards_avg = np.convolve(np.array(episode_rewards), np.ones(10), mode='valid') / 10
            plt.plot(episode_rewards_avg)
            plt.title('Training Progress')
            plt.xlabel('Episode')
            plt.ylabel('Total Reward')
            plt.savefig(f"Logs/SARSA/{folder_name}/rewards.png")
    
    return