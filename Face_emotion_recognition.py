from os import listdir
from PIL import Image
import numpy as np
from numpy import linalg as LA
import math
import matplotlib.pyplot as plt
import statistics

# The relative path to your CAFE-Gamma dataset
data_dir = "./CAFE/"
# Dictionary of semantic "label" to emotions
emotion_dict = {"h": "happy", "ht": "happy with teeth", "m": "maudlin",
                "s": "surprise", "f": "fear", "a": "anger", "d": "disgust", "n": "neutral"}
Happydata = []
saddata = []
Afraid = []
surprised = []
images = []
labels = []
dim = 10
learning_rate = 0.1


# function to load data from given data directory
def load_data(data_dir):
    """ Load all PGM images stored in your data directory into a list of NumPy
    arrays with a list of corresponding labels.
    Args:
        data_dir: The relative filepath to the CAFE dataset.
    Returns:
        images: A list containing every image in CAFE as an array.
        labels: A list of the corresponding labels (filenames) for each image.
    """
    # Get the list of image file names
    all_files = listdir(data_dir)
    # Store the images as arrays and their labels in two lists
    for file in all_files:
        # Load in the files as PIL images and convert to NumPy arrays
        if '_ht' in file:
            img = Image.open(data_dir + file)
            Happydata.append(np.array(img))
            images.append(np.array(img))
            labels.append(file)
        elif '_m' in file:
            img = Image.open(data_dir + file)
            saddata.append(np.array(img))
            images.append(np.array(img))
            labels.append(file)
        elif '_a' in file:
            img = Image.open(data_dir + file)
            Afraid.append(np.array(img))
            images.append(np.array(img))
            labels.append(file)
        elif '_s' in file:
            img = Image.open(data_dir + file)
            surprised.append(np.array(img))
            images.append(np.array(img))
            labels.append(file)
        elif '_h' in file or '_n' in file:
            continue
        else:
            img = Image.open(data_dir + file)
            images.append(np.array(img))
            labels.append(file)
    print("Total number of images:", len(images), "and labels:", len(labels))
    return images, labels

# Performs PCA on given data to rescale it to given number of dimensions
def PCA(data, dims_rescaled_data):
    """
    returns: data transformed in 2 dims/columns + regenerated original data
    pass in: data as 2D NumPy array
    """
    m, n = data.shape
    # mean center the data
    data = data - np.mean(data, axis=0)
    # calculate the covariance matrix
    R = np.matmul(data, data.T)
    # calculate eigenvectors & eigenvalues of the covariance matrix
    # use 'eigh' rather than 'eig' since R is symmetric,
    # the . gain is substantial
    evals, evecs = LA.eigh(R)
    # sort eigenvalue in decreasing order
    idx = np.argsort(evals)[::-1]
    evecs = evecs[:, idx]
    # sort eigenvectors according to same index
    evals = evals[idx]
    # select the first n eigenvectors (n is desired dimension
    # of rescaled data array, or dims_rescaled_data)
    evecs = evecs[:, :dims_rescaled_data]
    # carry out the transformation on the data using eigenvectors
    # and return the re-scaled data, eigenvalues, and eigenvectors
    eigen_vectors = np.dot(data.T, evecs)
    for i in range(eigen_vectors.shape[1]):
        sum = np.linalg.norm(eigen_vectors[:, i])
        eigen_vectors[:, i] = eigen_vectors[:, i] / sum
        eigen_vectors[:, i] = eigen_vectors[:, i] / math.sqrt(evals[i])
    return data, evals, eigen_vectors


def display_face(img):
    """ Display the input image and optionally save as a PNG.
    Args:
        img: The NumPy array or image to display
    Returns: None
    """
    # Convert img to PIL Image object (if it's an ndarray)
    if type(img) == np.ndarray:
        print("Converting from array to PIL Image")
        img = Image.fromarray(img)
    # Display the image
    img.show()

