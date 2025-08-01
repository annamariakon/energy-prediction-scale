import torch.nn as nn

# Create class instance of the neural network (2 hidden layers)
class NeuralNet_2(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, output_size):
        super(NeuralNet_2, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size1)  # First hidden layer
        self.relu1 = nn.ReLU()                         # Activation function
        self.fc2 = nn.Linear(hidden_size1, hidden_size2)  # Second hidden layer
        self.relu2 = nn.ReLU()                         # Activation function
        self.output = nn.Linear(hidden_size2, output_size)  # Output layer

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.output(x)
        return x