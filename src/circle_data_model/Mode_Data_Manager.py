import generate_saved_model
import  circle_utility
import tensorflow as tf
import pandas as pd
import numpy as np

import tensorflow_recommenders as tfrs
MAIN_TEXT_MODEL = generate_saved_model.model_nlm_v1
MAIN_USER_MODEL = generate_saved_model.model.user_model
MAIN_CAREGIVER_MODEL = generate_saved_model.model.caregiver_model

TEXT_INDEX = tfrs.layers.factorized_top_k.BruteForce(MAIN_TEXT_MODEL)
INDEX = tfrs.layers.factorized_top_k.BruteForce(MAIN_USER_MODEL)


MAIN_DATAFRAME = None
CAREGIVER_DS = None
def generate_dataframe(df_ref_snapshot):
    data = circle_utility.unpack_caregiver_snapshot(df_ref_snapshot)
    MAIN_DATAFRAME = circle_utility.convert_caregiver_dictList_to_df(data)
    MAIN_DATAFRAME['text_processed'] = MAIN_TEXT_MODEL(MAIN_DATAFRAME['text'])
    print(MAIN_DATAFRAME)
    return MAIN_DATAFRAME

def generate_ds(df):
    pass

def update_processed_dataframe():
    pass

def update_existing_df():
    pass

def predict(id, data, k_value):
    query_string = f'user_id!="{id}"'
    temp_df = MAIN_DATAFRAME.query(query_string)
    temp_ds= circle_utility.df_to_dataset(temp_df)

    TEXT_INDEX.index_from_dataset(
        temp_ds.map(lambda features: (features['CAREGIVER_ID'], features['text_processed']))
    )
    _, recommendation = TEXT_INDEX(data, k=k_value)
    data = {
        "recommendation": recommendation[0].numpy().tolist()
    }
    id_list = list(map(lambda string: string.decode("utf-8").strip(), data['recommendation']))

    temp_df = temp_df.iloc[np.where(temp_df.user_id.isin(id_list))]
    temp_ds = circle_utility.df_to_dataset(temp_df)
    INDEX.index_from_dataset(
        temp_ds.map(lambda features: (features['CAREGIVER_ID'], MAIN_CAREGIVER_MODEL(features)))
    )
    _, recommendation = INDEX(data, k=k_value)

    return recommendation

def update_index():
    pass