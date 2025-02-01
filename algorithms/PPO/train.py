import torch

from environment import Environment
from pipeline import Pipeline
from PPO.agent import PPOAgent

def train(env, agent, num_episodes=1000, max_steps_per_episode=200):
    for episode in range(num_episodes):
        obs = env.reset()
        obs = torch.tensor(obs['team'].flatten(), dtype=torch.float32)
        trajectory = {
            'obs': [],
            'actions': [],
            'log_probs': [],
            'rewards': [],
            'dones': [],
            'next_obs': [],
        }
        episode_reward = 0

        for step in range(max_steps_per_episode):
            trajectory['obs'].append(obs.numpy())

            # Select action
            action, log_prob = agent.select_action(obs)
            trajectory['actions'].append(action)
            trajectory['log_probs'].append(log_prob.item())

            # Step environment
            next_obs, reward, done, _ = env.step(action)
            next_obs = torch.tensor(next_obs['team'].flatten(), dtype=torch.float32)

            trajectory['rewards'].append(reward)
            trajectory['dones'].append(done)
            trajectory['next_obs'].append(next_obs.numpy())

            obs = next_obs
            episode_reward += reward

            if done:
                break

        print(f"Episode {episode + 1}, Total Reward: {episode_reward}")

        # Train the agent
        agent.train(trajectory)

# Initialize environment and PPO agent
env = Environment(pipeline=Pipeline())
obs_dim = env.observation_space['team'].shape[0] * env.observation_space['team'].shape[1]
action_dim = env.action_space.n
agent = PPOAgent(obs_dim, action_dim)

# Train the agent
train(env, agent)