# Reduces given data into dim number of dimensions
def reduce_dimensions(Data):
    Data_new = []
    for image in Data:
        a = image.flatten()
        Data_new.append(a)
    Data_new = np.matrix(Data_new)
    _, ev, ei = PCA(Data_new, dim)
    reduced_data = np.dot(Data_new, ei)
    return reduced_data, ei


# function to display eigen vectors in grayscale
def eigenvector_image(ev):
    ev = np.array(ev.T)
    ev = np.reshape(ev, (380, 240))
    plt.imshow(ev, cmap="gray")
    plt.show()


# Returns sigmoid of given value
def sigmoid(value):
    return 1.0 / (1 + np.exp(-value))


#Returns Logistic Regression Accuracy for given Dataset and weights
def calculate_accuracy(test, testlabel, weights):
    correct = 0
    for i in range(test.shape[0]):
        value = np.dot(weights, test[i].T)
        predict = sigmoid(value)
        if predict >= 0.5:
            y = 1
        else:
            y = 0
        if y == testlabel[i]:
            correct += 1
    return correct / test.shape[0]


#Returns Logistic Regression Loss for given Dataset and weights
def lossfunction(validation, validationlabel, weights):
    loss = 0
    for i in range(validation.shape[0]):
        value = np.dot(weights, validation[i].T)
        predict = sigmoid(value)
        loss += validationlabel[i] * np.log(predict) + (1 - validationlabel[i]) * np.log(1 - predict)
    return -loss[0,0]


#Performs Logistic Regression by training the given dataset for epoch number of iterations
def logistic_regression(features, target, epochs, rate, validation, validationlabel):
    weights = np.zeros(features.shape[1])
    updated_weights = np.zeros(features.shape[1])
    loss = lossfunction(validation, validationlabel, weights)
    for i in range(epochs):
        gradient = 0
        for j in range(0, features.shape[0]):
            value = np.dot(weights, features[j].T)
            predict = sigmoid(value)
            gradient += (target[j] - predict) * features[j]
        updated_weights = weights + rate * gradient
        new_loss = lossfunction(validation, validationlabel, updated_weights)
        if new_loss < loss:
            loss = new_loss
            weights = updated_weights
    return weights


# Returns Prediction Matrix for given dataset and weights
def yn(weights, features):
    s = 0
    y = []
    weights = np.matrix(weights)
    features = np.matrix(features)
    value = np.matmul(features, weights)
    value = np.exp(value)
    value = np.array(value)
    for i in range(len(value)):
        s = np.sum(value[i])
        y.append(value[i] / s)
    y = np.matrix(y)
    return y


#Reurns Softmax Regression Loss  for given dataset and weights
def softmax_loss(validation, validationlabel, weights):
    loss = 0
    y = yn(weights, validation)
    y = np.array(y)
    validationlabel=np.array(validationlabel)
    for i in range(validation.shape[0]):
        for j in range(6):
            loss += validationlabel[i][j] * np.log(y[i][j])
    return -loss


#Performs Softmax Regression using batch gradient descent on given dataset for epoch number of iterations
def softmax_regression(features, target, epochs, rate, validation, validationlabel):
    weights = np.zeros((features.shape[1], 6), dtype=np.int)
    new_weights = np.zeros((features.shape[1], 6), dtype=np.int)
    loss = softmax_loss(validation, validationlabel, weights)
    for i in range(epochs):
        gradient = 0
        predict = yn(weights, features)
        predict = np.array(predict)
        for j in range(features.shape[0]):
            gradient += np.matmul(features[j].T, np.matrix(target[j] - predict[j]))
        new_weights = weights + rate * gradient
        new_loss = softmax_loss(validation, validationlabel, new_weights)
        if new_loss < loss:
            loss = new_loss
            weights = new_weights
    return weights


#Returns softmax accuracy of given dataset and weights
def softmaxaccuracy(test, testlabel, weights):
    correct = 0
    predict = yn(weights, test)
    for i in range(test.shape[0]):
        argpre = np.argmax(predict[i])
        argtest = np.argmax(testlabel[i])
        if argpre == argtest:
            correct += 1
    return correct / test.shape[0]


