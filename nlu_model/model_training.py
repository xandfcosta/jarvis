import spacy
from spacy.lang.pt.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
from sklearn.metrics import accuracy_score
import json
import os
import math


datas = []
train_data = []
test_data = []
nlp = spacy.load("pt_core_news_md")

for subdir, dirs, files in os.walk("./nlu_model/sentences"):
    for file in files:
        with open(os.path.join(subdir, file), "r", encoding="utf-8") as f:
            datas.append(json.load(f))
      
for data in datas:
    sentences = data["data"]["sentences"]
    train_size = len(sentences)
    index = math.floor((len(sentences) * .9))

    for i in range(train_size):
        doc = nlp(sentences[i])
        sentence = " ".join([token.lemma_ for token in doc])
        train_data.append((sentence, data["data"]["intent"])) if i <= index else test_data.append((sentences[i], data["data"]["intent"]))

# Pré-processamento de texto
nlp = spacy.load('pt_core_news_sm')
stop_words = set(STOP_WORDS)

def preprocess(text):
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return ' '.join(tokens)

train_data = [(preprocess(data[0]), data[1]) for data in train_data]

# Extração de recursos
vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform([train_data[0] for train_data in train_data])
y_train = [train_data[1] for train_data in train_data]

X_test = vectorizer.transform([test_data[0] for test_data in test_data])
y_test = [test_data[1] for test_data in test_data]

# Treinamento do modelo
classifier = MultinomialNB()
classifier.fit(X_train, y_train)

predictions = classifier.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print('Acurácia:', accuracy)

# Salvar o modelo
with open('./nlu_model/classification_model.pkl', 'wb') as f:
    pickle.dump(classifier, f)
    
with open('./nlu_model/vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
    
print(classifier.predict(vectorizer.transform(["abrir o chrome"])))
