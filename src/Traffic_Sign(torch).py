# -*- coding: utf-8 -*-
"""Untitled8.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AL4Yw4hUscgd9XSQVu0iqHpEhD2yK4j7
"""

import torch, torchvision
from torch import nn
from torch import optim
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt
import torch.nn.functional as F

#drive for colab
from google.colab import drive
drive.mount('/gdrive')

#parameters
train_batch = 6 
test_batch = 3
lr = 0.01
momentum = 0.3
nb_epoch = 20
input_size = 28*28
hidden_layers = 100
log_interval = 5
random_seed = 69
torch.backends.cudnn.enabled = False
torch.manual_seed(random_seed)

#parameters 60% CC
train_batch = 4
test_batch = 2
lr = 0.05
momentum = 0.3
nb_epoch = 35
input_size = 28*28
hidden_layers = 100
log_interval = 5
random_seed = 69
torch.backends.cudnn.enabled = False
torch.manual_seed(random_seed)

#path for image folder
Train_Dataset_Path = r"/gdrive/My Drive/Signs/dataset_crop"
Test_Dataset_Path = r"/gdrive/My Drive/Signs/dataset_crop"

train_transforms = torchvision.transforms.Compose([ torchvision.transforms.GaussianBlur(5,5), torchvision.transforms.Grayscale(), torchvision.transforms.Resize((28,28)),torchvision.transforms.ToTensor()])
train_dataset = torchvision.datasets.ImageFolder(root = Train_Dataset_Path, transform = train_transforms) #imagefolder attribute converts folders with images to datasets
test_dataset = torchvision.datasets.ImageFolder(root = Test_Dataset_Path, transform = train_transforms)

#Train and Test loaders
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size = train_batch, shuffle = True, num_workers = 2)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size = test_batch, shuffle = True, num_workers = 2)

train_dataset[1][0].shape

checkdata = iter(train_loader)
img, label = next(checkdata)

img.size()

for i in range(2):
  print(label[i])
  plt.subplot(1,2,i+1)
  plt.title(label[i].numpy())
  plt.imshow(img[i][0], cmap = "gray")

#network classes
class myNetwork(nn.Module):
    def __init__(self):
        super(myNetwork, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, kernel_size=5)
        self.conv2 = nn.Conv2d(20, 40, kernel_size=5)
        self.conv2_drop = nn.Dropout2d(p = 0.5)
        self.fc1 = nn.Linear(40*4*4, 50)
        self.fc2 = nn.Linear(50, 16)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop( self.conv2(x)), 2))
        # print(x.shape)
        x = x.view(x.size(0), 40*4*4)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x)

# #network classes
# class myNetwork(nn.Module):
#     def __init__(self):
#         super(myNetwork, self).__init__()
#         self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
#         self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
#         self.conv2_drop = nn.Dropout2d(p = 0.5)
#         self.fc1 = nn.Linear(20*4*4, 50)
#         self.fc2 = nn.Linear(50, 16)

#     def forward(self, x):
#         x = F.relu(F.max_pool2d(self.conv1(x), 2))
#         x = F.relu(F.max_pool2d(self.conv2_drop( self.conv2(x)), 2))
#         # print(x.shape)
#         x = x.view(x.size(0), 20*4*4)
#         x = F.relu(self.fc1(x))
#         x = F.dropout(x, training=self.training)
#         x = self.fc2(x)
#         return F.log_softmax(x)

#initializg network object and optimizing
signnetwork = myNetwork()
optimizer = optim.SGD(signnetwork.parameters(), lr=lr,
                      momentum=momentum)
# arrays/list to store losses
train_losses = []
train_counter = []
test_losses = []
test_counter = [i*len(train_loader.dataset) for i in range(nb_epoch + 1)]

#training function
def train(epoch):
  signnetwork.train()
  for batch_idx, (data, target) in enumerate(train_loader):
    optimizer.zero_grad()
    output = signnetwork(data)
    loss = F.nll_loss(output, target)   #loss fucntion
    loss.backward()
    optimizer.step()                    #optimizing
    if batch_idx % log_interval == 0:
      print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
        epoch, batch_idx * len(data), len(train_loader.dataset),
        100. * batch_idx / len(train_loader), loss.item()))
      train_losses.append(loss.item())
      train_counter.append(
        (batch_idx*64) + ((epoch-1)*len(train_loader.dataset)))
      #saving models

#test function
def test():
  #setting to eval
  signnetwork.eval()
  test_loss = 0
  correct = 0
  with torch.no_grad():
    for data, target in test_loader:
      output = signnetwork(data)
      test_loss += F.nll_loss(output, target, size_average=False).item()  #loss function
      pred = output.data.max(1, keepdim=True)[1]
      correct += pred.eq(target.data.view_as(pred)).sum()
  test_loss /= len(test_loader.dataset)
  test_losses.append(test_loss)
  print('\nTest set: Avg. loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
    test_loss, correct, len(test_loader.dataset),
    100. * correct / len(test_loader.dataset)))

#training the model for 100 epochs even though we get the accuracy needed in 30 epochs
test()
for epoch in range(1, nb_epoch+1):
  train(epoch)
  test()

test_image = enumerate(test_loader)
batch_number, (image, labels) = next(test_image)