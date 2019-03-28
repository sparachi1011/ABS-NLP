# -*- coding: utf-8 -*-
"""

This is an MVP of the pre-processing steps of a binary text classification problem, dated 2/13/2019. 
Major code strcture changes, bug fixes, and algorithm development are in progress. 

"""
from contractions import CONTRACTION_MAP
import re
import nltk
import string
from nltk.stem import WordNetLemmatizer
import csv
from pattern.en import tag #note: HAVE TO DO PIP INSTALL PATTERN
from nltk.corpus import wordnet as wn

wnl = WordNetLemmatizer()

#Creating list of words to skip over during lemmatization
skipWords = []
with open('uniqueSkipWords.csv') as skipFile:
    skipWordsCSV  = csv.reader(skipFile, delimiter = ',')
    for row in skipWordsCSV:
        skipWords.append(row[0])
       
        
def tokenize_text(text):
    tokens = nltk.word_tokenize(text) 
    tokens = [token.strip() for token in tokens]
    return tokens


def expand_contractions(text, contraction_mapping):
    
    contractions_pattern = re.compile('({})'.format('|'.join(list(contraction_mapping.keys()))), 
                                      flags=re.IGNORECASE|re.DOTALL)
    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded_contraction = contraction_mapping.get(match)\
                                if contraction_mapping.get(match)\
                                else contraction_mapping.get(match.lower())                       
        expanded_contraction = first_char+expanded_contraction[1:]
        return expanded_contraction
        
    expanded_text = contractions_pattern.sub(expand_match, text)
    expanded_text = re.sub("'", "", expanded_text)
    return expanded_text
    
    
# Annotate text tokens with POS tags
def pos_tag_text(text):
    def penn_to_wn_tags(pos_tag, word):
        if word[-3:] == 'ing' and pos_tag != 'v':
            return wn.VERB
        elif pos_tag.startswith('J'):
            return wn.ADJ
        elif pos_tag.startswith('V'):
            return wn.VERB
        elif pos_tag.startswith('N'):
            return wn.NOUN
        elif pos_tag.startswith('R'):
            return wn.ADV
        else:
            return None
    try:
        tagged_text = tag(text)
    except Exception as e:
        try:
            tagged_text = tag(text)
        except Exception as e:
            tagged_text = tag(text)
    tagged_text = tag(text)
    tagged_lower_text = [(word.lower(), penn_to_wn_tags(pos_tag, word))
                         for word, pos_tag in
                         tagged_text]
    return tagged_lower_text
    

# lemmatize text based on POS tags    
def lemmatize_text(text):
    text = text.lower()
    #remove -ing, -ed before doing pos tagging
    pos_tagged_text = pos_tag_text(text)
    lemmatized_tokens = [wnl.lemmatize(word, pos_tag) if pos_tag and word not in skipWords
                         else word                     
                         for word, pos_tag in pos_tagged_text]
    lemmatized_text = ' '.join(lemmatized_tokens)
    return lemmatized_text
     
       
def remove_special_characters(text):
    tokens = tokenize_text(text)
    #removes all special charactesr including . ! ?. Does not take out numbers. 
    #keep %
    pattern = re.compile('[{}]'.format(re.escape(string.punctuation)))
    filtered_tokens = [_f for _f in [pattern.sub('', token) for token in tokens] if _f]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text


def misspell_stop(text):
    #Creating list of words to find and replace
    misspelled = {}
    with open('misspelledWords.csv') as misspelledFile:
        misspelledCSV  = csv.reader(misspelledFile, delimiter = ',')
        for row in misspelledCSV:
            # add stop words to stop array
            a=row[0]
            b=row[1]
            misspelled[a]=b
    #Creating list of words to remove      
    stopword_list = []
    with open('stopwords.csv') as stopFile:
        stopCSV  = csv.reader(stopFile, delimiter = ',')
        for row in stopCSV:
            stopword_list.append(row[0])
            
    tokens = tokenize_text(text)
    
    filtered_tokens=[]
    for token in tokens:
        if token in misspelled:
            filtered_tokens.append(misspelled[token])
#        elif token in skipWords:
#            filtered_tokens.append(token)
        elif token not in stopword_list:
            filtered_tokens.append(token)
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text

     
def normalize_corpus(corpus):
    normalized_corpus = []    
    for text in corpus:
        text = text.lower()
        text = misspell_stop(text) 
        text = expand_contractions(text, CONTRACTION_MAP)
        text = remove_special_characters(text)
        text = lemmatize_text(text)
        normalized_corpus.append(text)
    return normalized_corpus

