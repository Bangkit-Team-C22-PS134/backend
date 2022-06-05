import tensorflow as tf
import tensorflow_recommenders as tfrs
from  circle_data_model import circle_utility
from firebase_admin import credentials, firestore, initialize_app
import numpy as np


CAREGIVER_DS = np.array([0])
INDEX = None #will be set up later
MAIN_TEXT_MODEL = tf.keras.models.load_model('../resources/saved_model/text_query_v1')
MAIN_USER_MODEL = tf.keras.models.load_model('../resources/saved_model/user_query_v1')
MAIN_CAREGIVER_MODEL = tf.keras.models.load_model('../resources/saved_model/caregiver_query_v1')


def update_index():
    global MAIN_CAREGIVER_DATAFRAME

    return 0

def predict_text(text):
    global MAIN_TEXT_MODEL
    return MAIN_TEXT_MODEL.predict([text])

if __name__ == "__main__" :
    cred = credentials.Certificate("key.json")
    default_app = initialize_app(cred)
    db = firestore.client()
    db_ref = db.collection('chat_rooms')
    data = db_ref.get()
    data = circle_utility.unpack_caregiver_snapshot(data)
    data = circle_utility.convert_caregiver_dictList_to_df(data)
    caregiver_ds = circle_utility.df_to_dataset(data)
    TEXT_INDEX = tfrs.layers.factorized_top_k.BruteForce(MAIN_TEXT_MODEL)

    # update this
    TEXT_INDEX.index_from_dataset(
        caregiver_ds.map(lambda features: (features['CAREGIVER_ID'], MAIN_TEXT_MODEL([features['text']])))
    )

    INDEX = tfrs.layers.factorized_top_k.BruteForce(MAIN_USER_MODEL)

    # update_this
    INDEX.index_from_dataset(
        caregiver_ds.map(lambda features: (features['CAREGIVER_ID'], MAIN_CAREGIVER_MODEL(features)))
    )

    a = ['Gender', 'Age', 'ADHD-Hiperaktif-dan-kurang-fokus', 'Depresi', 'Gangguan-kecemasan', 'Gangguan-makan',
         'Gangguan-stres-pascatrauma', 'Skizofrenia']
    value = ['Pria', 30, 0, 1, 0, 0, 1, 0]
    dictionary_Test = dict((el, ([value[ix]])) for ix, el in enumerate(a))
    print(dictionary_Test)

    a, titles = INDEX(dictionary_Test, k=1)
    print(f"Top recommendations: {titles[0]}")

    a, titles = TEXT_INDEX(np.array(["AAAA sa sayang"]), k=1)

    print(f"Top recommendations: {titles[0]}")

    print(MAIN_TEXT_MODEL(np.array(["aa sss"])))



def test_model_v1():
    cred = credentials.Certificate("key.json")
    default_app = initialize_app(cred)
    db = firestore.client()
    db_ref = db.collection('chat_rooms')
    data = db_ref.get()
    data = circle_utility.unpack_caregiver_snapshot(data)
    data = circle_utility.convert_caregiver_dictList_to_df(data)
    caregiver_ds = circle_utility.df_to_dataset(data)
    TEXT_INDEX = tfrs.layers.factorized_top_k.BruteForce(MAIN_TEXT_MODEL)

    # update this
    TEXT_INDEX.index_from_dataset(
        caregiver_ds.map(lambda features: (features['CAREGIVER_ID'], MAIN_TEXT_MODEL([features['text']])))
    )

    INDEX = tfrs.layers.factorized_top_k.BruteForce(MAIN_USER_MODEL)

    # update_this
    INDEX.index_from_dataset(
        caregiver_ds.map(lambda features: (features['CAREGIVER_ID'], MAIN_CAREGIVER_MODEL(features)))
    )

    a = ['Gender', 'Age', 'ADHD-Hiperaktif-dan-kurang-fokus', 'Depresi', 'Gangguan-kecemasan', 'Gangguan-makan',
         'Gangguan-stres-pascatrauma', 'Skizofrenia']
    value = ['Pria', 30, 0, 1, 0, 0, 1, 0]
    dictionary_Test = dict((el, ([value[ix]])) for ix, el in enumerate(a))
    print(dictionary_Test)

    a, titles = INDEX(dictionary_Test, k=5)
    print(f"Top recommendations: {titles[0]}")

    a, titles = TEXT_INDEX(np.array(["AAAA sa sayang"]), k=5)
    print(f"Top recommendations: {titles[0]}")

    print(MAIN_TEXT_MODEL(np.array(["aa sss"])))