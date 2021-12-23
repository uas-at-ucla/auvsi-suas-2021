import torch
import torch.nn as nn
import torch.nn.functional as F
from torchsummary import summary


class ShapeColorClassifier(nn.Module):

    """
    Class representing the ML model that will be used to classify the color of AUVSI SUAS shapes.
    The model's architecture was implemented from the following paper: https://arxiv.org/pdf/1510.07391.pdf
    - The paper used this model's architecture to identify the color of cars. We could train it to identify AUVSI SUAS object colors.
    - Model Input: RGB images of dimension (227 x 227).
    - Model Output: Tensor with 8 features, which represents the probability of the following 8 colors being in the car image:
        1. Green
        2. Red
        3. White
        4. Yellow
        5. Black
        6. Blue
        7. Cyan
        8. Gray
    - Authors stated that they achieved an average accuracy of 94.47% during testing.

    We can increase the number of colors the model can identify by changing the output of the final fully-connected layer.
    
    We cannot increase the resolution of the input images without changing the kernel size/stride of the convolution and maxpool layers.
    - However, we could use a superresolution model to upscale the image and then resize to a lower size. This ensures the smaller image is of good quality.
    """

    def __init__(self, num_colors=8):
        super(ShapeColorClassifier, self).__init__()

        #### ReLU activation function was used for ALL layers, including fully-connected layers ####
        """
        Model Input: PyTorch Tensor representing a batch of RGB images.
            Shape = [Number of Imgs in Batch, Number of Channels in Image, Width, Height]

        Layer ordering:
        1. Conv2d
        2. Activation
        3. MaxPool
        4. Other (batch norm...)

        ReLU activation function was used for ALL layers, including fully-connected layers

        Normalization process used the following values (a = 10^-4, B = 0.75, and n = 5)
        """

        #### FOR TOP LAYER ####
        # Conv2d with BatchNorm2d and MaxPool2d size (3x3) and stride 2.
        self.top_conv1 = nn.Sequential(nn.Conv2d(in_channels=3, out_channels=48, kernel_size=(11, 11), stride=4),
                                        nn.ReLU(),
                                        nn.BatchNorm2d(num_features=48),
                                        nn.MaxPool2d(kernel_size=(3, 3), stride=2))
        self.top_conv2_p1 = nn.Sequential(nn.Conv2d(in_channels=48, out_channels=64, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU(),
                                            nn.BatchNorm2d(num_features=64),
                                            nn.MaxPool2d(kernel_size=(3, 3), stride=2))
        self.top_conv2_p2 = nn.Sequential(nn.Conv2d(in_channels=48, out_channels=64, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU(),
                                            nn.BatchNorm2d(num_features=64),
                                            nn.MaxPool2d(kernel_size=(3, 3), stride=2))
        
        # Before conv3, we will be doing a channel concatenation based on the tensors returned from top_conv2_p1 and top_conv2_p2.
        # This means the input channel for this layer would be 128; from the output channels of the two top_conv2 layers, 64 + 64 = 128
        self.top_conv3 = nn.Sequential(nn.Conv2d(in_channels=128, out_channels=192, kernel_size=(3, 3), stride=1, padding=1),
                                        nn.ReLU())

        self.top_conv4_p1 = nn.Sequential(nn.Conv2d(in_channels=192, out_channels=96, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU())
        self.top_conv4_p2 = nn.Sequential(nn.Conv2d(in_channels=192, out_channels=96, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU())

        self.top_conv5_p1 = nn.Sequential(nn.Conv2d(in_channels=96, out_channels=64, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU(),
                                            nn.MaxPool2d(kernel_size=(3, 3), stride=2))
        self.top_conv5_p2 = nn.Sequential(nn.Conv2d(in_channels=96, out_channels=64, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU(),
                                            nn.MaxPool2d(kernel_size=(3, 3), stride=2))

        #### FOR BOTTOM LAYER ####
        self.bot_conv1 = nn.Sequential(nn.Conv2d(in_channels=3, out_channels=48, kernel_size=(11, 11), stride=4),
                                        nn.ReLU(),
                                        nn.BatchNorm2d(num_features=48),
                                        nn.MaxPool2d(kernel_size=(3, 3), stride=2))
        self.bot_conv2_p1 = nn.Sequential(nn.Conv2d(in_channels=48, out_channels=64, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU(),
                                            nn.BatchNorm2d(num_features=64),
                                            nn.MaxPool2d(kernel_size=(3, 3), stride=2))
        self.bot_conv2_p2 = nn.Sequential(nn.Conv2d(in_channels=48, out_channels=64, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU(),
                                            nn.BatchNorm2d(num_features=64),
                                            nn.MaxPool2d(kernel_size=(3, 3), stride=2))
        
        # Before conv3, we will be doing a channel concatenation based on the tensors returned from bot_conv2_p1 and bot_conv2_p2.
        # This means the input channel for this layer would be 128; from the output channels of the two bot_conv2 layers, 64 + 64 = 128
        self.bot_conv3 = nn.Sequential(nn.Conv2d(in_channels=128, out_channels=192, kernel_size=(3, 3), stride=1, padding=1),
                                        nn.ReLU())

        self.bot_conv4_p1 = nn.Sequential(nn.Conv2d(in_channels=192, out_channels=96, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU())
        self.bot_conv4_p2 = nn.Sequential(nn.Conv2d(in_channels=192, out_channels=96, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU())

        self.bot_conv5_p1 = nn.Sequential(nn.Conv2d(in_channels=96, out_channels=64, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU(),
                                            nn.MaxPool2d(kernel_size=(3, 3), stride=2))
        self.bot_conv5_p2 = nn.Sequential(nn.Conv2d(in_channels=96, out_channels=64, kernel_size=(3, 3), stride=1, padding=1),
                                            nn.ReLU(),
                                            nn.MaxPool2d(kernel_size=(3, 3), stride=2))

        #### Fully-Connected Layer ####
        # Employed dropout regularization
        self.classifier = nn.Sequential(nn.Linear(in_features=(6 * 6 * 64 * 4), out_features=4096), nn.ReLU(), nn.Dropout(0.7),  # (6*6*64*4) gives us the total number of features from the 4 outputs given by top and bottom conv5 layer.
                                        nn.Linear(in_features=4096, out_features=4096), nn.ReLU(), nn.Dropout(0.6),
                                        nn.Linear(in_features=4096, out_features=num_colors)) # In this final fully-connected layer, 8 features are outputted to represent classification of 8 colors.

        # Remember to apply a softmax to classifier output in forward()

    def forward(self, input):
        # Calculations
        
        #### TOP LAYER ####
        out_top_conv1 = self.top_conv1(input)
        out_top_conv2 = torch.cat(tensors=(self.top_conv2_p1(out_top_conv1), self.top_conv2_p2(out_top_conv1)), dim=1) 
        out_top_conv3 = self.top_conv3(out_top_conv2)

        # Conv4
        out_top_conv4_p1 = self.top_conv4_p1(out_top_conv3)
        out_top_conv4_p2 = self.top_conv4_p2(out_top_conv3)
        
        # Conv5 (Final output from Convolutions before fully-connected layers)
        out_top_conv5_p1 = self.top_conv5_p1(out_top_conv4_p1)
        out_top_conv5_p2 = self.top_conv5_p2(out_top_conv4_p2)

        #### BOTTOM LAYER ####
        out_bot_conv1 = self.bot_conv1(input)
        out_bot_conv2 = torch.cat(tensors=(self.bot_conv2_p1(out_bot_conv1), self.bot_conv2_p2(out_bot_conv1)), dim=1)
        out_bot_conv3 = self.bot_conv3(out_bot_conv2)

        # Conv4
        out_bot_conv4_p1 = self.bot_conv4_p1(out_bot_conv3)
        out_bot_conv4_p2 = self.bot_conv4_p2(out_bot_conv3)

        # Conv5
        out_bot_conv5_p1 = self.bot_conv5_p1(out_bot_conv4_p1)
        out_bot_conv5_p2 = self.bot_conv5_p2(out_bot_conv4_p2)

        #### Concatenation before fully-connected layers ####
        out_cat = torch.cat(tensors=(out_top_conv5_p1, out_top_conv5_p2, out_bot_conv5_p1, out_bot_conv5_p2), dim=1)    # Channel concatenation from dim=1
        out_flatten = torch.flatten(out_cat, start_dim=1, end_dim=3)


        #### Classification w/ Softmax ####
        classification = self.classifier(out_flatten)
        classification = F.softmax(classification)

        return classification


#test_tensor = torch.randn(size=(1, 3, 227, 227))
#model = ShapeColorClassifier()

#test_output = model(test_tensor)
#print(test_output.shape)

#summary(model, input_size=(3, 227, 227), device='cpu')