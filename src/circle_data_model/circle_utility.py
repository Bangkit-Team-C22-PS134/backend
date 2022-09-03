import tensorflow as tf
import numpy as np
import pandas as pd
from datetime import date

###TO DO MAKE THE CODE MORE MODULAR AND REMOVE THE SHITTY MAGIC VARIABLE
### I WILL NOT REFACTOR THIS UNTIL THE MAIN FEATURE IS DONE

def convert_snapshot(data, desired_key = None):
    """
    this extract desired keys from list of dicts from snapshot
    """
    data_dictionary = map(lambda x: x.to_dict(), data)
    if (desired_key is not None):
        data_dictionary = map(lambda x: dict((k, x[k]) for k in desired_key if k in x), list(data_dictionary))

    return list(data_dictionary)

def fill_non_existent_column(df, is_caregiver=False):
    """
    This fill the df with unique problems column i
    """
    if is_caregiver is False:
        new_column = ['ADHD-Hiperaktif-dan-kurang-fokus', 'Depresi', 'Gangguan-kecemasan', 'Gangguan-makan',
                      'Gangguan-stres-pascatrauma', 'Skizofrenia']
    else:
        new_column = ['Caregiver-ADHD-Hiperaktif-dan-kurang-fokus', 'Caregiver-Depresi', 'Caregiver-Gangguan-kecemasan',
                      'Caregiver-Gangguan-makan', 'Caregiver-Gangguan-stres-pascatrauma', 'Caregiver-Skizofrenia']

    for col in new_column:
        if (col in df.columns):
            pass
        else:
            df[col] = 0

def df_to_dataset(dataframe, shuffle=True, batch_size=32, text_processed=False):
    """
    A utility method to create a tf.data dataset from a Pandas Dataframe
    """
    dataframe = dataframe.copy()
    if(text_processed):
        processed_text = dataframe.pop('text_processed')
        ds = tf.data.Dataset.from_tensor_slices(dict(dataframe))
        ds_processed = tf.data.Dataset.from_tensors(dict(processed_text))
        ds = tf.data.Dataset.zip((ds,ds_processed))
    else:
        ds = tf.data.Dataset.from_tensor_slices(dict(dataframe))

    if shuffle:
        ds = ds.shuffle(buffer_size=len(dataframe))
    ds = ds.batch(batch_size)
    return ds

def age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def convert_categorical_data(df, col, is_caregiver = False):
    """
    Convert categorical data that splited by space to their own column in pandas dataframe , making them like one hot encoded
    """
    ### Join every string in every row, split the result, pull out the unique values.
    genres = np.unique(' '.join(df[col]).split(' '))
    ### Drop 'NA'
    genres = np.delete(genres, np.where(genres == ''))
    if(not is_caregiver):
        for genre in genres:
            df[genre] = df[col].str.contains(genre).astype('int')
    else:
        for genre in genres:
            df['Caregiver-'+genre] = df[col].str.contains(genre).astype('int')
    df.drop(col, axis=1, inplace=True)

def change_column_name(df, old_name, new_name):
    """
    replace list of column name in old_name to new colum name in new_name
    the order of old_name and new_name need to be exact
    """
    res = {old_name[i]: new_name[i] for i in range(len(new_name))}
    df.rename(columns=res, inplace=True)

def Merge(dict1, dict2):
    """
    Python code to merge dict
    """
    res = {**dict1, **dict2}
    return res

def unpack_caregiver_snapshot(data):
    """

    :param data: data is a snapshot list of chatroom collection
    :return: list of caregiver in form of dictionary
    """
    desired_keys = ["problems", "birthday", "gender", "caregiver_id", "text", "user_id"]
    # this unpack the value of snapshot list and turn the snapshot into dictionary also add aditional key for caregiver_id
    caregiver_dict_unpacked = map(lambda feature: Merge(feature.to_dict(), {'caregiver_id': feature.id, 'user_id':feature.to_dict()['caregiver'].id}), data)

    # this unpack the snapshot in 'caregiver' snapshot and add them back to main dictionary
    caregiver_dict = map(lambda feature: Merge(feature, feature.pop('caregiver').get().to_dict()),
                         caregiver_dict_unpacked)

    #check for room capacity
    caregiver_dict = filter(lambda feature: feature['max_user'] > len(feature['users']) , caregiver_dict)

    # this seperate desired keys from unused keys
    caregiver_dict = map(lambda x: dict((k, x[k]) for k in desired_keys if k in x), caregiver_dict)


    # this convert birthday stamp into interger age
    caregiver_dict = map(lambda feature: Merge(feature, {'age': age(feature.pop('birthday'))}), caregiver_dict)

    return list(caregiver_dict)

def convert_caregiver_dictList_to_df(dictionary):
    """
    :param dictionary: list of dictionary
    :return: dataframe of the said dictionary
    """
    # Creates DataFrame.
    df = pd.DataFrame(dictionary)
    #change column name to feature according to the model
    change_column_name(df, ['problems','gender','caregiver_id','age'],['Caregiver_Tipe_Masalah','Caregiver_Gender','CAREGIVER_ID','Caregiver_Age'])
    #convert categorical data into their own column
    convert_categorical_data(df, "Caregiver_Tipe_Masalah", is_caregiver = True)
    #fill missing column with default value
    fill_non_existent_column(df, is_caregiver = True)
    return df


def unpack_user_snapshot(data):
    print(type(data))
    if (type(data) != list):
        data = [data]
    print(type(data))
    data = convert_snapshot(data, desired_key=["problems", "gender", "birthday", "text"])
    data = map(lambda feature: Merge(feature, {'age': age(feature.pop('birthday'))}), data)

    return data


def convert_user_dictList_to_df(dictionary):
    """
    :param dictionary: list of dictionary
    :return: dataframe of the said dictionary
    """
    # Creates DataFrame.
    df = pd.DataFrame(dictionary)
    # change column name to feature according to the model
    change_column_name(df, ['problems', 'gender', 'caregiver_id', 'age'],
                       ['Tipe_Masalah', 'Gender', 'CAREGIVER_ID', 'Age'])
    # convert categorical data into their own column
    convert_categorical_data(df, "Tipe_Masalah", is_caregiver=False)
    # fill missing column with default value
    fill_non_existent_column(df, is_caregiver=False)
    return df



def turn_firestore_vector_to_df(firestore_documents, identifiers: str, feature: str,):
    """
    :param firestore_documents: list of firestore documents
    :param identifiers: identifier name , this is usually a room id
    :param feature: feature name , i usually use vector as a name
    :return: DataFrame
    """
    firestore_documents_dict_unpacked = map(lambda document: Merge(document.to_dict(), {identifiers: document.id}),
                                            firestore_documents)
    firestore_documents_dict_unpacked = map(lambda document: Merge(document[feature], {identifiers: document[identifiers]}),
                                            firestore_documents_dict_unpacked)
    firestore_documents_dict_unpacked = [turn_vector_to_df(element, identifiers, feature) for element in
                                         list(firestore_documents_dict_unpacked)]
    return pd.DataFrame.from_dict(list(firestore_documents_dict_unpacked))


def turn_vector_to_df(dictionary, identifiers: str, feature: str, minus=1, ):
    data_list = list()
    # -1 because theres 1 item thats not a vector,
    for i in range(len(dictionary.keys()) - minus):
        data_list.append(np.float32(dictionary[f"{i}"]))

    data_result = {identifiers:dictionary[identifiers], feature : np.array(data_list)}

    return data_result

