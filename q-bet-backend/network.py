import torch
from torch import nn
import numpy as np

# could name import this
# import torch.nn.functional as F


class FeedForwardNN(nn.Module):
    def __init__(self, in_dim, out_dim):
        super(FeedForwardNN, self).__init__()

        # apply affine linear transformation to incoming data
        self.layer1 = nn.Linear(in_dim, 64)
        self.layer2 = nn.Linear(64, 64)
        self.layer3 = nn.Linear(64, out_dim)

    def forward(self, obs):
        # convert observation to tensor
        # shouldn't be necessary? we convert to tensor in feature_vector.py
        if isinstance(obs, np.ndarray):
            obs = torch.tensor(obs, dtype=torch.float)

        activation1 = nn.functional.relu(self.layer1(obs))
        activation2 = nn.functional.relu(self.layer2(activation1))
        output = self.layer3(activation2)

        return output