#Determines and displays Confusion Matrix for given test dataset and weights
def confusion_matrix(test, testlabel, weights):
    a = np.zeros(shape=(6, 6))
    predict = yn(weights, test)
    for i in range(len(test)):
        argpre = np.argmax(predict[i])
        argtest = np.argmax(testlabel[i])
        a[argtest][argpre] += 1
    for row in range(a.shape[0]):
        a[row] = a[row]/np.sum(a[row])


#Perfroms Softmax regression using Stochastic Gradient Descent on given dataset for epoch number of iterations
def softmax_stochastic(features, target, epochs, rate, validation, validationlabel):
    weights=np.zeros((features.shape[1],6), dtype=np.int)
    new_weights=np.zeros((features.shape[1],6), dtype=np.int)
    loss= softmax_loss(validation,validationlabel,weights)
    p=np.arange(features.shape[0])
    for i in range(epochs):
        gradient=0
        predict=yn(weights,features)
        predict=np.array(predict)
        p=np.random.permutation(p)
        for j in range(features.shape[0]):
            gradient=np.matmul(features[p[j]].T,np.matrix(target[p[j]]-predict[p[j]]))
            new_weights=weights+rate*gradient
            new_loss=softmax_loss(validation,validationlabel,new_weights)
            if new_loss<loss:
                loss=new_loss
                weights=new_weights
    return weights


images, labels = load_data(data_dir="./CAFE/")
Data, ei = reduce_dimensions(images)


# logistic regression for happy v/s sad
X = []
X_prime = []
training_error = []
holdout_loss = []
standard_dev_train = []
standard_dev_holdout = []
for epoch in range(1,11):
    avg_error = 0
    avg_accuracy = 0
    avg_training_error = []
    avg_hold_loss = []
    test_error = []
    avg_holdout_loss = 0
    for i in range(10):
        train = []
        validation = []
        trainlabel = []
        testlabel = []
        newvalidation = []
        validationlabel = []
        test = []
        if i < 9:
            for k in range(10):
                if k == i:
                    test.append(Happydata[k])
                    testlabel.append(1)
                    test.append(saddata[k])
                    testlabel.append(0)
                elif k == i + 1:
                    validation.append(Happydata[k])
                    validationlabel.append(1)
                    validation.append(saddata[k])
                    validationlabel.append(0)
                else:
                    train.append(Happydata[k])
                    trainlabel.append(1)
                    train.append(saddata[k])
                    trainlabel.append(0)
        else:
            test.append(Happydata[k])
            testlabel.append(1)
            test.append(saddata[k])
            testlabel.append(0)
            validation.append(Happydata[0])
            validationlabel.append(1)
            validation.append(saddata[0])
            validationlabel.append(0)
            for k in range(1, 9):
                train.append(Happydata[k])
                trainlabel.append(1)
                train.append(saddata[k])
                trainlabel.append(0)
        train, eigenvec = reduce_dimensions(train)
        for image in validation:
            newvalidation.append(image.flatten())
        newvalidation = np.matrix(newvalidation)
        newvalidation = np.matmul(newvalidation, eigenvec)
        w = logistic_regression(train, trainlabel, epoch, learning_rate, newvalidation, validationlabel)
        train_set_loss = lossfunction(train, trainlabel, w)*1.0/len(train)
        hold_set_loss = lossfunction(newvalidation,validationlabel,w)*1.0/len(newvalidation)
        avg_training_error.append(train_set_loss)
        avg_hold_loss.append(hold_set_loss)
        avg_holdout_loss += hold_set_loss
        newtest = []
        for image in test:
            newtest.append(image.flatten())
        newtest = np.matrix(newtest)
        newtest = np.matmul(newtest, eigenvec)
        error = lossfunction(newtest, testlabel, w)*1.0/len(newtest)
        test_error.append(error)
        avg_error += error
        accuracy = calculate_accuracy(newtest, testlabel, w)
        avg_accuracy += accuracy
    avg_train_error = sum(avg_training_error)*1.0/10
    standard_deviation = statistics.stdev(avg_training_error)
    standard_dev_train.append(standard_deviation)
    standard_deviation_holdout = statistics.stdev(avg_hold_loss)
    standard_dev_holdout.append(standard_deviation_holdout)
    avg_holdout_loss = avg_holdout_loss*1.0/10
    training_error.append(avg_train_error)
    holdout_loss.append(avg_holdout_loss)
    X.append(epoch)
    test_sd = statistics.stdev(test_error)
    avg_error = avg_error * 1.0 / 10
    avg_accuracy = avg_accuracy * 1.0 / 10

