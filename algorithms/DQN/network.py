import torch
import torch.nn as nn

class DQNNetwork(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQNNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(n_observations, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, n_actions)
        )

    def forward(self, x):
        return self.network(x)

