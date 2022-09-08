import pandas
import pandas as pd

from circle_data_model import circle_utility
from circle_data_model import Recommender

#this need to change if its docker
Recommender = Recommender.RecommenderEngine()
identifier = "room_id"
feature = "vector"
main_dataframe: pandas.DataFrame = pd.DataFrame()

def add_data_in_dataframe(df_ref_snapshot):

    global main_dataframe

    df_ref_snapshot = check_if_snapshot_isinList(df_ref_snapshot)

    if (len(df_ref_snapshot)==0):
        raise Exception("Data is empty")
        return 1

    temp = circle_utility.turn_firestore_vector_to_df(df_ref_snapshot, identifier, feature)
    main_dataframe = pandas.concat([main_dataframe , temp])

    Recommender.generate_index(main_dataframe, feature, identifier)
    return 0


def update_data_in_dataframe(snapshot):
    """
    update existing dataframe with new data from specific if from snapshot
    :param snapshot: firestore snapshot
    :return: None
    """
    global main_dataframe

    snapshot = check_if_snapshot_isinList(snapshot)

    temp = circle_utility.turn_firestore_vector_to_df(snapshot, identifier, feature)
    room_ids, vectors = temp.T.to_numpy()
    for count, id in enumerate(room_ids):
        main_dataframe.loc[main_dataframe[identifier] ==  id , identifier] = vectors[count]

    Recommender.generate_index(main_dataframe, feature, identifier)
    return

def delete_data_in_dataframe(snapshot):
    global main_dataframe

    snapshot = check_if_snapshot_isinList(snapshot)

    for document in snapshot:
        # This deletion is completed by "selecting" rows where document id is the same
        main_dataframe.drop(main_dataframe[(main_dataframe.room_id == document.id)].index, inplace=True)
    Recommender.generate_index(main_dataframe, feature, identifier)
    return

def check_if_snapshot_isinList(snapshot):
    """
    turn single document into list
    :param snapshot: snapshots
    :return: snapshot in list
    """
    if isinstance(snapshot, list):
        return snapshot
    else:
        return [snapshot]

def turn_text_to_vector(text: str):
    vector = Recommender.model([text])
    return vector

def predict(text:str, k_value):
    try:
        if (main_dataframe is None):
            return "empty query"
    except Exception as e:
        raise e


    #check k value
    data_len = len(main_dataframe)
    if(data_len < k_value):
        k_value = data_len

    #rekomendasi
    recommendation = Recommender.predict(text, k_value=k_value)


    return recommendation

def update_index():
    pass