print(test_sd)
print(avg_accuracy)
plt.errorbar(X,holdout_loss,yerr=standard_dev_holdout,label = 'Holdout set Loss')
plt.errorbar(X,training_error,yerr=standard_dev_train,label = 'Training set Loss')
plt.legend(loc='upper right')
plt.xlabel('Number of Epochs')
plt.ylabel('Cross entropy Loss')
plt.title('Logistic Regression for Happy v/s Sad')
plt.show()


#Logistic Regression for Afriad v/s Surprised
X = []
X_prime = []
training_error = []
holdout_loss = []
standard_dev_train = []
standard_dev_holdout = []
for epoch in range(1,11):
    avg_error = 0
    avg_accuracy = 0
    avg_training_error = []
    avg_hold_loss = []
    test_error = []
    avg_holdout_loss = 0
    for i in range(10):
        train = []
        validation = []
        trainlabel = []
        testlabel = []
        newvalidation = []
        validationlabel = []
        test = []
        if i < 9:
            for k in range(10):
                if k == i:
                    test.append(Afraid[k])
                    testlabel.append(1)
                    test.append(surprised[k])
                    testlabel.append(0)
                elif k == i + 1:
                    validation.append(Afraid[k])
                    validationlabel.append(1)
                    validation.append(surprised[k])
                    validationlabel.append(0)
                else:
                    train.append(Afraid[k])
                    trainlabel.append(1)
                    train.append(surprised[k])
                    trainlabel.append(0)
        else:
            test.append(Afraid[k])
            testlabel.append(1)
            test.append(surprised[k])
            testlabel.append(0)
            validation.append(Afraid[0])
            validationlabel.append(1)
            validation.append(surprised[0])
            validationlabel.append(0)
            for k in range(1, 9):
                train.append(Afraid[k])
                trainlabel.append(1)
                train.append(surprised[k])
                trainlabel.append(0)
        train, eigenvec = reduce_dimensions(train)
        for image in validation:
            newvalidation.append(image.flatten())
        newvalidation = np.matrix(newvalidation)
        newvalidation = np.matmul(newvalidation, eigenvec)
        w = logistic_regression(train, trainlabel, epoch, learning_rate, newvalidation, validationlabel)
        train_set_loss = lossfunction(train, trainlabel, w)*1.0/len(train)
        hold_set_loss = lossfunction(newvalidation,validationlabel,w)*1.0/len(newvalidation)
        avg_training_error.append(train_set_loss)
        avg_hold_loss.append(hold_set_loss)
        avg_holdout_loss += hold_set_loss
        newtest = []
        for image in test:
            newtest.append(image.flatten())
        newtest = np.matrix(newtest)
        newtest = np.matmul(newtest, eigenvec)
        error = lossfunction(newtest, testlabel, w)*1.0/len(newtest)
        test_error.append(error)
        avg_error += error
        accuracy = calculate_accuracy(newtest, testlabel, w)
        avg_accuracy += accuracy
    avg_train_error = sum(avg_training_error)*1.0/10
    standard_deviation = statistics.stdev(avg_training_error)
    standard_dev_train.append(standard_deviation)
    standard_deviation_holdout = statistics.stdev(avg_hold_loss)
    standard_dev_holdout.append(standard_deviation_holdout)
    avg_holdout_loss = avg_holdout_loss*1.0/10
    training_error.append(avg_train_error)
    holdout_loss.append(avg_holdout_loss)
    X.append(epoch)
    test_sd = statistics.stdev(test_error)
    avg_error = avg_error * 1.0 / 10
    avg_accuracy = avg_accuracy * 1.0 / 10

