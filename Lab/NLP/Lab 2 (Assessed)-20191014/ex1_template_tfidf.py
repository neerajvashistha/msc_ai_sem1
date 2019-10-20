# -*- coding: utf-8 -*-
"""ex1_template.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WtuJ6XLmc1hvpIkOdyiU9AKT4hyo7MnZ
"""

from __future__ import print_function  # needed for Python 2
from __future__ import division        # needed for Python 2
import csv                               # csv reader
from sklearn.svm import LinearSVC
from nltk.classify import SklearnClassifier
from random import shuffle
from sklearn.pipeline import Pipeline

# !pip install nltk
# !pip install sklearn
import nltk, math
nltk.download('stopwords')
nltk.download('words')

# load data from a file and append it to the rawData

def loadData(path, Text=None):
    with open(path,'r') as f:
        reader = csv.reader(f, delimiter='\t')
        # reader.next() # ignore header
        next(reader)
        for line in reader:
            (Id, Text, Rating, VerPurchase, Label) = parseReview(line)
            rawData.append((Id, Text, Rating, VerPurchase, Label))
            preprocessedData.append((Id, preProcess(Text), Rating, VerPurchase, Label))
            #print(preProcess(Text))

        
def splitData(percentage):
    dataSamples = len(rawData)
    halfOfData = int(len(rawData)/2)
    trainingSamples = int((percentage*dataSamples)/2)
    for (index, Text,_,_, Label) in rawData[:trainingSamples] + rawData[halfOfData:halfOfData+trainingSamples]:
        trainData.append((toFeatureVector(preProcess(Text),index),Label))
    for (index, Text,_,_, Label) in rawData[trainingSamples:halfOfData] + rawData[halfOfData+trainingSamples:]:
        testData.append((toFeatureVector(preProcess(Text),index),Label))

# QUESTION 1
import csv,re
# Convert line from input file into an id/text/label tuple
def parseReview(reviewLine):
    """
    reviewLine is a list
    """
    # Should return a triple of an integer, a string containing the review, and a string indicating the label
    doc_id = int(reviewLine[0])
    label = reviewLine[1]
    review_text = reviewLine[8]
    #print((doc_id, review_text, label))
    return (doc_id, review_text, reviewLine[2], reviewLine[3] ,label)

# TEXT PREPROCESSING AND FEATURE VECTORIZATION
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.corpus import words
stopwords = stopwords.words('english')
porter = PorterStemmer()

# Input: a string of one review
def preProcess(text):
    # Should return a list of tokens    
    # CHANGE THE CODE BELOW
    # # word tokenisation
    # text = re.sub(r"(\w)([.,;:!?'\"”\)])", r"\1 \2", text)
    # text = re.sub(r"([.,;:!?'\"“\(])(\w)", r"\1 \2", text)
    # #print "tokenising:", text
    # tokens = re.split(r"\s+",text)
    # # normalisation
    # text = re.sub(r"(\S)\1\1+",r"\1\1\1", text)
    text = text.lower()
    text = re.sub('[^A-Za-z0-9]+',' ',text)
    tokens = text.split(' ')
    # stop word removal
    tokens = [w for w in tokens if w not in stopwords]
    # Stemming
    # tokens = [porter.stem(w) for w in tokens]
    tokens = [porter.stem(w) if porter.stem(w) in set(words.words()) else w for w in tokens ] 
    # remove speacial char
    tokens = [w for w in tokens if w is not '' ]

    return tokens

# QUESTION 2
rawData = []
preprocessedData = []
loadData('amazon_reviews.txt')
print(preprocessedData[0:10])
featureDict = {} # A global dictionary of features
import collections
alltokens =[]

for i in preprocessedData:
  alltokens.extend(i[1])

featureDict = collections.Counter(alltokens)
print("Built Feature Dict")
featureDict_new = {}
total_no_of_words = sum(featureDict.values())
total_no_of_reviews = len(rawData)
print(total_no_of_words,total_no_of_reviews)

for k,v in featureDict.items():
	featureDict_new[k] = (float(v)/total_no_of_words)*math.log(float(total_no_of_reviews) / v)

print("Built new feature dict")
import numpy as np
from scipy import stats
length_of_token = []
for i in preprocessedData:
  length_of_token.append(len(i[1]))

