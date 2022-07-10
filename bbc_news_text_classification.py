# -*- coding: utf-8 -*-
"""BBC_News_Text_Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VxPwPKtqRmC5LNnxr2-QdggbnJjkb7lX

# BBC News Text Classification

## Background
In this machine learning project, the overall topic that will be resolved is in the field of news classification, where it will try to predict the news category whether it's a business, entertainment, politics, sports, or tech topic based on the text news.

## 1. Download and import the required library

### 1.1 Download the required library
"""

!pip install nltk

"""### 1.2 Import the required libraries"""

# library for prepare the dataset
import os
import zipfile

# library for data visualization
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# library for data processing
import numpy as np
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# library for modeling
import tensorflow
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dropout, Dense, SpatialDropout1D

"""## 2. Prepares the dataset

### 2.1 Prepare Kaggle credential
"""

# set the Kaggle credential

os.environ['KAGGLE_USERNAME'] = 'rifqinovandi'
os.environ['KAGGLE_KEY'] = '1480a0d3001fda1784e2e9930f358102'

"""### 2.2 Download and preprocess dataset"""

# Download the dataset with Kaggle CLI
!kaggle datasets download -d balatmak/newsgroup20bbcnews

# Extract zip file to CWD
files = "/content/newsgroup20bbcnews.zip"
zip = zipfile.ZipFile(files, 'r')
zip.extractall('/content')
zip.close()

"""## 3. Data Understanding

### 3.1 Read dataset with pandas
"""

# Read dataset with pandas

news_df = pd.read_csv('/content/bbc-text.csv')
news_df

print(news_df['text'][1])

"""### 3.2 Explore dataset information"""

news_df.info()

# check for missing values
news_df.isna().sum()

# check for duplicate row
news_df.duplicated().sum()

"""### 3.3 Data visualization"""

news_df['category'].value_counts().plot(kind='bar', figsize=(10, 8))

"""### 3.4 Clean text from stopwords and symbols"""

# download nltk stopwords

nltk.download('stopwords')

# create function to clean text from stopwords and symbols using regex and nltk

space = re.compile('[/(){}\[\]\|@,;]')
symbols= re.compile('[^0-9a-z #+_]')
STOPWORDS = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    text = space.sub(' ', text) 
    text = symbols.sub('', text)
    text = text.replace('x', '')
    text = ' '.join(word for word in text.split() if word not in STOPWORDS) # remove stopwors from text
    return text

# applying function to pandas df

news_df['text'] = news_df['text'].apply(clean_text)

"""### 3.5 Visualize most common text in WordCloud"""

# create WordCloud function

def wordCloud(words):
  wordCloud = WordCloud(width=800, height=500, background_color='white', random_state=21, max_font_size=120).generate(words)

  plt.figure(figsize=(10, 7))
  plt.imshow(wordCloud, interpolation='bilinear')
  plt.axis('off')

# visualize WordCloud for all category

all_words = ' '.join([text for text in news_df['text']])
wordCloud(all_words)

# visualize WordCloud for business category news

business = ' '.join(text for text in news_df['text'][news_df['category']=='business'])
wordCloud(business)

# visualize WordCloud for entertainment category news

entertainment = ' '.join(text for text in news_df['text'][news_df['category']=='entertainment'])
wordCloud(entertainment)

# visualize WordCloud for politics category news

politics = ' '.join(text for text in news_df['text'][news_df['category']=='politics'])
wordCloud(politics)

# visualize WordCloud for sport category news

sport = ' '.join(text for text in news_df['text'][news_df['category']=='sport'])
wordCloud(sport)

# visualize WordCloud for tech category news

tech = ' '.join(text for text in news_df['text'][news_df['category']=='tech'])
wordCloud(tech)

"""Since the word 'said' is always dominating our WordCloud, we can remove that word later to improve our model accuracy

## 4. Data Preparation

### 4.1 Clean duplicated and unecessary word in data
"""

news_df = news_df.drop_duplicates()

