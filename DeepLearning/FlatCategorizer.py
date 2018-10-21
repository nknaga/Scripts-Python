import sys
import numpy as np
import matplotlib.pyplot as plt
import os
from os.path import join
from os import listdir
os.environ['TF_CPP_MIN_VLOG_LEVEL'] = '3'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from keras import optimizers, regularizers
from keras.models import Model
from keras.layers import Flatten, Dense, Conv2D, Dropout, MaxPooling2D, GaussianNoise, Input
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, EarlyStopping, Callback

import tensorflow as tf
tf.reset_default_graph()
from keras import backend as K
K.image_dim_ordering()

###################### Hyperparameters ######################
#                    Mode paramaters
picSize = (150, 150, 3)

#                    Network parameters
convLayers = ((64, 1), (128, 1), (128, 2),(256, 3),(256, 3))
denseLayers = (512, 256)

#                    Training parameters
batchSize = 64
epochs = 100
learningRate = 1*10**-3
momentum = 0.5
lrDecay = 10**-5  # learning rate decay (not weight decay)
weightDecay = 4*10**-5  # weight decay

class PlotLearning(Callback):
    def on_train_begin(self, logs={}):
        self.i = 0
        self.x = []
        self.losses, self.val_losses = [], []
        self.acc, self.val_acc = [], []
        self.logs = []

    def on_epoch_end(self, epoch, logs={}):
        self.logs.append(logs)
        self.x.append(self.i)
        self.losses.append(logs.get('loss'))
        self.val_losses.append(logs.get('val_loss'))
        self.acc.append(logs.get('acc'))
        self.val_acc.append(logs.get('val_acc'))
        self.i += 1
        f, (ax1, ax2) = plt.subplots(1, 2, sharex=True)

        ax1.set_yscale('log')
        ax1.plot(self.x, self.losses, label="Training")
        ax1.plot(self.x, self.val_losses, label="Validation")
        ax1.set_xlabel('Epochs')
        ax1.set_ylabel('Crossentropy')
        ax1.legend()

        ax2.plot(self.x, self.acc, label="Training")
        ax2.plot(self.x, self.val_acc, label="Validation")
        ax2.set_xlabel('Epochs')
        ax2.set_ylabel('Accuracy')
        ax2.legend()

        plt.tight_layout()
        plt.savefig('plot.png')


def ExportSummary(model):
    old = sys.stdout
    with open('currentModel.txt', 'w') as file:
        sys.stdout = file
        model.summary()
        sys.stdout = old
    del model

def PlotConfuse(labels, confuse):
    labels = np.array(labels)

    # Plot the matrix
    fig, ax = plt.subplots(1,1)
    img = ax.imshow(confuse,cmap='viridis', interpolation='nearest')
    fig.colorbar(img, ax=ax)

    # Write the labels  and titles
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xticks(list(range(len(labels))))
    ax.set_yticks(list(range(len(labels))))
    plt.xlabel('Predicted')
    plt.ylabel('Reality')
    plt.tight_layout()
    plt.show()


def ImportModel(labels, weightPath=False):
    inputLayer = Input(shape = picSize)

    first = True
    for size, number in convLayers:
        for i in range(number):
            if first:
                x = Conv2D(size, (3,3), activation='relu', padding='same')(inputLayer)
                first = False
            else:
                x = Conv2D(size, (3,3), activation='relu', padding='same')(x)
        x = MaxPooling2D((2,2), strides=(2, 2))(x)
    x = GaussianNoise(0.01, name='gaussianNoise')(x)
    x = Flatten(name='flatten')(x)

    for nodes in denseLayers:
        x = Dense(nodes, kernel_regularizer=regularizers.l2(weightDecay), activation='relu')(x)
        x = Dropout(0.5)(x)
    x = Dense(labels, activation='softmax')(x)
    model = Model(inputs=inputLayer, outputs=x)

    sgd = optimizers.SGD(lr=learningRate,momentum=momentum,decay=lrDecay, nesterov=True)
    model.compile(optimizer = sgd, loss='categorical_crossentropy', metrics=['accuracy'])

    if weightPath:
        print('load', weightPath)
        model.load_weights(weightPath)
    return model

def Train(folder, weightPath, labels):
    model = ImportModel(labels)
    trainDatagen = ImageDataGenerator(rotation_range=30,
                                      zoom_range=(0.75, 1.25),
                                      fill_mode='constant',
                                      cval=0)
    trainGen = Flow(join(folder, 'train'), dataGen=trainDatagen)

    valGen = Flow(join(folder, 'validation'))

    ExportSummary(model)
    calls = [ModelCheckpoint(weightPath, save_best_only=True),
             EarlyStopping(monitor='val_loss', patience=15),
             PlotLearning()]
    model.fit_generator(trainGen, epochs=epochs, verbose=1,
                        callbacks=calls,
                        steps_per_epoch=200,
                        validation_data=valGen,
                        validation_steps=20)

def Test(weightPath, folder, labels):
    confuse = []
    confuse = [[0 for x in range(labels)] for y in range(labels)]
    model = ImportModel(labels, weightPath=weightPath)
    TestGen = Flow(join(folder, 'test'))
    t = 0
    errors = []
    labelsName = listdir(join(folder, 'test'))
    while t < 500:
        Progress(f"{t}\\5000")
        x32, y32 = next(TestGen)
        z32 = model.predict(x32)
        for y, z in zip(y32, z32):
            ymax = np.argmax(y)
            zmax = np.argmax(z)
            confuse[ymax][zmax]+=1
            errors.append((x32[t%32], zmax))
            t+=1
    for i in range(len(confuse)):
        confuse[i]/=np.sum(confuse[i])
    print('success rate: ',round(sum([confuse[i][i] for i in range(len(confuse))])/len(confuse), 3))
    PlotConfuse(labelsName, confuse)

    plt.figure()
    nb=5
    k = 0
    for i in range(nb):
        for j in range(nb):
            if k >= len(errors):
                break
            im, label = errors[k]
            plt.subplot(nb,nb,k+1)
            image = im.astype(int)
            plt.title(labelsName[np.argmax(label)])
            plt.axis('off')
            plt.imshow(image)
            k += 1
    plt.show()


def Flow(folder, dataGen=False):
    if not dataGen:
        dataGen = ImageDataGenerator(fill_mode='constant', cval=0)
    return dataGen.flow_from_directory(folder,
                                       color_mode = 'rgb',
                                       target_size=picSize[:2],
                                       batch_size=batchSize,
                                       class_mode='categorical',
                                       interpolation='bicubic')

def Progress(s):
    sys.stdout.write('\r')
    sys.stdout.write(s+'           ')
    sys.stdout.flush()

if __name__ == '__main__':
    mode =  'train'
    name = 'flatCat'
    folder = join('imgs', name)
    weightPath = join('models', name +'.h5')
    labels = len(listdir(join(folder, 'train')))

    if mode == 'train':
        Train(folder, weightPath, labels)
    elif mode == 'test':
        Test(weightPath, folder, labels)