print("Avg length of tokens", np.mean(length_of_token))
print("Median of tokens",np.median(length_of_token))
print("Mode of tokens",stats.mode(length_of_token))

import math
def toFeatureVector(tokens,index=None):
    # Should return a dictionary containing features as keys, and weights as values
    adict = {}
    total_no_of_words = sum(featureDict.values())
    total_no_of_reviews = len(rawData)

    for i in tokens[:22]:
      adict[i] = featureDict_new[i]
      # count = 0
      # for line in rawData:
      #   if i in line:
      #     count = count+1
      # adict[i] = (featureDict[i]/total_no_of_words)*math.log(float(1 + total_no_of_reviews) / (1 + count))
    if index is not None:
      for i in preprocessedData:
        if i[0] == index:
          adict['raiting'] = i[2]
          adict['verPur'] = 1 if i[3] == 'Y' else 0
    return adict

token = ['least', 'think', 'product', 'save', 'day', 'keep', 'around', 'case', 'need', u'someth']
toFeatureVector(token,index=1)

# TRAINING AND VALIDATING OUR CLASSIFIER
def trainClassifier(trainData):
    print("Training Classifier...")
    pipeline =  Pipeline([('svc', LinearSVC())])
    return SklearnClassifier(pipeline).train(trainData)

# QUESTION 3
# from sklearn.model_selection import cross_val_score
# scores = cross_val_score(lr, boston.data, boston.target, cv=7, scoring='neg_mean_squared_error')
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
def crossValidate(dataset, folds):
    shuffle(dataset)
    cv_results = []
    foldSize = int(len(dataset)/folds)
    for i in range(0,len(dataset),foldSize):
      valD = dataset[i:i+foldSize]
      testD = dataset[:i]+dataset[i+foldSize:] #list(set(dataset)-set(dataset[i:i+foldSize]))
      classi = trainClassifier(testD)
      print('predicting')
      y_true = map(lambda t: t[1], valD)
      y_pred = predictLabels(valD,classi)
      print(type(y_true),'true values',y_true)
      print(precision_recall_fscore_support(y_true, y_pred, average='macro'))
      print(accuracy_score(y_true,y_pred))
      # trainClassifier()
      # predictLabels()
      # break; # Replace by code that trains and tests on the 10 folds of data in the dataset
    return cv_results

# z=['a','b','c','d','e','f','g','h']
# for i in range(0,len(z),2):
#   print(z[i:i+2],list(set(z)-set(z[i:i+2])))
#   print(z[i:i+2],z[:i]+z[i+2:])
#   print('\n')

tokens = ['a','b','c','d','e','f','g','h']
tokens[:4]

# PREDICTING LABELS GIVEN A CLASSIFIER

def predictLabels(reviewSamples, classifier):
    # return classifier.classify_many(map(lambda t: toFeatureVector(preProcess(t[1])), reviewSamples))
    return classifier.classify_many(map(lambda t: t[0], reviewSamples))



def predictLabel(reviewSample, classifier):
    return classifier.classify(toFeatureVector(preProcess(reviewSample)))

# MAIN

# loading reviews
rawData = []          # the filtered data from the dataset file (should be 21000 samples)
preprocessedData = [] # the preprocessed reviews (just to see how your preprocessing is doing)
trainData = []        # the training data as a percentage of the total dataset (currently 80%, or 16800 samples)
testData = []         # the test data as a percentage of the total dataset (currently 20%, or 4200 samples)

# the output classes
fakeLabel = 'fake'
realLabel = 'real'

# references to the data files
reviewPath = 'amazon_reviews.txt'

## Do the actual stuff
# We parse the dataset and put it in a raw data list
print("Now %d rawData, %d trainData, %d testData" % (len(rawData), len(trainData), len(testData)),
      "Preparing the dataset...",sep='\n')
loadData(reviewPath) 
# We split the raw dataset into a set of training data and a set of test data (80/20)
print("Now %d rawData, %d trainData, %d testData" % (len(rawData), len(trainData), len(testData)),
      "Preparing training and test data...",sep='\n')
splitData(0.8)
# We print the number of training samples and the number of features
print("Now %d rawData, %d trainData, %d testData" % (len(rawData), len(trainData), len(testData)),
      "Training Samples: ", len(trainData), "Features: ", len(featureDict), sep='\n')

crossValidate(trainData, 10)

