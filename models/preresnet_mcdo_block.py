import torch
import torch.nn as nn
import models.layers as layers
import torch.nn.functional as F


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_channels, channels, stride=1, groups=1, width_per_group=64, rate=0.3, **block_kwargs):
        super(BasicBlock, self).__init__()

        if groups != 1 or width_per_group != 64:
            raise ValueError("BasicBlock only supports groups=1 and base_width=64")
        width = int(channels * (width_per_group / 64.)) * groups

        self.rate = rate

        self.shortcut = []
        if stride != 1 or in_channels != channels * self.expansion:
            self.shortcut.append(layers.conv1x1(in_channels, channels * self.expansion, stride=stride))
            self.shortcut.append(layers.bn(channels * self.expansion))

        self.shortcut = nn.Sequential(*self.shortcut)
        self.bn1 = layers.bn(in_channels)
        self.relu1 = layers.relu()
        self.conv1 = layers.conv3x3(in_channels, width, stride=stride)
        self.bn2 = layers.bn(width)
        self.relu2 = layers.relu()
        self.conv2 = layers.conv3x3(width, channels * self.expansion)

    def forward(self, x):
        if len(self.shortcut) > 0:
            x = self.bn1(x)
            x = self.relu1(x)
            skip = self.shortcut(x)
        else:
            skip = self.shortcut(x)
            x = self.bn1(x)
            x = self.relu1(x)

        x = self.conv1(x)
        x = self.bn2(x)
        x = self.relu2(x)
        x = F.dropout(x, p=self.rate)
        x = self.conv2(x)

        x = skip + x

        return x


class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, in_channels, channels, stride=1, groups=1, width_per_group=64, rate=0.3, **block_kwargs):
        super(Bottleneck, self).__init__()

        width = int(channels * (width_per_group / 64.)) * groups

        self.rate = rate

        self.shortcut = []
        if stride != 1 or in_channels != channels * self.expansion:
            self.shortcut.append(layers.conv1x1(in_channels, channels * self.expansion, stride=stride))
            self.shortcut.append(layers.bn(channels * self.expansion))

        self.shortcut = nn.Sequential(*self.shortcut)
        self.bn1 = layers.bn(in_channels)
        self.relu1 = layers.relu()
        self.conv1 = layers.conv1x1(in_channels, width)
        self.bn2 = layers.bn(width)
        self.relu2 = layers.relu()
        self.conv2 = layers.conv3x3(width, width, stride=stride, groups=groups)
        self.bn3 = layers.bn(width)
        self.relu3 = layers.relu()
        self.conv3 = layers.conv1x1(width, channels * self.expansion)

    def forward(self, x):
        if len(self.shortcut) > 0:
            x = self.bn1(x)
            x = self.relu1(x)
            skip = self.shortcut(x)
        else:
            skip = self.shortcut(x)
            x = self.bn1(x)
            x = self.relu1(x)

        x = self.conv1(x)
        x = self.bn2(x)
        x = self.relu2(x)
        x = self.conv2(x)
        x = self.bn3(x)
        x = self.relu3(x)
        x = F.dropout(x, p=self.rate)
        x = self.conv3(x)

        x = skip + x

        return x