news_df.duplicated().sum()

news_df['text'] = [re.sub('said', '', x) for x in news_df['text']]

"""### 4.2 Using one hot encoding for category column"""

category = pd.get_dummies(news_df['category'])
news_fixed = pd.concat([news_df, category], axis=1)
news_fixed = news_fixed.drop(columns='category')
news_fixed

"""### 4.3 Split train and test data"""

text = news_fixed['text'].values
label = news_fixed[['business', 'entertainment', 'politics', 'sport', 'tech']].values

# Train test split data

text_train, text_test, label_train, label_test = train_test_split(text, label, test_size=0.2)

"""### 4.4 Pre-modeling steps"""

# set the necessary variables

vocab_size = 50000
embedding_dim = 100
max_length = 3000
trunc_type='post'
oov_tok = "<OOV>"

# using text preprocessing tokenizer and sequence preprocessing padsequences

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(text_train)
tokenizer.fit_on_texts(text_test)

train_sequences = tokenizer.texts_to_sequences(text_train)
test_sequences = tokenizer.texts_to_sequences(text_test)
 
train_padsequences = pad_sequences(train_sequences, maxlen=max_length, truncating=trunc_type)
test_padsequences = pad_sequences(test_sequences, maxlen=max_length)

"""## 5. Modeling

### 5.1 Using Sequential model
"""

# using sequential model with embedding, LSTM, and Dense layers

model = Sequential([
                    Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_length),
                    SpatialDropout1D(0.2),
                    LSTM(64, dropout=0.4, recurrent_dropout=0.3),
                    Dropout(0.5),
                    Dense(5, activation='softmax')
                    ])

"""### 5.2 Compile model"""

# Compile model

model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

"""### 5.3 Create callback class"""

# Add calbacks on_epoch_end

class myCallback(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.96 and logs.get('val_accuracy')>0.96):
      print("\nModel accuracy and validation accuracy > 96%!")
      self.model.stop_training = True
callbacks = myCallback()

"""### 5.4 Fit model"""

# Fit model

hist = model.fit(
    train_padsequences,
    label_train,
    epochs=10,
    validation_data=(test_padsequences, label_test),
    callbacks=[callbacks]
)

"""## 6. Model Evaluation"""

# Plot accuracy and loss model

plt.plot(hist.history['accuracy'])
plt.plot(hist.history['val_accuracy'])
plt.title('Grafik Plot Akurasi Model')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='lower right')
plt.show()

plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('Grafik Plot Loss Model')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='lower right')
plt.show()

# create function to predict text
labels = ['Business','Entertainment','Politics','Sports','Tech']

def predictText(text):
  texts = map(clean_text, text) # apply clean text function
  seq = tokenizer.texts_to_sequences(texts) 
  padded = pad_sequences(seq, maxlen=max_length)
  pred = model.predict(padded)
  df = pd.DataFrame({'category' : labels, 'percentage' : pred[0]})
  print(df)
  print('\nThe text is classified as', labels[np.argmax(pred)], 'category')

news = ['It was announced on Tuesday that Disney Channel movie with tourmate Demi Lovato, "Camp Rock 2: The Final Jam," will premiere on September 3 at 8 p.m. ET. On July 27, long before they watch the sequel to the 2008 flick, fans can pick up the soundtrack, featuring 15 original songs that a press release promises will span genres from hip-hop to rock to pop. The flick will not only have more summer lovin\' between real-life couple Lovato and Joe Jonas as Mitchie and Shane, but there will also be a little friendly rivalry between the Camp Rockers and a group of musicians at another summer camp, Camp Star, including a love interest for Nick Jonas, played by Chloe Bridges. The JoBros promise the movie\'s music will be every bit as entertaining as its plot, which has been kept a secret since the movie was shot. "The songs are really cool," Joe told MTV News.']
predictText(news)

"""From the result of the prediction above, the model has alreaady achieved a good accuracy that the news has the correct prediction"""