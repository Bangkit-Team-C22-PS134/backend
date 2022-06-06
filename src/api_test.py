import os

import pandas as pd
from flask import Flask, jsonify, json, request
from flask_restful import Api, Resource, reqparse, abort
import threading
import logging
from keras.models import load_model
from  circle_data_model import  circle_utility
from circle_data_model import generate_saved_model
import tensorflow_recommenders as tfrs
from werkzeug.exceptions import BadRequest
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
api = Api(app)
# this set up ML model
MAIN_TEXT_MODEL = generate_saved_model.model_nlm_v1
MAIN_USER_MODEL =  generate_saved_model.model.user_model
MAIN_CAREGIVER_MODEL = generate_saved_model.model.caregiver_model
TEXT_INDEX = tfrs.layers.factorized_top_k.BruteForce(MAIN_TEXT_MODEL)
INDEX = tfrs.layers.factorized_top_k.BruteForce(MAIN_USER_MODEL)

#Variable for dataframe
CAREGIVER_DATAFRAME = None
CAREGIVER_DS = None

# this set up firestore auth and client , also using environment variable to store private key
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
db_ref_userPref = db.collection('users')
db_key = db.collection('api_keys').document("matching_setting_api_keys")
db_chat_room_pref = db.collection('chat_room_pref')

# this set up the api resources and request json
video_post_args = reqparse.RequestParser()
video_post_args.add_argument("name", type=str, help="Name of the video is required", required=False)
video_post_args.add_argument("likes", type=int, help="Likes on the video is required", required=False)
video_post_args.add_argument("views", type=int, help="Views of the video is required", required=False)

user_args = reqparse.RequestParser()
user_args.add_argument("user_id", type=str, help="User ID is needed" , required=True)


# this set up firebase listening document for changes in api_keys

# Create an Event for notifying main thread.
callback_done_apikey = threading.Event()
callback_done_chatRoomPrefs = threading.Event()

# Create a callback on_snapshot function to capture changes
def on_snapshot_apikey(doc_snapshot, changes, read_time):
    global api_key
    for doc in doc_snapshot:
        api_key = doc.get("api_key")
    callback_done_apikey.set()

# Create a callback on_snapshot function to capture changes
def on_snapshot_chatRoomPrefs(doc_snapshot, changes, read_time):
    global INDEX , TEXT_INDEX
    data = circle_utility.unpack_caregiver_snapshot(doc_snapshot)
    data = circle_utility.convert_caregiver_dictList_to_df(data)
    caregiver_ds = circle_utility.df_to_dataset(data)
    # update this
    TEXT_INDEX.index_from_dataset(
       caregiver_ds.map(lambda features: (features['CAREGIVER_ID'], MAIN_TEXT_MODEL([features['text']])))
    )


    # update_this
    INDEX.index_from_dataset(
        caregiver_ds.map(lambda features: (features['CAREGIVER_ID'], MAIN_CAREGIVER_MODEL(features)))
    )
    callback_done_apikey.set()

# Watch the document
doc_watch_apikey = db_key.on_snapshot(on_snapshot_apikey)
doc_watch_chatRoomPrefs = db_chat_room_pref.on_snapshot(on_snapshot_chatRoomPrefs)

def get_error_msg():
    if app.config.get("FAB_API_SHOW_STACKTRACE"):
        return app.format_exc()
    return "Fatal error"


def abort_if_user_id_doesnt_exist(data):
    print("from func" , data.exists)
    if (not data.exists):
        abort(404, message="Could not find the user...")


def abort_if_video_exists(id):
    if (db_ref_userPref.document(id).get().exists):
        abort(409, message="Video already exists with that ID...")


def check_api_keys(key):
    if (api_key != key):
        abort(401, message="Unauthorized Access")

class match_user_resource(Resource):
    def get(self, id):
        # mulai processing metode get
        # return list semua user
        return 0


class Video(Resource):
    def get(self, id):
        #mulai processing metode get

        try:
            args = video_post_args.parse_args()
            check_api_keys(request.headers.get('user-api-key'))

            data = db_ref_userPref.document(id).get()
            abort_if_user_id_doesnt_exist(data)
            return json.dumps(data.to_dict()), 200
        except BadRequest as e:
            print(request)
            return str(e), 400
        except Exception as e:
            logging.exception(e)
            return str(e), 500

    def post(self, id):
        try:
            args = video_post_args.parse_args()
            check_api_keys(args['api_key'])

            abort_if_video_exists(id)

            db_ref_userPref.document(id).set(args)
            return json.dumps({"success": True}), 200
        except BadRequest as e:
            return str(e), 400
        except Exception as e:
            logging.exception(e)
            return str(e), 500

    def delete(self, id):
        try:
            args = video_post_args.parse_args()
            check_api_keys(args['api_key'])

            abort_if_user_id_doesnt_exist(id)
            return '', 204
        except BadRequest as e:
            return str(e), 400
        except Exception as e:
            logging.exception(e)
            return str(e), 500

api.add_resource(Video, "/video/<string:id>")
api.add_resource(match_user_resource, "/user/<string:id>")

@app.route("/user/match", methods=["GET"])
def match_user():
    # get data from firestore and check if its exist
    user_id = request.args.get("user_id", "notvalid")
    k_value = int(request.args.get("k_value", 3))
    if (user_id is None):
        return "id is not provided", 400

    check_api_keys(request.headers.get('user-api-key'))
    data = db_ref_userPref.document(str(user_id)).get()
    abort_if_user_id_doesnt_exist(data)

    # process the data
    data = list(circle_utility.unpack_user_snapshot(data))
    data = circle_utility.convert_user_dictList_to_df(data)

    # turn dataframe into list and pack the value with brackets
    data = data.to_dict('records')[0]
    for k, v in data.items():
        data[k] = [v]

    _, recommendation = INDEX(data, k=k_value)
    data = {
        "recommendation": recommendation[0].numpy().tolist()
    }
    data = list(map(lambda string: string.decode("utf-8").strip(), data['recommendation']))
    return json.dumps(data), 200

@app.route("/")
def index():
    """
    :param id: document id of chat_room that need to be updated
    :return: 200 http code
    """
    return "what"


if __name__ == "__main__":
    app.run(debug=True)  # dont run debug true if its in production
