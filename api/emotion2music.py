from figaro import generate_sample_from_description
import torch
import ast
import torch.nn as nn
import os
from torch.utils.data import DataLoader
import torch
from torch import nn
from torch.utils.data import Dataset
import pandas as pd
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



MUSIC_FEATURES = ['danceability', 'energy', 'key',
                  'loudness', 'mode', 'acousticness',
                  'instrumentalness', 'valence',
                  'tempo', 'time_signature']

import ast
import torch.nn.functional as F
from functools import cache
DATASET_PATH = "../dataset/processed_dataset.csv"
df_merged = pd.read_csv(DATASET_PATH)

# Data preparation
class MusicDataset(Dataset):
    def __init__(self, dataframe, description_column, numerical_feature=False, soft_labels=False):
        features = []
        for i in range(len(dataframe.index)):
          row = []
          for feature_name in MUSIC_FEATURES:
            row.append(dataframe.iloc[i][feature_name])
          features.append(row)
        self.features = features
        self.descriptions = [ast.literal_eval(x) for x in dataframe[description_column].values]
        self.numerical = numerical_feature
        self.max_description_length = max([len(x) for x in self.descriptions])
        self.soft_labels = soft_labels

        print(f"Max length for {description_column}", self.max_description_length)

        if not self.numerical:
          token_list = set(token for desc in self.descriptions for token in desc)
          if self.soft_labels:
            token_list = sorted(token_list, key=lambda x: int(x.split("_")[-1]))
          print(token_list)
          self.vocab = {token: i for i, token in enumerate(token_list, start=1)}
          self.vocab['<PAD>'] = 0  # Add a padding token

          print(f"Vocab size for {description_column}", len(self.vocab))

          self.vocab_inv = {i: token for token, i in self.vocab.items()}

    def __len__(self):
        return len(self.descriptions)

    @cache
    def __getitem__(self, idx):
        feature = torch.tensor(self.features[idx], dtype=torch.float32)
        if self.numerical:
          description = [int(x.split('_')[-1]) for x in self.descriptions[idx]]
        else:
          description = [self.vocab[token] for token in self.descriptions[idx]]
        # print("Des", self.descriptions[idx][:15])
        # print("Len", len(description))
        description_tensor = torch.tensor(description + [0]*(self.max_description_length - len(description)), dtype=torch.long)
        # print("Description shape", description_tensor.shape)
        if self.soft_labels:
          description_tensor_soft = self.create_soft_labels(description_tensor, len(self.vocab))
        else:
          description_tensor_soft = torch.zeros(1)
        return feature.to(device), description_tensor.to(device), description_tensor_soft.to(device)

    def create_soft_labels(self, targets, num_classes, smoothing=0.5):
        """
        Creates soft labels using a Gaussian distribution centered at each target label.
        :param targets: tensor of shape [batch_size, seq_length] with integer class labels.
        :param num_classes: total number of classes.
        :param smoothing: controls the spread of the distribution around the class label.
        :return: tensor of shape [batch_size, seq_length, num_classes] with soft labels.
        """
        soft_labels = torch.zeros(targets.shape[0], num_classes, device=targets.device)

        # Create a Gaussian distribution centered at each target label
        for s in range(targets.shape[0]):
            label = targets[s]
            soft_labels[s, max(0, label - 1):min(num_classes, label + 2)] = torch.tensor(
                [smoothing / 2 if i == label - 1 or i == label + 1 else 1.0 - smoothing if i == label else 0 for i in range(max(0, label - 1), min(num_classes, label + 2))],
                device=targets.device
            )

        # Normalize to ensure it's a valid probability distribution
        soft_labels = F.normalize(soft_labels, p=1, dim=1)
        return soft_labels
full_dataset = MusicDataset(df_merged, 'description', numerical_feature=False)
from torch.autograd import Variable


