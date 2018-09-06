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

picSize = (243, 243, 3)
epochs = 30
batchSize = 16
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
        plt.ylabel('cross entropy')
        plt.legend()
    

        plt.tight_layout()
        plt.savefig('plot.png')
        
def ImportModel(weight):
    convBloc = [(64,1), (128,1), (256,1), (512,1)]
    convSize = (5, 5)
    pooling = (math.ceil(convSize[0]/2), math.ceil(convSize[1]/2))
    endSize = int(picSize[0]/pooling[0]**len(convBloc))
    reshapeSize =  (endSize, endSize, convBloc[-1][0])
    denseLayers = [2048, np.prod(reshapeSize)]
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
    for j, layer in enumerate(denseLayers):
        model.add(Dense(layer, kernel_regularizer=reg, activation=a))
        if j != len(denseLayers)-1:
            model.add(Dropout(0.5))
    model.add(Reshape(reshapeSize))
 
    # Up convolutions  
    for i, (layer, jmax) in enumerate(convBloc[::-1]):
        for j in range(jmax):
            model.add(Conv2D(layer, convSize, activation=a, padding=p))
        model.add(UpSampling2D(pooling))
    
    model.add(Conv2D(3, convSize, activation='sigmoid', padding='same'))

    sgd = optimizers.SGD(lr=learningRate,momentum=momentum,decay=lrDecay,
                         nesterov=True)
    model.compile(optimizer = sgd, loss='mean_squared_error')
    if weight:
        print('load weights')
        model.load_weights(weightPath)
            
    with open('currentModel.txt', 'w') as file:
        old = sys.stdout
        sys.stdout = file
        model.summary()
        sys.stdout = old
        
    return model
    
    
def Progress(s):
    sys.stdout.write('\r')
    sys.stdout.write(s+'           ')
    sys.stdout.flush()
    
def PrepareImage(file):
    img = image_utils.load_img(file, target_size=picSize[:2], grayscale=False,
                               interpolation='bicubic')
    x = image_utils.img_to_array(img)
    x = np.expand_dims(x, axis=0)/255
    return x
        
def PrepareImages(files):
    inputs = []
    begin = datetime.now()
    l = len(files)
    for i, file in enumerate(files):
        eta = ((datetime.now()-begin)/(i+1)*l+begin).strftime('%H:%M')
        Progress(str(i)+'/'+str(l)+' - '+eta)

        x = PrepareImage(file)
        inputs.append(x[0])
    print()
    inputs = np.array(inputs)
    return inputs
    
def ListFilesRec(folder):
    resFiles = []
    for root, dirs, files in walk(join('.', 'imgs', folder)):
        for file in files:
            if file.endswith('.jpg'):
                resFiles.append(join(root, file))
    resFiles.sort(key =lambda z:int(z.split('(')[1].split(')')[0]))
    return resFiles
    

def Train(inputs):
    model = ImportModel(False)
    calls = [ModelCheckpoint(weightPath, save_best_only=True),
             EarlyStopping(monitor='val_loss', patience=15),
             PlotLearning()]

    model.fit(epochs=epochs, verbose=1, validation_split = 0.1,
              x=inputs, y=inputs, batch_size = batchSize, 
              callbacks=calls)
              
def Apply(files):
    model = ImportModel(True)
    begin = datetime.now()
    l = len(files)
    for i, file in enumerate(files):
        x = PrepareImage(file)
        pred = model.predict(x)

        im = image_utils.array_to_img(pred[0])
        im.save(join('results', split(file)[-1]))
        
        im = image_utils.array_to_img(x[0])
        im.save(join('results', split(file)[-1][:-4]+'_source'+'.jpg'))
        
        eta = ((datetime.now()-begin)/(i+1)*l+begin).strftime('%H:%M')
        Progress(str(i)+'/'+str(l)+' - '+eta)
    print()
        
if __name__ == '__main__':
    if len(sys.argv) == 2:
        mode = sys.argv[1]
    else:
        mode = '1'
    
    files = ListFilesRec('fav-rignak')[:]
    if mode == '1':
        Apply(files[:20])
    elif mode == '2':
        inputs = PrepareImages(files)
        Train(inputs)
    