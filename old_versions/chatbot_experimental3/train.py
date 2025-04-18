# -*- coding: utf-8 -*-
"""
Created on Sun Apr  6 14:37:07 2025

@author: Fredrik
Train file
"""
import json
from nltk_utils import tokenize,bag_of_words,stem
import numpy as np

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from model import NeuralNet

with open("intents.json", "r") as file:
    intents = json.load(file)

all_words = []
tags = []
xy = []
for intent in intents["intents"]:
    tag = intent["tag"]
    tags.append(tag)
    for pattern in intent["patterns"]:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w,tag))

ignore_words = ["?","!",".",","]
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

#print(tags)

X_train = []
y_train = []

for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    
    label = tags.index(tag)
    y_train.append(label) # CrossEntropyLoss

X_train = np.array(X_train)
y_train = np.array(y_train)

class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train
    
    #dataset[idx]
    def __getitem__(self, index):
        return torch.from_numpy(self.x_data[index]), torch.tensor(self.y_data[index], dtype=torch.long)
    
    def __len__(self):
        return self.n_samples
    
#Hyperparameters
batch_size = 8
hidden_size = 8
output_size = len(tags)
input_size = len(X_train[0])
learning_rate = 0.001
num_epochs = 1000
# =============================================================================
# print(input_size, len(all_words))
# print(output_size, tags)
# =============================================================================

    
# Dataset and loader
dataset = ChatDataset()
train_loader = DataLoader(dataset=ChatDataset(), batch_size=batch_size, shuffle=True, num_workers=0)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")    
model = NeuralNet(input_size, hidden_size, output_size).to(device)

#Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(device)
        
        # Forward
        output = model(words)
        loss = criterion(output, labels)
        
        # backward and optimizer step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    if (epoch +1) % 100 == 0:
        print(f"epoch {epoch+1}/{num_epochs}, loss={loss.item():.4f}")

print(f"final loss, loss={loss.item():.4f}")

data = {
        "model_state": model.state_dict(),
        "input_size": input_size,
        "output_size": output_size,
        "hidden_size": hidden_size,
        "all_words": all_words,
        "tags": tags
        }

FILE = "data.pth"
torch.save(data, FILE)

print(f"training complete. File saved to {FILE}")