# -*- coding: utf-8 -*-
"""

This is MVP0.1 of an NLP binary text classification problem, dated 2/12/2019.
Major code strcture changes, bug fixes, and algorithm development are in progress. 
Read ITAR_NLPDeploymentDocumentforNLPversion01.pdf for deployment instructions.

"""
#%%
'''
IMPORT STATEMENTS
'''
import csv
from normalization_deploy_0 import normalize_corpus
import nltk
nltk.download('punkt') #need to download only the first time running
from sklearn.feature_extraction.text import CountVectorizer 
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import itertools
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model.logistic import LogisticRegression


'''
PARAMETER DEFINITIONS
Future versions will include a separate file with all parameter configurations.
'''
min_df = 1         #min_df to ignore terms that appear too infrequently: 0.01 (ignore terms that appear in <1% documents); 5 (ignore terms that appear in <5 docs)
max_df = 0.70        #max_df to ignore terms that appear too frequently: 0.50 (ignore terms that appear in >50% of documents); 25 (ignore terms that appear in >25 docs)
ngram_range = (1,1)        #ngram_range is lower & upper boundary of range of n-values for dif n-grams to be extracted. (1,1) = only 1-grams. 
max_features = None        #max_features to consider only top features ordered by term frequency
mnb = MultinomialNB()
svm = SGDClassifier(loss='hinge', max_iter=100)
lr = LogisticRegression()
trainingFileName = 'TrainingDataset.csv'


'''
FUNCTION DEFINITIONS
'''
#IMPORT TRAINING DATA
#Remove class "0" - have not yet been looked at by any SME. 
def importData(): 
    combined_corpus_raw = []
    classes_raw = []
    combined_corpus = []
    classes = []
    class_binary = []
    combined_corpus_binary = []

    with open(trainingFileName, encoding="latin-1") as trainfile:
        trainCSV = csv.reader(trainfile, delimiter = ',')
        for col in trainCSV:
            new_row = ['. '.join([col[10], col[42]])]
            combined_corpus_raw.append(new_row[0])
            classes_raw.append(col[1])
    i = 0
    while i < len(classes_raw):
        if classes_raw[i] != '0' and classes_raw[i] != 'Class Label': #if class is not 0 i.e. not yet seen & disclude header
            classes.append(classes_raw[i])
            combined_corpus.append(combined_corpus_raw[i])
        i += 1
    i = 0
    while i < len(classes): 
        if classes[i] != '1': #separate out the failures
            class_binary.append("Non-Failures")
            combined_corpus_binary.append(combined_corpus[i])
        else:
            class_binary.append("Failures")
            combined_corpus_binary.append(combined_corpus[i])
        i += 1
    return combined_corpus, classes, combined_corpus_binary, class_binary


#IMPORT TESTING DATA
def importTestData(fileName):
    #import new testing file
    combined_corpus_binary_test = []
    vesselName = []
    vesselID = []
    equipName = []
    equipID = []
    with open(fileName) as testFile:
        testCSV = csv.reader(testFile, delimiter = ',')
        for col in testCSV:
            new_row = ['. '.join([col[0], col[1]])]
            combined_corpus_binary_test.append(new_row[0])
            vesselName.append(col[2])
            vesselID.append(col[3])
            equipName.append(col[4])
            equipID.append(col[5])
    #print(combined_corpus_binary_test, vesselName, vesselID, equipName, equipID)
    return combined_corpus_binary_test, vesselName, vesselID, equipName, equipID


#Bag of Words
def bow_extractor(corpus, lowercase  = True, analyzer='word', tokenizer=callable, ngram_range=ngram_range):
    vectorizer = CountVectorizer(min_df=min_df, 
                                 max_df = max_df, 
                                 ngram_range=ngram_range, 
                                 max_features = max_features) 
    features = vectorizer.fit_transform(corpus)
    return vectorizer, features
    

