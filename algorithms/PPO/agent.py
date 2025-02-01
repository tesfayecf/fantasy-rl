
import torch
import torch.optim as optim
import numpy as np
from torch.distributions import Categorical

from networks import PolicyNetwork, ValueNetwork

# Hyperparameters
LEARNING_RATE = 3e-4
GAMMA = 0.99
CLIP_EPS = 0.2
ENTROPY_COEF = 0.01
CRITIC_LOSS_COEF = 0.5
BATCH_SIZE = 64
EPOCHS = 10

class PPOAgent:
    def __init__(self, obs_dim, action_dim):
        self.policy = PolicyNetwork(obs_dim, action_dim)
        self.value = ValueNetwork(obs_dim)
        self.policy_optimizer = optim.Adam(self.policy.parameters(), lr=LEARNING_RATE)
        self.value_optimizer = optim.Adam(self.value.parameters(), lr=LEARNING_RATE)

    def select_action(self, obs):
        logits = self.policy(obs)
        dist = Categorical(logits=logits)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob

    def compute_returns(self, rewards, dones, next_value):
        """
        Compute the discounted returns using GAE.
        """
        returns = []
        R = next_value
        for reward, done in zip(reversed(rewards), reversed(dones)):
            R = reward + GAMMA * R * (1.0 - done)
            returns.insert(0, R)
        return returns

    def train(self, trajectory):
        obs = torch.tensor(trajectory['obs'], dtype=torch.float32)
        actions = torch.tensor(trajectory['actions'], dtype=torch.int64)
        log_probs = torch.tensor(trajectory['log_probs'], dtype=torch.float32)
        rewards = trajectory['rewards']
        dones = trajectory['dones']
        next_obs = torch.tensor(trajectory['next_obs'], dtype=torch.float32)

        with torch.no_grad():
            next_value = self.value(next_obs).squeeze(-1).numpy()
            returns = self.compute_returns(rewards, dones, next_value)
            returns = torch.tensor(returns, dtype=torch.float32)
            advantages = returns - self.value(obs).squeeze(-1)

        for _ in range(EPOCHS):
            indices = np.random.permutation(len(obs))
            for i in range(0, len(indices), BATCH_SIZE):
                batch_indices = indices[i:i + BATCH_SIZE]

                batch_obs = obs[batch_indices]
                batch_actions = actions[batch_indices]
                batch_log_probs = log_probs[batch_indices]
                batch_advantages = advantages[batch_indices].detach()
                batch_returns = returns[batch_indices]

                # Compute policy loss
                logits = self.policy(batch_obs)
                dist = Categorical(logits=logits)
                new_log_probs = dist.log_prob(batch_actions)
                entropy = dist.entropy().mean()

                ratio = (new_log_probs - batch_log_probs).exp()
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1 - CLIP_EPS, 1 + CLIP_EPS) * batch_advantages
                policy_loss = -torch.min(surr1, surr2).mean() - ENTROPY_COEF * entropy

                # Compute value loss
                values = self.value(batch_obs).squeeze(-1)
                value_loss = CRITIC_LOSS_COEF * (batch_returns - values).pow(2).mean()

                # Optimize both networks
                self.policy_optimizer.zero_grad()
                self.value_optimizer.zero_grad()
                (policy_loss + value_loss).backward()
                self.policy_optimizer.step()
                self.value_optimizer.step()