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
    tokenized_text = tokenizer.tokenize(text.text)
    sent = ['[CLS]'] + tokenized_text + ['[SEP]']
    input_ids = tokenizer.convert_tokens_to_ids(sent)
    #Pad our tokens which might be less than max_length size
    input_ids = pad_sequences([input_ids], maxlen=max_length+2, truncating='post', padding='post')
    atten_mask = [float(i > 0) for i in input_ids[0]]
    x = {'input_ids': np.array([input_ids[0]]), 'attention_mask': np.array([atten_mask])}
    mild = model.predict(x)[0][0][0]
    wild = model.predict(x)[0][0][1]
    if mild > wild:
        res = 1
    else:
        res = 0
    print(mild, wild)
    return {"result": res}



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    run(app, host="0.0.0.0", port=port)