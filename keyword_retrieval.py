import numpy as np
from bm25 import BM25 
from custom_tokenizer import *
import json




class  keywords_retriever:
    def __init__(self, fileIntents):
        self.fileIntents = fileIntents
        self.candidateKey = []
        self.corpus = self.merge(fileIntents)
        
    def merge(self, path):
        listIntent = []
        json_data = open(path, encoding="utf8")
        intents = json.load(json_data)
        
        for intent in intents["intents"]:
            self.candidateKey.append(intent['tag'])
            patternIntent =[]
            for pattern in intent['patterns']:
                patternIntent.append(pattern)
            listIntent.append(" ".join(patternIntent))
        return listIntent
        
    def getKeywords(self, query, topK=1):
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
    #['khóa', 'là', 'gì']
        bm25 = BM25()
        bm25.fit(texts)
        scores = np.array(bm25.search(query))
        scores = np.argsort(scores)[::-1][:topK]
        res = []
        for i in scores:
            res.append(self.candidateKey[i])
        return res
        


if __name__ == "__main__":
    input_query = input("Query: ")
    classify = keywords_retriever("data/keywords.json")
    print(classify.getKeywords(input_query, topK=1))  
