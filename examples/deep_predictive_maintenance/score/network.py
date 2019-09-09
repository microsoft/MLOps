
import torch 
import torch.nn as nn

class Network(nn.Module):
    
    def __init__(self,batch_size,input_size, 
                 hidden_size, nb_layers, dropout):
        super(Network, self).__init__()
        
        
        self.hidden_size = hidden_size
        self.nb_layers = nb_layers
        self.rnn = nn.LSTM(input_size, hidden_size, 
                           nb_layers, batch_first=True,
                           dropout = dropout)
        self.fc = nn.Linear(hidden_size, 2)
        self.activation = nn.ReLU()
        self.softmax = nn.LogSoftmax()
        
    
    def forward(self, sequence):
        
        out,_ = self.rnn(sequence)
        out = self.activation(out)
        out = self.fc(out[:, -1, :])
        likelihood = self.softmax(out)
        return out, likelihood