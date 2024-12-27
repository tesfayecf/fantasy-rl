import torch
import random
import torch.nn as nn
import torch.cuda
import numpy as np
import torch.optim as optim
from collections import deque

from DQN.network import DQNNetwork

class Agent:
    def __init__(self, env, memory_size=10000):
        self.env = env
        self.memory = deque(maxlen=memory_size)
        
        # Calculate observation size
        sample_obs = env._get_state()
        obs_size = (
            np.prod(sample_obs['team'].shape) + 
            np.prod(sample_obs['market'].shape) + 
            np.prod(sample_obs['budget'].shape)
        )
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy_net = DQNNetwork(obs_size, env.action_space.n).to(self.device)
        self.target_net = DQNNetwork(obs_size, env.action_space.n).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
        self.optimizer = optim.Adam(self.policy_net.parameters())
        self.criterion = nn.MSELoss()

    def flatten_state(self, state):
        """Convert dictionary state to flat array."""
        team_flat = state['team'].flatten()
        market_flat = state['market'].flatten()
        budget_flat = state['budget'].flatten()
        return np.concatenate([team_flat, market_flat, budget_flat])

    def select_action(self, state, epsilon):
        """Select action using epsilon-greedy policy."""
        if random.random() < epsilon:
            return self.env.action_space.sample()
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            return q_values.max(1)[1].item()

    def store_transition(self, state, action, reward, next_state, done):
        """Store transition in replay memory."""
        self.memory.append((
            state,
            action,
            reward,
            next_state,
            done
        ))

    def train_step(self, batch_size, gamma=0.99):
        """Perform one step of training."""
        if len(self.memory) < batch_size:
            return
        
        # Sample batch
        batch = random.sample(self.memory, batch_size)
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*batch)
        
        # Convert to tensors
        state_batch = torch.FloatTensor(state_batch).to(self.device)
        action_batch = torch.LongTensor(action_batch).to(self.device)
        reward_batch = torch.FloatTensor(reward_batch).to(self.device)
        next_state_batch = torch.FloatTensor(next_state_batch).to(self.device)
        done_batch = torch.FloatTensor(done_batch).to(self.device)
        
        # Compute current Q values
        current_q_values = self.policy_net(state_batch).gather(1, action_batch.unsqueeze(1))
        
        # Compute next Q values
        next_q_values = self.target_net(next_state_batch).max(1)[0].detach()
        expected_q_values = reward_batch + gamma * next_q_values * (1 - done_batch)
        
        # Compute loss and update
        loss = self.criterion(current_q_values.squeeze(), expected_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
