
from circle_data_model import circle_utility
from circle_data_model import Recommender

#this need to change if its docker
Recommender = Recommender.RecommenderEngine()
identifier = "room_id"
feature = "vector"

def generate_dataframe(df_ref_snapshot):
    if (len(df_ref_snapshot)==0):
        raise Exception("Data is empty")
        return 1

    data = circle_utility.turn_firestore_vector_to_df(df_ref_snapshot, identifier, feature)
    Recommender.generate_index(data, feature, identifier)
    return 0

def update_existing_df():
    pass

def predict(text:str, k_value):
    try:
        if (Recommender.index_data is None):
            return "empty query"
    except Exception as e:
        raise e


    #check k value
    data_len = len(Recommender.index_data)
    if(data_len < k_value):
        k_value = data_len


    #ini adalah kenapa pentingnya semua harus di dokumentasi dan menggunakan bahasa yang consise dan jelas jidan :)
    recommendation = Recommender.predict(text, k_value=k_value)


    return recommendation

def update_index():
    pass