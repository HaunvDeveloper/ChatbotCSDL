#from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from bm25 import BM25 
from custom_tokenizer import *
import json

class  classify:
    def __init__(self, fileIntents):
        self.fileIntents = fileIntents
        self.candidateIntents = []
        self.corpus = self.merge(fileIntents)
        
    def merge(self, path):
        listIntent = []
        json_data = open(path, encoding="utf8")
        intents = json.load(json_data)
        
        for intent in intents["intents"]:
            self.candidateIntents.append(intent['tag'])
            #print(self.candidateIntents)
            patternIntent =[]
            for pattern in intent['patterns']:
                patternIntent.append(pattern)
            listIntent.append(" ".join(patternIntent))
        return listIntent
    
    def getIntent(self, query):
        corpus = self.corpus.copy()
        texts = []
        for document in corpus:
            token = custom_tokenize(document.lower())
            texts.append(token)
        # build a word count dictionary so we can remove words that appear only once
        word_count_dict = {}
        for text in texts:
            for token in text:
                word_count = word_count_dict.get(token, 0) + 1
                word_count_dict[token] = word_count

        texts = [
            [token for token in text if word_count_dict[token] > 0] for text in texts
        ]
        query = custom_tokenize(query.lower())
        bm25 = BM25()
        bm25.fit(texts)
        scores = bm25.search(query)
        scores = np.array(scores)
        return self.candidateIntents[np.argmax(scores)]


if __name__ == "__main__":
    input_query = input("Query: ")
    classify = classify("data/intents.json")
    print(classify.getIntent(input_query))   
