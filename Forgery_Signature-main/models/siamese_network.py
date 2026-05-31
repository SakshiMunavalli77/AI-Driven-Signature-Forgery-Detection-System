import torch
import torch.nn as nn
from torchvision import models

class SiameseNetwork(nn.Module):
    def __init__(self, embedding_dim=128):
        super(SiameseNetwork, self).__init__()
        self.embedding_dim = embedding_dim

        # Use ResNet50 (same as training)
        self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

        # Remove final classification layer
        self.backbone.fc = nn.Identity()

        # Embedding layer - supports configurable dimensions
        self.embedding = nn.Sequential(
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Linear(512, embedding_dim)
        )

    def forward_once(self, x):
        x = self.backbone(x)
        x = self.embedding(x)
        return x

    def forward(self, input1, input2):
        output1 = self.forward_once(input1)
        output2 = self.forward_once(input2)
        return output1, output2