print(test_sd)
print(avg_accuracy)
plt.errorbar(X,holdout_loss,yerr=standard_dev_holdout,label = 'Holdout set Loss')
plt.errorbar(X,training_error,yerr=standard_dev_train,label = 'Training set Loss')
plt.legend(loc='upper right')
plt.xlabel('Number of Epochs')
plt.ylabel('Cross entropy Loss')
plt.title('Logistic Regression for Afraid v/s Surprised')
plt.show()


# Softmax Regression using Batch gradient descent for all 6 emotions
X = []
training_error = []
holdout_loss = []
standard_dev = []
for epoch in range(1, 51):
    avg_error = 0
    avg_accuracy = 0
    avg_training_error = []
    avg_holdout_loss = 0
    for i in range(10):
        train = []
        validation = []
        trainlabel = []
        testlabel = []
        newvalidation = []
        validationlabel = []
        test = []
        if i < 9:
            for k in range(60):
                if '_h' in labels[k]:
                    label = [1, 0, 0, 0, 0, 0]
                elif '_m' in labels[k]:
                    label = [0, 1, 0, 0, 0, 0]
                elif '_s' in labels[k]:
                    label = [0, 0, 1, 0, 0, 0]
                elif '_f' in labels[k]:
                    label = [0, 0, 0, 1, 0, 0]
                elif '_a' in labels[k]:
                    label = [0, 0, 0, 0, 1, 0]
                else:
                    label = [0, 0, 0, 0, 0, 1]
                if k >= 6 * i and k < 6 * (i + 1):
                    test.append(images[k])
                    testlabel.append(label)
                elif k >= 6 * (i + 1) and k < 6 * (i + 2):
                    validation.append(images[k])
                    validationlabel.append(label)
                else:
                    train.append(images[k])
                    trainlabel.append(label)
        else:
            for k in range(6 * i, 6 * (i + 1)):
                if '_h' in labels[k]:
                    label = [1, 0, 0, 0, 0, 0]
                elif '_m' in labels[k]:
                    label = [0, 1, 0, 0, 0, 0]
                elif '_s' in labels[k]:
                    label = [0, 0, 1, 0, 0, 0]
                elif '_f' in labels[k]:
                    label = [0, 0, 0, 1, 0, 0]
                elif '_a' in labels[k]:
                    label = [0, 0, 0, 0, 1, 0]
                else:
                    label = [0, 0, 0, 0, 0, 1]
                test.append(images[k])
                testlabel.append(label)
            for k in range(0, 6):
                if '_h' in labels[k]:
                    label = [1, 0, 0, 0, 0, 0]
                elif '_m' in labels[k]:
                    label = [0, 1, 0, 0, 0, 0]
                elif '_s' in labels[k]:
                    label = [0, 0, 1, 0, 0, 0]
                elif '_f' in labels[k]:
                    label = [0, 0, 0, 1, 0, 0]
                elif '_a' in labels[k]:
                    label = [0, 0, 0, 0, 1, 0]
                else:
                    label = [0, 0, 0, 0, 0, 1]
                validation.append(images[k])
                validationlabel.append(label)
            for k in range(6, 54):
                if '_h' in labels[k]:
                    label = [1, 0, 0, 0, 0, 0]
                elif '_m' in labels[k]:
                    label = [0, 1, 0, 0, 0, 0]
                elif '_s' in labels[k]:
                    label = [0, 0, 1, 0, 0, 0]
                elif '_f' in labels[k]:
                    label = [0, 0, 0, 1, 0, 0]
                elif '_a' in labels[k]:
                    label = [0, 0, 0, 0, 1, 0]
                else:
                    label = [0, 0, 0, 0, 0, 1]
                train.append(images[k])
                trainlabel.append(label)
        train, eigenvec = reduce_dimensions(train)
        trainlabel = np.matrix(trainlabel)
        for image in validation:
            newvalidation.append(image.flatten())
        newvalidation = np.matrix(newvalidation)
        newvalidation = np.matmul(newvalidation, eigenvec)
        newtest = []
        for image in test:
            newtest.append(image.flatten())
        newtest = np.matrix(newtest)
        newtest = np.matmul(newtest, eigenvec)
        w = softmax_regression(train, trainlabel, epoch, learning_rate, newvalidation, validationlabel)
        if epoch == 50 and i == 1:
            confusion_matrix(newtest, testlabel, w)
        train_set_loss = softmax_loss(train, trainlabel, w) * 1.0 / (len(train) * 6)
        # visualizing the weights
        w = np.matrix(w)
        for l in range(6):
            image = np.zeros((1, 91200), dtype=np.int)
            image = np.matrix(image)
            image = image.T
            emotion = w[:, l]
            for j in range(dim):
                eigen = ei[:, j] * emotion[j, 0]
                image = image + eigen
            image = image.T
            image = np.reshape(image, (380, 240))
            plt.imshow(image, cmap="gray")
            plt.show()
        hold_set_loss = softmax_loss(newvalidation, validationlabel, w) * 1.0 / (len(newvalidation) * 6)
        avg_training_error.append(train_set_loss)
        avg_holdout_loss += hold_set_loss
        error = softmax_loss(newtest, testlabel, w) * 1.0 / (len(newtest) * 6)
        avg_error += error
        accuracy = softmaxaccuracy(newtest, testlabel, w)
        avg_accuracy += accuracy
    avg_train_error = sum(avg_training_error) * 1.0 / 10
    standard_deviation = statistics.stdev(avg_training_error)
    standard_dev.append(standard_deviation)
    avg_holdout_loss = avg_holdout_loss * 1.0 / 10
    training_error.append(avg_train_error)
    holdout_loss.append(avg_holdout_loss)
    X.append(epoch)
    avg_error = avg_error * 1.0 / 10
    avg_accuracy = avg_accuracy * 1.0 / 10

