import sys
#from sortedcontainers import SortedDict
import numpy as np
import matplotlib.pyplot as plt
from os.path import join, exists
from datetime import datetime
from os import listdir, walk, makedirs
from glob import glob
import colorsys
import random
from keras.preprocessing import image as image_utils
from keras import backend as K
from keras import optimizers, regularizers
from keras.models import Sequential, load_model
from keras.layers import Flatten, Dense, Conv2D, Dropout, MaxPooling2D
from keras.callbacks import ModelCheckpoint, Callback
from random import shuffle
import tensorflow as tf
from bct import modularity_und as SortConfusionMatrix

### Hyperparameters ###
name = 'illustrations'
mode = 'test'  # train, test or testH
modelType = 1  # 1 flat, 2 folder, 3 binary
modelIndex = 0

trainNumPic = 8000 # Number of picture per label on which train
                   # if > 1000, will be the total number of images
testNumPic = 400 # Number of picture per label on which test

batchSize = 32
picSize = (128, 128, 3)
validationSplit = 0.1  # Percentage of picture used for validation during train
epochs = 120
learningRate = 1*10**-3
momentum = 0.5
decay = 10**-6
regularizersRate = 4*10**-5
dropOut = 0.5
threshold = 1
grayscale = picSize[-1]==1
#######################
if not exists('models'):
    makedirs(join('models'))
if not exists(join('models', name)):
    makedirs(join('models', name))
    

class PlotLearning(Callback):
    """Callback generating a fitness plot in a file after each epoch"""
    def on_train_begin(self, logs={}):
        self.i = 0
        self.x = []
        self.losses = []
        self.val_losses = []
        self.acc = []
        self.val_acc = []
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
        ax1.plot(self.x, self.losses, label="loss")
        ax1.plot(self.x, self.val_losses, label="val_loss")
        ax1.legend()

        ax2.plot(self.x, self.acc, label="accuracy")
        ax2.plot(self.x, self.val_acc, label="validation accuracy")
        ax2.legend()

        plt.savefig('plot.png')

class Model():
    def __init__(self, labels, name, files, folder):
        """Initialization of the model
        
        Input:
        labels -- a list of str
        name -- a string
        files -- a list of list of str
            files[i] -- the list of namefile for labels[i]
        folder -- a string
        """
        self.labels = labels
        self.files = files
        self.name = name
        self.folder = folder

        self.flatFiles = FlattenList(self.files)