##TF-IDF
def tfidf_extractor(corpus, ngram_range = ngram_range):
    vectorizer = TfidfVectorizer(min_df=min_df, 
                                 norm='l2',
                                 smooth_idf=True,
                                 use_idf=True,
                                 ngram_range=ngram_range,
                                 max_features=max_features)
    features = vectorizer.fit_transform(corpus)
    return vectorizer, features
      

#Modelling 
def train_predict_model(classifier, train_features, train_labels, test_features):
    classifier.fit(train_features, train_labels)
    predictions = classifier.predict(test_features)
    probabilities = classifier.predict_proba(test_features)
    return predictions, probabilities

#%%
'''
RUN FUNCTIONS for binary problem. - need to make into wrapper
Using the entire EPF dataset to train the model.
Using the new input dataset as the test dataset. Run the model on this test dataset. 
'''

#MAKE THIS A WRAPPER
def runAll(fileName):
    #import training data
    combined_corpus, classes, combined_corpus_binary, class_binary = importData()
    norm_corpus_binary = normalize_corpus(combined_corpus_binary)
    #import testing data
    combined_corpus_binary_test, vesselName, vesselID, equipName, equipID = importTestData(fileName)

    norm_corpus_binary_test = normalize_corpus(combined_corpus_binary_test)
    #get train features
    bow_vectorizer_2_binary, bow_features_2_binary = bow_extractor(norm_corpus_binary)
    tfidf_vectorizer_binary, tfidf_train_features_binary = tfidf_extractor(norm_corpus_binary)
    #get test features
    bow_test_features_binary = bow_vectorizer_2_binary.transform(norm_corpus_binary_test)
    tfidf_test_features_binary = tfidf_vectorizer_binary.transform(norm_corpus_binary_test)
    #Modelling
    mnb_bow_predictions_binary, mnb_bow_probabilities_binary = train_predict_model(mnb, bow_features_2_binary, class_binary, bow_test_features_binary)
    mnb_tfidf_predictions_binary, mnb_tfidf_probabilities_binary = train_predict_model(mnb, tfidf_train_features_binary, class_binary,  tfidf_test_features_binary)
    lr_tfidf_predictions_binary, lr_tfidf_probabilities_binary = train_predict_model(lr, tfidf_train_features_binary, class_binary, tfidf_test_features_binary)
    #get scores of each prediction
    predNB = []
    i = 0
    while i < len(mnb_bow_predictions_binary):
        if mnb_bow_predictions_binary[i] == "Failures":
            predNB.append(mnb_bow_probabilities_binary[i][0])
        else:
            predNB.append(mnb_bow_probabilities_binary[i][1])
        i += 1
    predLR = []
    i = 0
    while i < len(lr_tfidf_predictions_binary):
        if lr_tfidf_predictions_binary[i] == "Failures":
            predLR.append(lr_tfidf_probabilities_binary[i][0])
        else:
            predLR.append(lr_tfidf_probabilities_binary[i][1])
        i += 1
     #fix common LR mis-class problem
    finalCase = []
    i = 0
    while i < len(mnb_bow_predictions_binary):
        if mnb_bow_predictions_binary[i] == "Failures" or lr_tfidf_predictions_binary[i] == "Failures":
            finalCase.append("Failures")
        elif mnb_bow_predictions_binary[i] == lr_tfidf_predictions_binary[i]:
            finalCase.append(mnb_bow_predictions_binary[i])
        else:
            finalCase.append("")
        i += 1
    #consolidate output
    outputDF = pd.DataFrame({'Normalized Maintenance Details': norm_corpus_binary_test[1:],
                              'Algorithm 1': mnb_bow_predictions_binary[1:],
                              'Algorithm 1 Probability': predNB[1:],
                              'Algorithm 2': lr_tfidf_predictions_binary[1:],
                              'Algorithm 2 Probability': predLR[1:],
                              'Final Class Label': finalCase[1:],
                              'Vessel Name': vesselName[1:],
                              'Vessel ID': vesselID[1:],
                              'Equipment Name': equipName[1:],
                              'Equipment ID': equipID[1:]
                                  })
    #print to output csv file
    outputDF.to_csv('PredictedClasses.csv', index = False)
    return


#runAll()