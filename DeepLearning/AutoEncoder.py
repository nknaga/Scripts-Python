# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 12:24:51 2018

@author: Rignak
"""
from os import walk
from os.path import join, split
from datetime import datetime
import sys
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import math

from keras.preprocessing import image as image_utils
from keras import optimizers, regularizers
from keras.models import Sequential
from keras.layers import Flatten, Dense, Conv2D, Dropout, MaxPooling2D, Reshape, UpSampling2D
from keras.callbacks import ModelCheckpoint, EarlyStopping, Callback
from keras.preprocessing.image import ImageDataGenerator

picSize = (128, 128, 3)
epochs = 30
batchSize = 32
learningRate = 5*10**-3
momentum = 0.9
lrDecay = 10**-5  # learning rate decay (not weight decay)
weightDecay = 4*10**-5  # weight decay
activation = 'relu'



weightPath = join("models", 'autoencoder.h5')
import os
os.environ['TF_CPP_MIN_VLOG_LEVEL'] = '3'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


import tensorflow as tf
tf.reset_default_graph()
from keras import backend as K
K.image_dim_ordering()

class PlotLearning(Callback):
    """Callback generating a fitness plot in a file after each epoch"""
    def on_train_begin(self, logs={}):
        self.i = 0
        self.x = []
        self.losses = []
        self.val_losses = []
        self.logs = []

    def on_epoch_end(self, epoch, logs={}):
        self.logs.append(logs)
        self.x.append(self.i)
        self.losses.append(logs.get('loss'))
        self.val_losses.append(logs.get('val_loss'))
        self.i += 1

        plt.figure()
        plt.yscale('log')
        plt.plot(self.x, self.losses, label="Training")
        plt.plot(self.x, self.val_losses, label="Validation")
        plt.xlabel('Epoch')
        plt.ylabel('binary_crossentropy')
        plt.legend()


        plt.tight_layout()
        plt.savefig('plot.png')

def ImportModel(weight):
    convBloc = [(64,2), (128,2), (256,2), (256,3), (512,3)]
    convSize = (3, 3)
    pooling = (math.ceil(convSize[0]/2), math.ceil(convSize[1]/2))
    endSize = int(picSize[0]/pooling[0]**len(convBloc))
    reshapeSize =  (endSize, endSize, convBloc[-1][0])
    denseLayers = [128, np.prod(reshapeSize)]
    a = activation
    p = 'same'
    reg = regularizers.l2(weightDecay)

    model = Sequential()

    # Down convolutions
    for i, (layer, jmax) in enumerate(convBloc):
        for j in range(jmax):
            if i == 0 and j == 0:
                model.add(Conv2D(layer, convSize, input_shape = picSize, activation=a, padding=p))
            else:
                model.add(Conv2D(layer, convSize, activation=a, padding=p))
        model.add(MaxPooling2D(pooling))

    # Dense layers
    model.add(Flatten(name='flatten'))
#    for j, layer in enumerate(denseLayers):
#        model.add(Dense(layer, kernel_regularizer=reg, activation=a))
#        if j != len(denseLayers)-1:
#            model.add(Dropout(0.5))
    model.add(Reshape(reshapeSize))

    # Up convolutions
    for i, (layer, jmax) in enumerate(convBloc[::-1]):
        for j in range(jmax):
            model.add(Conv2D(layer, convSize, activation=a, padding=p))
        model.add(UpSampling2D(pooling))

    model.add(Conv2D(picSize[2], convSize, activation=a, padding=p))

    sgd = optimizers.SGD(lr=learningRate,momentum=momentum,decay=lrDecay,
                         nesterov=True)
    model.compile(optimizer = sgd, loss='binary_crossentropy')
    if weight:
        print('load weights')
        model.load_weights(weightPath)

    with open('currentModel.txt', 'w') as file:
        old = sys.stdout
        sys.stdout = file
        model.summary()
        sys.stdout = old

    return model


def ExportSummary(model):
    old = sys.stdout
    with open('currentModel.txt', 'w') as file:
        sys.stdout = file
        model.summary()
        sys.stdout = old


def Progress(s):
    sys.stdout.write('\r')
    sys.stdout.write(s+'           ')
    sys.stdout.flush()


def ListFilesRec(folder):
    resFiles = []
    for root, dirs, files in walk(folder):
        for file in files:
            if file.endswith('.png'):
                resFiles.append(join(root, file))
    print(len(resFiles))
    #resFiles.sort(key =lambda z:int(z.split('(')[1].split(')')[0]))
    return resFiles


def Train(folder):
    model = ImportModel(False)
    print(folder)
    trainDatagen = ImageDataGenerator(rotation_range=20,
                                       zoom_range=(0.8, 1.2),
                                       horizontal_flip=True,
                                       fill_mode='reflect')
    TrainGen = trainDatagen.flow_from_directory(folder,
                                                color_mode = 'rgb',
                                                target_size=picSize[:2],
                                                batch_size=batchSize,
                                                class_mode='input',
                                                interpolation='bicubic')

    ExportSummary(model)
    calls = [ModelCheckpoint(weightPath, save_best_only=True),
             EarlyStopping(monitor='val_loss', patience=15),
             PlotLearning()]

    model.fit_generator(TrainGen, epochs=epochs, verbose=1,
                        callbacks=calls,
                        steps_per_epoch=100,
                        validation_data=TrainGen,
                        validation_steps=5)

def Apply(folder):
    model = ImportModel(True)
    testDatagen = ImageDataGenerator(rotation_range=20,
                                     zoom_range=(0.8, 1.2),
                                     horizontal_flip=True,
                                     fill_mode='reflect')
    TestGen = testDatagen.flow_from_directory(folder,
                                              color_mode = 'rgb',
                                              target_size=picSize[:2],
                                              batch_size=2,
                                              class_mode='input',
                                              interpolation='bicubic')

    x, y = next(TestGen)
    z = model.predict(x)
    for i in range (0,1):
        image = x[i].astype(int)
        plt.subplot(1,2,1)
        plt.imshow(image)

        plt.subplot(1,2,2)
        res = z[i].astype(int)
        plt.imshow(res)
        plt.show()

if __name__ == '__main__':
    folder = join('.', 'imgs', 'fav-rignak')
    if len(sys.argv) == 2:
        mode = sys.argv[1]
    else:
        mode = '1'

    if mode == '1':
        Apply(folder)
    elif mode == '2':
        Train(folder)