# LSTM Model Configuration
class LSTMModel(nn.Module):
    def __init__(self, vocab_size, numerical=False):
        super().__init__()
        self.embedding_dim = 128
        self.hidden_dim = 256
        self.vocab_size = vocab_size
        self.numerical = numerical
        if not numerical:
          self.embedding = nn.Embedding(self.vocab_size, self.embedding_dim, padding_idx=0)

          self.lstm = nn.LSTM(self.embedding_dim + 10, self.hidden_dim, batch_first=True, num_layers=6)  # +10 for concatenated features
        else:
          self.lstm = nn.LSTM(1 + 10, self.hidden_dim, batch_first=True)  # +10 for concatenated features
        self.fc = nn.Linear(self.hidden_dim, self.vocab_size)

    def forward(self, features, descriptions):
        if self.numerical:
          embeddings = descriptions.unsqueeze(-1)
        else:
          embeddings = self.embedding(descriptions)

        h_0 = Variable(torch.zeros(6, descriptions.shape[0], self.hidden_dim).cuda())
        c_0 = Variable(torch.zeros(6, descriptions.shape[0], self.hidden_dim).cuda())
        # Concatenate features to each input embedding
        features_expanded = features.unsqueeze(1).repeat(1, descriptions.size(1), 1)
        lstm_input = torch.cat((embeddings, features_expanded), dim=2)
        lstm_out, _ = self.lstm(lstm_input, (h_0, c_0))
        logits = self.fc(lstm_out)
        return logits

    def sample(self, features, input, max_len=100):
        h_0 = Variable(torch.zeros(6, 1, self.hidden_dim).cuda())
        c_0 = Variable(torch.zeros(6, 1, self.hidden_dim).cuda())
        features_expanded = features.unsqueeze(0).unsqueeze(0)
        result = []
        input = input.unsqueeze(0).unsqueeze(0).cuda()
        for i in range(max_len):
            # print("h0", h_0)
            if self.numerical:
              embeddings = input.unsqueeze(-1)
            else:
              embeddings = self.embedding(input)
            lstm_input = torch.cat((embeddings, features_expanded), dim=2)
            lstm_out, (new_h_0, new_c_0) = self.lstm(lstm_input, (h_0, c_0))
            h_0 = new_h_0
            c_0 = new_c_0
            logits = self.fc(lstm_out)
            prediction = logits.argmax(-1)
            result.append(prediction.item())
            input = prediction
            # features_expanded = torch.cat((features_expanded, features.unsqueeze(0).unsqueeze(0)), dim=1)
        return result
    
pitch_dataset = MusicDataset(df_merged, 'pitch_description', numerical_feature=False, soft_labels=True)
pitch_lstm = LSTMModel(len(pitch_dataset.vocab), numerical=False).to(device)
pitch_lstm.load_state_dict(torch.load(os.getenv("PITCH_MODEL_PATH")))


density_dataset = MusicDataset(df_merged, 'density_description', numerical_feature=False, soft_labels=True)
density_lstm = LSTMModel(len(density_dataset.vocab), numerical=False).to(device)
density_lstm.load_state_dict(torch.load(os.getenv("DENSITY_MODEL_PATH")))


duration_dataset = MusicDataset(df_merged, 'duration_description', numerical_feature=False, soft_labels=True)
duration_lstm = LSTMModel(len(duration_dataset.vocab), numerical=False).to(device)
duration_lstm.load_state_dict(torch.load(os.getenv("DURATION_MODEL_PATH")))


velocity_dataset = MusicDataset(df_merged, 'velocity_description', numerical_feature=False, soft_labels=True)
velocity_lstm = LSTMModel(len(velocity_dataset.vocab), numerical=False).to(device)
velocity_lstm.load_state_dict(torch.load(os.getenv("VELOCITY_MODEL_PATH")))


categorical_dataset = MusicDataset(df_merged, 'categorical_description', numerical_feature=False, soft_labels=True)
categorical_lstm = LSTMModel(len(categorical_dataset.vocab), numerical=False).to(device)
categorical_lstm.load_state_dict(torch.load(os.getenv("CAT_MODEL_PATH")))
    
def sample(features, dataset, model):
  with torch.no_grad():
    out = model.sample(features, torch.tensor(dataset.vocab["Bar_1"]), max_len=100)
      
    return out.cpu().numpy().tolist()
  
def get_description(features):
    pitch = sample(features, pitch_dataset, pitch_lstm)
    density = sample(features, density_dataset, density_lstm)
    duration = sample(features, duration_dataset, duration_lstm)
    velocity = sample(features, velocity_dataset, velocity_lstm)
    categorical = sample(features, categorical_dataset, categorical_lstm)
    result = []
    for p, d, dur, v, c in zip(pitch, density, duration, velocity, categorical):
        result += [pitch_dataset.vocab_inv[p], density_dataset.vocab_inv[d], duration_dataset.vocab_inv[dur], velocity_dataset.vocab_inv[v], categorical_dataset.vocab_inv[c]]

    return result


def generate_sample(
        danceability: float,
        energy: float,
        valence: float,
        tempo: float,
        acousticness: float,
        instrumentalness: float,
        key: int,
        mode: int,
        time_signature: int,
        uid: str):

    vec = np.array([danceability, energy, key, mode, acousticness, instrumentalness, valence, tempo, time_signature])
    
    # print(prediction[0])

    prediction = get_description(torch.tensor(vec).to(device))

    first_bars = []
    bar = 0
    for x in ast.literal_eval(prediction):
        if 'Bar' in x:
            bar += 1
        if bar == 4:
            break
        first_bars.append(x)
    description = " ".join([f"<{x}>" for x in first_bars])
    print(description)
    generate_sample_from_description(description, uid)