print(avg_accuracy)
plt.plot(X, training_error, 'r', label='Training set loss')
plt.plot(X, holdout_loss, 'b', label='Holdout set loss')
plt.legend(loc='upper right')
plt.xlabel('Number of Epochs')
plt.ylabel('Loss')
plt.title('Training and HoldOut Loss v/s Number of Epochs')
plt.show()


# Softmax Regression using Stochastic gradient descent for all 6 emotions
X = []
training_error = []
holdout_loss = []
standard_dev = []
for epoch in range(1, 51):
    avg_error = 0
    avg_accuracy = 0
    avg_training_error = []
    avg_holdout_loss = 0
    for i in range(10):
        train = []
        validation = []
        trainlabel = []
        testlabel = []
        newvalidation = []
        validationlabel = []
        test = []
        if i < 9:
            for k in range(60):
                if '_h' in labels[k]:
                    label = [1, 0, 0, 0, 0, 0]
                elif '_m' in labels[k]:
                    label = [0, 1, 0, 0, 0, 0]
                elif '_s' in labels[k]:
                    label = [0, 0, 1, 0, 0, 0]
                elif '_f' in labels[k]:
                    label = [0, 0, 0, 1, 0, 0]
                elif '_a' in labels[k]:
                    label = [0, 0, 0, 0, 1, 0]
                else:
                    label = [0, 0, 0, 0, 0, 1]
                if k >= 6 * i and k < 6 * (i + 1):
                    test.append(images[k])
                    testlabel.append(label)
                elif k >= 6 * (i + 1) and k < 6 * (i + 2):
                    validation.append(images[k])
                    validationlabel.append(label)
                else:
                    train.append(images[k])
                    trainlabel.append(label)
        else:
            for k in range(6 * i, 6 * (i + 1)):
                if '_h' in labels[k]:
                    label = [1, 0, 0, 0, 0, 0]
                elif '_m' in labels[k]:
                    label = [0, 1, 0, 0, 0, 0]
                elif '_s' in labels[k]:
                    label = [0, 0, 1, 0, 0, 0]
                elif '_f' in labels[k]:
                    label = [0, 0, 0, 1, 0, 0]
                elif '_a' in labels[k]:
                    label = [0, 0, 0, 0, 1, 0]
                else:
                    label = [0, 0, 0, 0, 0, 1]
                test.append(images[k])
                testlabel.append(label)
            for k in range(0, 6):
                if '_h' in labels[k]:
                    label = [1, 0, 0, 0, 0, 0]
                elif '_m' in labels[k]:
                    label = [0, 1, 0, 0, 0, 0]
                elif '_s' in labels[k]:
                    label = [0, 0, 1, 0, 0, 0]
                elif '_f' in labels[k]:
                    label = [0, 0, 0, 1, 0, 0]
                elif '_a' in labels[k]:
                    label = [0, 0, 0, 0, 1, 0]
                else:
                    label = [0, 0, 0, 0, 0, 1]
                validation.append(images[k])
                validationlabel.append(label)
            for k in range(6, 54):
                if '_h' in labels[k]:
                    label = [1, 0, 0, 0, 0, 0]
                elif '_m' in labels[k]:
                    label = [0, 1, 0, 0, 0, 0]
                elif '_s' in labels[k]:
                    label = [0, 0, 1, 0, 0, 0]
                elif '_f' in labels[k]:
                    label = [0, 0, 0, 1, 0, 0]
                elif '_a' in labels[k]:
                    label = [0, 0, 0, 0, 1, 0]
                else:
                    label = [0, 0, 0, 0, 0, 1]
                train.append(images[k])
                trainlabel.append(label)
        train, eigenvec = reduce_dimensions(train)
        trainlabel = np.matrix(trainlabel)
        for image in validation:
            newvalidation.append(image.flatten())
        newvalidation = np.matrix(newvalidation)
        newvalidation = np.matmul(newvalidation, eigenvec)
        newtest = []
        for image in test:
            newtest.append(image.flatten())
        newtest = np.matrix(newtest)
        newtest = np.matmul(newtest, eigenvec)
        w = softmax_stochastic(train, trainlabel, epoch, learning_rate, newvalidation, validationlabel)
        train_set_loss = softmax_loss(train, trainlabel, w) * 1.0 / (len(train) * 6)
        hold_set_loss = softmax_loss(newvalidation, validationlabel, w) * 1.0 / (len(newvalidation) * 6)
        avg_training_error.append(train_set_loss)
        avg_holdout_loss += hold_set_loss
        error = softmax_loss(newtest, testlabel, w) * 1.0 / (len(newtest) * 6)
        avg_error += error
        accuracy = softmaxaccuracy(newtest, testlabel, w)
        avg_accuracy += accuracy
    avg_train_error = sum(avg_training_error) * 1.0 / 10
    standard_deviation = statistics.stdev(avg_training_error)
    standard_dev.append(standard_deviation)
    avg_holdout_loss = avg_holdout_loss * 1.0 / 10
    training_error.append(avg_train_error)
    holdout_loss.append(avg_holdout_loss)
    X.append(epoch)
    avg_error = avg_error * 1.0 / 10
    avg_accuracy = avg_accuracy * 1.0 / 10

plt.plot(X, training_error, 'r', label='Training set loss')
plt.plot(X, holdout_loss, 'b', label='Holdout set loss')
plt.legend(loc='upper right')
plt.xlabel('Number of Epochs')
plt.ylabel('Loss')
plt.title('Training and HoldOut Loss v/s Number of Epochs')
plt.show()
