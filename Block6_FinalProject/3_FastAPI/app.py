import uvicorn
import pandas as pd 
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile
import mlflow
from PIL import Image
import numpy as np
import tensorflow as tf
import os
from sklearn.datasets import load_iris
import boto3
import sys

### 
# Here you can define some configurations 
###

app = FastAPI()

# Log model from local computer into heroku server
s3_model_path = 'model_celine_100cat_10epoch.h5'
print('s3_model_path',s3_model_path)
# sys.stdout.flush()

loaded_model = tf.keras.models.load_model(s3_model_path)
print('loaded_model',loaded_model)
# sys.stdout.flush()

def get_img_array(img, size):
    # `img` is a PIL image of size 299x299
    # img = tf.keras.preprocessing.image.load_img(img_path, target_size=size)
    array = tf.image.resize(img,size)
    # `array` is a float32 Numpy array of shape (299, 299, 3)
    # array = tf.keras.preprocessing.image.img_to_array(img)
    # normalize array
    array = array / 255.0
    # We add a dimension to transform our array into a "batch"
    # of size (1, 299, 299, 3)
    array = np.expand_dims(array, axis=0)
    return array



@app.post("/predict", tags=["Machine Learning"])
# async def predict(file: UploadFile = File(...)):
async def create_upload_file(file: UploadFile):    
    # print("file",file)
    # sys.stdout.flush()
    file_bytes = await file.read()
    # print("file_bytes", file_bytes)
    sys.stdout.flush()

   
    img = tf.io.decode_image(file_bytes)

    print('image mise',img)
    sys.stdout.flush()
   
    # img_array = np.array(img)
    img_array = img.numpy()
    print('image array',img_array)
    sys.stdout.flush()

    preprocessed_image = get_img_array(img_array,(299,299))
    print('image preprocessed',preprocessed_image)
    sys.stdout.flush()

    # Predict on a np array
    preds = loaded_model.predict(preprocessed_image)
    pred_labels = tf.argmax(preds, axis = -1)
    print("preds",preds)
    sys.stdout.flush()

    class_labels = ['ADONIS', 'AFRICAN GIANT SWALLOWTAIL', 'AMERICAN SNOOT', 'AN 88', 'APPOLLO', 'ARCIGERA FLOWER MOTH', 'ATALA', 'ATLAS MOTH', 'BANDED ORANGE HELICONIAN', 'BANDED PEACOCK', 'BANDED TIGER MOTH', 'BECKERS WHITE', 'BIRD CHERRY ERMINE MOTH', 'BLACK HAIRSTREAK', 'BLUE MORPHO', 'BLUE SPOTTED CROW', 'BROOKES BIRDWING', 'BROWN ARGUS', 'BROWN SIPROETA', 'CABBAGE WHITE', 'CAIRNS BIRDWING', 'CHALK HILL BLUE', 'CHECQUERED SKIPPER', 'CHESTNUT', 'CINNABAR MOTH', 'CLEARWING MOTH', 'CLEOPATRA', 'CLODIUS PARNASSIAN', 'CLOUDED SULPHUR', 'COMET MOTH', 'COMMON BANDED AWL', 'COMMON WOOD-NYMPH', 'COPPER TAIL', 'CRECENT', 'CRIMSON PATCH', 'DANAID EGGFLY', 'EASTERN COMA', 'EASTERN DAPPLE WHITE', 'EASTERN PINE ELFIN', 'ELBOWED PIERROT', 'EMPEROR GUM MOTH', 'GARDEN TIGER MOTH', 'GIANT LEOPARD MOTH', 'GLITTERING SAPPHIRE', 'GOLD BANDED', 'GREAT EGGFLY', 'GREAT JAY', 'GREEN CELLED CATTLEHEART', 'GREEN HAIRSTREAK', 'GREY HAIRSTREAK', 'HERCULES MOTH', 'HUMMING BIRD HAWK MOTH', 'INDRA SWALLOW', 'IO MOTH', 'Iphiclus sister', 'JULIA', 'LARGE MARBLE', 'LUNA MOTH', 'MADAGASCAN SUNSET MOTH', 'MALACHITE', 'MANGROVE SKIPPER', 'MESTRA', 'METALMARK', 'MILBERTS TORTOISESHELL', 'MONARCH', 'MOURNING CLOAK', 'OLEANDER HAWK MOTH', 'ORANGE OAKLEAF', 'ORANGE TIP', 'ORCHARD SWALLOW', 'PAINTED LADY', 'PAPER KITE', 'PEACOCK', 'PINE WHITE', 'PIPEVINE SWALLOW', 'POLYPHEMUS MOTH', 'POPINJAY', 'PURPLE HAIRSTREAK', 'PURPLISH COPPER', 'QUESTION MARK', 'RED ADMIRAL', 'RED CRACKER', 'RED POSTMAN', 'RED SPOTTED PURPLE', 'ROSY MAPLE MOTH', 'SCARCE SWALLOW', 'SILVER SPOT SKIPPER', 'SIXSPOT BURNET MOTH', 'SLEEPY ORANGE', 'SOOTYWING', 'SOUTHERN DOGFACE', 'STRAITED QUEEN', 'TROPICAL LEAFWING', 'TWO BARRED FLASHER', 'ULYSES', 'VICEROY', 'WHITE LINED SPHINX MOTH', 'WOOD SATYR', 'YELLOW SWALLOW TAIL', 'ZEBRA LONG WING']
    # Get the predicted label index
    pred_label_index = tf.argmax(preds, axis=-1).numpy()[0]
    print("preds_label_index",pred_label_index)
    sys.stdout.flush()

    # Get the predicted class name
    predicted_class = class_labels[pred_label_index]
    print("predicted_class",predicted_class)
    sys.stdout.flush()

    #Format response
    response = {"prediction": predicted_class}
    print("predicted_class",predicted_class)

    return response



if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000) # Here you define your web server to run the `app` variable (which contains FastAPI instance), with a specific host IP (0.0.0.0) and port (4000)


