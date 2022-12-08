import os
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from keras.models import load_model
from keras.utils import pad_sequences
import numpy as np
from uvicorn import run
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(middleware=middleware)

origins = ["*"]
methods = ["*"]
headers = ["*"]

class Text(BaseModel):
    text: str


#Get BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = TFBertForSequenceClassification.from_pretrained('bert-base-uncased')
max_length = 200

# Prepare training: Compile tf.keras model with optimizer, loss and learning rate schedule 
optimizer = tf.keras.optimizers.Adam(learning_rate=3e-5, epsilon=1e-08, clipnorm=1.0)
loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
metric = tf.keras.metrics.SparseCategoricalAccuracy('accuracy')
model.compile(optimizer=optimizer, loss=loss, metrics=[metric])

model.load_weights('./checkpoints/my_checkpoint')



@app.get("/")
async def root():
    return {"message": "Welcome to the Food Vision API!"}


@app.post("/predict")
async def predict(text: Text):
    text = text.text.split("\n")
    tokenized_texts = [tokenizer.tokenize(t) for t in text]
    tokenized_texts = [sent[:max_length] for sent in tokenized_texts]
    for i in range(len(tokenized_texts)):
        sent = tokenized_texts[i]
        sent = ['[CLS]'] + sent + ['[SEP]']
        tokenized_texts[i] = sent
    input_ids = [tokenizer.convert_tokens_to_ids(com) for com in tokenized_texts]
    #Pad our tokens which might be less than max_length size
    input_ids = pad_sequences(input_ids, maxlen=max_length+2, truncating='post', padding='post')
    attn_masks = []
    for seq in input_ids:
        seq_mask = [float(i>0) for i in seq]
        attn_masks.append(seq_mask)
    x = {'input_ids': np.array(input_ids), 'attention_mask': np.array(attn_masks)}
    res = model.predict(x)
    res = res[0]
    toxic = []
    for i in range(res.shape[0]):
        if res[i, 0] > res[i, 1]:
            toxic.append(1)
        else:
            toxic.append(0)
    return {"result": toxic}



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    run(app, host="0.0.0.0", port=port)