#        print()
#        print('name:', self.name)
#        print('labels:', self.labels)
#        print('files:', self.files)

    def ExportSummary(self):
        """Write the model in a .txt"""
        old = sys.stdout
        model = self.ImportModel(False)
        with open('currentModel.txt', 'w') as file:
            sys.stdout = file
            model.summary()
            sys.stdout = old
        del model

    def PrepareData(self):
        """Prepare the input and output of the model
        
        Output: 
        output -- 2d array of int (1 or 2)
            output[i] -- an array with 1 if label[i] correspond to the file, 0 else
        input -- an array containing the images"""
        if trainNumPic > 1000:
            self.files = [files[:trainNumPic//len(self.files)] for files in self.files]
        else:
            self.files = [files[:trainNumPic] for files in self.files]
            
        self.files = [files[:trainNumPic] for files in self.files]
        self.flatFiles = FlattenList(self.files)
        output = [[int(file in files) for file in self.flatFiles] for files in self.files]
        input_ = []
        begin = datetime.now()
        for i, file in enumerate(self.flatFiles):
            eta = ((datetime.now()-begin)/(i+1)*len(self.files)+begin).strftime('%H:%M')
            Progress(str(i)+'/'+str(len(self.flatFiles))+' - '+eta)

            x = PrepareImage(file)
            input_.append(x[0])
        output = np.transpose(np.array(output))
        input_ = np.array(input_)
        c = list(range(len(output)))
        shuffle(c)
        self.output = np.array([output[i] for i in c])
        self.input = np.array([input_[i] for i in c])

        
    def Train(self, resume=0):
        """Launch the training of the model
        
        Input:
        resume -- an int
            change the value to continue a previously stopped training
        """
        begin = datetime.now()
        if resume:
            weight = join("models", self.folder, self.name+".h5")
            model = load_model(weight)
        else:
            model = self.ImportModel(False)
        call = ModelCheckpoint(join("models", self.folder, self.name+".h5"))
        model.fit(epochs=epochs, verbose=1, validation_split = validationSplit,x=self.input, y=self.output,
                  batch_size = batchSize, callbacks=[call, PlotLearning()], initial_epoch = resume)
        print('time needed:', datetime.now()-begin)


    def TestModel(self):
        """Launch the model for tests and compute plots and stats"""
        k = 1
        res = {}
        confuse = [[0 for x in self.labels] for y in self.labels]
        begin = datetime.now()
        undecided = 0
        limit = len(self.files)*testNumPic
        for files, label in zip(self.files, self.labels):
            decided = 0
            if len(files) != 0:
                res[label] = 0
            for i, file in enumerate(files[::-1]): # Reverse makes more probable to not use the training picts
                if i > testNumPic:
                    continue
                try:
                    r = self.Recognize(file)
                    labelMax,p = getMaxTuple(r)
                    if threshold < p:  # We don't decide
                        undecided += 1
                    else:  # We decide something
                        decided += 1
                        confuse[self.labels.index(labelMax)][self.labels.index(label)] += 1
                        if label == labelMax:  # Our prediction is correct
                            res[label] += 1
                    ending = (datetime.now() - begin) / k  * limit + begin
                    Progress(str(k) +'\\' +str(limit) + " | " +  ending.strftime('%H:%M'))
                    k+=1
                    #print('\\'.join(file.split('\\')[3:]), 'detected as', labelMax, p)
                except Exception as e:
                    print(e)
                    k+=1
            if decided:
                res[label]/=decided
                for labelMax in self.labels:
                    confuse[self.labels.index(labelMax)][self.labels.index(label)] /= decided
            else:
                res[label] = 1
                for labelMax in self.labels:
                    confuse[self.labels.index(labelMax)][self.labels.index(label)] = 1

        print()
        return res, confuse, undecided/limit

    def Test(self):
        """Launch the model for tests and print plots and stats"""
        self.LoadModel()
        res, confuse, undecided = self.TestModel()
        for label, success in res.items():
            print(label, ':', success)
        res = np.mean([confuse[i][i] for i in range(len(confuse))])
        print('overall succes:', res)
        print('undecided:', undecided)
        self.PlotConfuse(confuse)

    
    def PlotConfuse(self, confuse):
        """Plot the confusion matrix and cluster the labels
        
        Input:
        confuse -- a 2d-matrix of float
            confuse[i][j] -- %age of label[j] being decided as label[i]"""
        # Sort the confusion matrix to make clusters
            # 1/ Get the index
        ci = SortConfusionMatrix(confuse)[0]
        c = [(ci[i], i) for i in range(len(ci))]
        c.sort()
        p = [c[i][1] for i in range(len(c))]
        
            # 2/ Actually sort
        confuse = np.array(confuse)[p][:,p]
        labels = np.array(self.labels)[p]

        # Plot the matrix
        fig, ax = plt.subplots(1,1)
        img = ax.imshow(confuse,cmap='RdYlGn')
        fig.colorbar(img, ax=ax)
        # Plot the frontier between clusters
        for i in range(1, len(c)):
            if c[i][0] != c[i-1][0]:
                ax.axhline(i-0.5)
                ax.axvline(i-0.5)
        
        # Write the labels  and titles
        ax.set_xticklabels(labels, rotation=40, ha="right")
        ax.set_yticklabels(labels)
        ax.set_xticks(list(range(len(labels))))
        ax.set_yticks(list(range(len(labels))))
        plt.xlabel('Predicted')
        plt.ylabel('Reality')
        plt.title(self.name)
        plt.tight_layout()

        plt.show()

    def LoadModel(self):
        """Load the model with weigth"""
        weight = join("models", self.folder, self.name+".h5")
        self.model = self.ImportModel(weight)
        
    def Recognize(self, file):
        """Launch the model on one image
        
        Input:
        file -- a string, the namefile of the image
        
        Output:
            res -- a list of tuple
                res[i] -- a tuple (str, float) where str is a label"""
        x = PrepareImage(file)
        preds = self.model.predict(x)
        preds = preds[0]
        res = []
        for i in range(len(self.labels)):
            res.append((self.labels[i], preds[i]))


        return res

    def ImportModel(self, weight, input_shape = picSize):
        """Create a model
        
        Input:
        weight -- False or a string
            False: the model is loaded without weight
            string: the filename of the model, which will be uesd to load the weigth
        input_shape -- (int, int, int), the dimension of one image
        
        Output:
        modelD - a keras model"""
        modelD = Sequential()
        # Block 1
        modelD.add(Conv2D(64, (3, 3), input_shape = input_shape, activation='relu', padding='same', name='block1_conv1'))
        modelD.add(Conv2D(64, (3, 3), activation='relu', padding='same', name='block1_conv2'))
        modelD.add(MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool'))

        # Block 2
        modelD.add(Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv1'))
        modelD.add(Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv3'))
        modelD.add(MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool'))

        # Block 3
        modelD.add(Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv1'))
        modelD.add(Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv2'))
        modelD.add(Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv3'))
#        modelD.add(Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv4'))
        modelD.add(MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool'))

        # Block 4
        modelD.add(Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv1'))
        modelD.add(Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv2'))
        modelD.add(Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv3'))
#        modelD.add(Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv4'))
        modelD.add(MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool'))
    #
    #    # Block 5
        modelD.add(Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv1'))
        modelD.add(Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv2'))
        modelD.add(Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv3'))
##        modelD.add(Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv4'))
        modelD.add(MaxPooling2D((2, 2), strides=(2, 2), name='block5_pool'))
    #

        # Classification block
        modelD.add(Flatten(name='flatten'))
        modelD.add(Dense(3072, kernel_regularizer=regularizers.l2(regularizersRate), activation='relu', name='fc1'))
        modelD.add(Dropout(dropOut, name='do1'))
        modelD.add(Dense(3072, kernel_regularizer=regularizers.l2(regularizersRate), activation='relu', name='fc2'))
        modelD.add(Dropout(dropOut, name='do2'))
        modelD.add(Dense(1024, kernel_regularizer=regularizers.l2(regularizersRate), activation='relu', name='fc5'))
        modelD.add(Dropout(dropOut, name='do3'))
        modelD.add(Dense(len(self.labels), activation='softmax', name='predictions'))

        #opt = optimizers.Adam(lr=learningRate, decay=decay,)
        sgd = optimizers.SGD(lr=learningRate,momentum=momentum,decay=decay, nesterov=True)

        modelD.compile(optimizer = sgd,
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        if weight:
            print('load', self.name, weight)
            modelD.load_weights(weight)

        return modelD


    def TestHierarch(self, models, mode):
        """Test the architecture of models
        
        Input:
        self -- the model with mode 1
        models -- a list of models with mode 2 or 3
        mode -- a int
        
        output
        ress -- a float, the percentage of success of the architecture"""
        confuse = [[0 for x in self.labels] for y in self.labels]
        print(self.labels,'\n')
        with tf.Session() as sess:
            init = tf.global_variables_initializer()
            sess.run(init)
            for model in models:
                model.LoadModel()
            if mode == 2:
                hierarch = HierarchIni(models)
                begin = datetime.now()
                shuffle(models[0].flatFiles)
                total = {label:0 for label in self.labels}
                for i, file in enumerate(models[0].flatFiles[:testNumPic*len(self.labels)]):
                    labelmax = MaxLabelTree(models[0], hierarch, file)
                    total[labelmax] += 1
                    for labelBis, files in zip(self.labels, self.files):
                        if file in files:
                            confuse[self.labels.index(labelmax)][self.labels.index(labelBis)] += 1
                    eta = ((datetime.now()-begin)/(i+1)*(testNumPic*len(self.files))+begin).strftime('%H:%M')
                    Progress(str(i+1)+'/'+str(testNumPic*len(self.files))+' | '+eta)
                for i, label1 in enumerate(self.labels):
                    for j, label2 in enumerate(self.labels):
                        confuse[i][j]/=total[label1]

#            if mode == 3:
#                fileLabelModel = SortedDict()
#                for model in models:
#                    for file in model.files[0]:
#                        fileLabelModel[file]=[model, model.labels[0]]
#                begin = datetime.now()
#                for i, file in enumerate(fileLabelModel):
#                    model, label = fileLabelModel[file]
#                    labelmax = MaxLabelMultiBin(models, file)
#                    print(file, 'detected as', labelmax)
#                    confuse[self.labels.index(label)][self.labels.index(labelmax)] += 1/len(model.files[0])
#                    eta = ((datetime.now()-begin)/(i+1)*len(fileLabelModel)+begin).strftime('%H:%M')
#                    Progress(str(i+1)+'/'+str(len(fileLabelModel))+' | '+eta)

            print('--------------\nmode:', mode)
            print('confuse:', confuse)
            res = 0
            for i in range(len(confuse)):
                print(self.labels[i], ':', confuse[i][i])
                res+= confuse[i][i]/len(confuse)
            print(mode, 'succes:', res)
            self.PlotConfuse(confuse)
        return res


def HierarchIni(models):
    hierarch = {}
    currentFlats = [(set(glob(join(root, '**', '*.jpg'),  recursive=True)),root) for root, subdirs, files in walk(join('.', 'imgs', models[0].folder))]
    for model in models:
        modelflat = set(model.flatFiles)
        for currentflat, root in currentFlats:
            if currentflat == modelflat:
                hierarch[root.split('\\')[-1]] = model
    return hierarch

def MaxLabelTree(model1, hierarch, file):
    r = model1.Recognize(file)
    labelmax = getMaxTuple(r)[0]
    while labelmax in hierarch:
        r = hierarch[labelmax].Recognize(file)
        labelmax = getMaxTuple(r)[0]
    return labelmax

def MaxLabelMultiBin(models, file):
    r = []
    for model in models:
        r.append(model.Recognize(file)[0])
    labelmax, p = getMaxTuple(r)
    return labelmax

def getMaxTuple(r):
    pmax = 0
    for label, p in r:
        if p > pmax:
            labelmax = label
            pmax = p
    return labelmax, p

def FlattenList(l):
    flatL = []
    for ele in l:
        flatL += ele
    return flatL

def Progress(s):
    sys.stdout.write('\r')
    sys.stdout.write(s+'           ')
    sys.stdout.flush()

def preprocess_input(x, dim_ordering='default'):
    if dim_ordering == 'default':
        dim_ordering = K.image_dim_ordering()
    assert dim_ordering in {'tf', 'th'}

    if dim_ordering == 'th':
        x[:, 0, :, :] -= 103.939
        x[:, 1, :, :] -= 116.779
        x[:, 2, :, :] -= 123.68
        # 'RGB'->'BGR'
        x = x[:, ::-1, :, :]
    else:
        x[:, :, :, 0] -= 103.939
        x[:, :, :, 1] -= 116.779
        x[:, :, :, 2] -= 123.68
        # 'RGB'->'BGR'
        x = x[:, :, :, ::-1]
    return x


def PrepareImage(file):
    img = image_utils.load_img(file, target_size=picSize[:2],grayscale=grayscale)
    x = image_utils.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    if x.shape[-1]==3:
        x = preprocess_input(x)
    return x
        
def GetColor(z, mini = 40, maxi=100):
    if z < mini:
        ratio = 0
    elif z > maxi:
        ratio = 1
    else:
        ratio = (z-mini)/(maxi - mini)
    hue = ratio * 1.2/3.6
    rgb = colorsys.hls_to_rgb(hue, 0.45, 1)
    return rgb

def PlotHist(r, s):
    x, y = [], []
    for label, p in sorted(list(r.items())[:25], key=lambda x: x[1]):
        x.append(label)
        y.append(int(p*1000)/10)
    print('Overall probabilities (over tags):', sum(y)/len(y),'%')

    colors = [GetColor(y_) for y_ in y]
    y_pos = np.arange(len(y))
    fig, ax = plt.subplots((1))
    ax.barh(y_pos, y, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(x)
    plt.ylabel('Labels')
    plt.xlabel('Percentage of success')
    plt.title(s)
    plt.show()

def ModelsGenerator(folder, mode):
    # mode=1 is a classic classifier
    # mode=2 is a tree classifier
    # mode=3 is a binary multiclass classifier
    models = []
    if mode in [1,3]:
        labels = list(set([path.split('\\')[-2]  for path in glob(join('.', 'imgs', folder, '**', '*.jpg'),  recursive=True)]))
        filesL = [glob(join('.', 'imgs', folder, '**', label, '*.jpg'),  recursive=True) for label in labels]

        if mode == 1:
            [random.shuffle(files) for files in filesL]
            models = [Model(labels, folder, filesL, folder)]
#        elif mode == 3:
#            flatFiles = FlattenList(filesL)
#            for label, files in zip(labels, filesL):
#                binFiles = [files, [file for file in flatFiles if not file in files]]
#                random.shuffle(binFiles[1])
#                binLabels = [label, 'not_'+label]
#                models.append(Model(binLabels, label, binFiles, folder))
    elif mode==2:
        pathsL = []
        add = [[join('.', 'imgs', folder, fold) for fold in listdir(join('.', 'imgs', folder))]]
        while add:
            pathsL += add
            add = [[join(root, fold) for fold in listdir(root) if not fold.endswith('.jpg')] for root in pathsL[-1]]
        pathsL = [paths for paths in pathsL if paths]
        for i, paths in enumerate(pathsL):
            modelName = folder+str(i)
            labels = [path.split('\\')[-1] for path in paths]
            filesL = [glob(join('.', 'imgs', folder, '**', label, '**', '*.jpg'),  recursive=True) for label in labels]
            [random.shuffle(files) for files in filesL]
            models.append(Model(labels, modelName, filesL, folder))
    return models

#def TrainAll(name):
#    for i in [1,2,3]:
#        models = ModelsGenerator(name, i)
#        for model in models:
#            with tf.Session() as sess:
#                model.PrepareData()
#                model.Train()
#            sess
#
#def TestAll(name):
#    for i in range(3, 0, -1):
#        with tf.Session() as sess:
#            basicModel = ModelsGenerator(name,1)[0]
#            if i == 1:
#                basicModel.Test()
#            else:
#                models = ModelsGenerator(name, i)
#                basicModel.TestHierarch(models,i)
#        sess

#def TestTriParty(name):
#    models = [ModelsGenerator(name, i) for i in range(1,4)]
#    files = models[0][0].flatFiles
#    begin = datetime.now()
#    confuse = [[0 for x in models[0][0].labels] for y in models[0][0].labels]
#
#    preds = {}
#    for file in files:
#        preds[file] = []
#    length = len(files)
#    for k, modelL in enumerate(models):
#        with tf.Session() as sess:
#            for model in modelL:
#                model.LoadModel()
#            for i, file in enumerate(files):
#                if k == 0:
#                    preds[file].append(getMaxTuple(models[0][0].Recognize(file))[0])
#                elif k== 1:
#                    preds[file].append(MaxLabelTree(models[1][0],HierarchIni(models[1]), file))
#                elif k==2:
#                    preds[file].append(MaxLabelMultiBin(models[2], file))
#
#                eta = ((datetime.now()-begin)/(i+1)*length+begin).strftime('%H:%M')
#                Progress(str(i+1)+'/'+str(length)+' | '+eta)
#
#        sess
#    decide = 1
#    for file in files:
#        if preds[file][0] == preds[file][1] and preds[file][1]==preds[file][2]:
#            label = preds[file][0]
#            for labelBis, filesBis in zip(models[0][0].labels, models[0][0].files):
#                if file in filesBis:
#                    confuse[models[0][0].labels.index(labelBis)][models[0][0].labels.index(label)] += 1/len(filesBis)
#        else:
#            decide -= 1/length
#    print('confuse:', confuse)
#    res = sum([confuse[i][i]/len(confuse) for i in range(len(confuse))])
#    print('succes:', res/decide)
#    models[0][0].PlotConfuse(confuse)
#    print('proportion of decided:', decide)


#TrainAll(name)
models = ModelsGenerator(name,modelType)
if mode == 'test':
    models[modelIndex].Test()
elif mode == 'train':
    models[modelIndex].ExportSummary()
    models[modelIndex].PrepareData()
    models[modelIndex].Train(resume=0)
    #TestTriParty(name)
elif mode == 'testH':
    ModelsGenerator(name,1)[0].TestHierarch(models, modelType)
    
print('FINISH')
