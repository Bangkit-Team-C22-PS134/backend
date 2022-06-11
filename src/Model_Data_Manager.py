from circle_data_model import generate_saved_model
from circle_data_model import circle_utility
import numpy as np
import tensorflow_recommenders as tfrs

MAIN_TEXT_MODEL = generate_saved_model.model_nlm_v1
MAIN_USER_MODEL = generate_saved_model.model.user_model
MAIN_CAREGIVER_MODEL = generate_saved_model.model.caregiver_model

TEXT_INDEX = tfrs.layers.factorized_top_k.ScaNN(MAIN_TEXT_MODEL)
INDEX = tfrs.layers.factorized_top_k.ScaNN(MAIN_USER_MODEL)


MAIN_DATAFRAME = None
CAREGIVER_DS_TEXT = None

def generate_dataframe(df_ref_snapshot):
    global CAREGIVER_DS_TEXT, MAIN_DATAFRAME
    data = circle_utility.unpack_caregiver_snapshot(df_ref_snapshot)
    MAIN_DATAFRAME = circle_utility.convert_caregiver_dictList_to_df(data)
    CAREGIVER_DS_TEXT = circle_utility.df_to_dataset(MAIN_DATAFRAME)
    CAREGIVER_DS_TEXT = CAREGIVER_DS_TEXT.map(lambda features: (features['CAREGIVER_ID'], MAIN_TEXT_MODEL(features['text'])))
    return MAIN_DATAFRAME

def generate_ds(df):
    pass

def update_processed_dataframe(df_ref_snapshot):
    pass

def update_existing_df():
    pass

def predict(id, data, k_value):
    query_string = f'user_id!="{id}"'
    temp_df = MAIN_DATAFRAME.query(query_string)
    #check k value
    if(len(MAIN_DATAFRAME.index) < k_value):
        k_value = len(MAIN_DATAFRAME.index)

    TEXT_INDEX.index_from_dataset(
        CAREGIVER_DS_TEXT
    )
    _, recommendation = TEXT_INDEX(np.array([data['text']]), k=k_value)
    temp_data = {
        "recommendation": recommendation[0].numpy().tolist()
    }
    id_list = list(map(lambda string: string.decode("utf-8").strip(), temp_data['recommendation']))
    new_temp_df = temp_df.iloc[np.where(temp_df.CAREGIVER_ID.isin(id_list))]
    temp_ds = circle_utility.df_to_dataset(new_temp_df)


    INDEX.index_from_dataset(
        temp_ds.map(lambda features: (features['CAREGIVER_ID'], MAIN_CAREGIVER_MODEL(features)) )
    )
    # check k value
    if (len(new_temp_df.index) < k_value):
        k_value = len(new_temp_df.index)
    _, recommendation = INDEX(data, k=k_value)

    return recommendation

def update_index():
    pass