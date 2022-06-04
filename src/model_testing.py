import tensorflow as tf
from  circle_data_model import circle_utility
from firebase_admin import credentials, firestore, initialize_app
import numpy as np


MAIN_CAREGIVER_DATAFRAME = np.array([0])
MAIN_TEXT_MODEL = tf.saved_model.load('../resources/saved_model/text_query_v1')


def update_index():
    global MAIN_CAREGIVER_DATAFRAME

    return 0

def predict_text(text):
    global MAIN_TEXT_MODEL
    return MAIN_TEXT_MODEL.predict([text])

if __name__ == "__main__" :
    print(MAIN_TEXT_MODEL(["aa sss"]))




