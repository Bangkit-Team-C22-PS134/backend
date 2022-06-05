import os

import pandas as pd
from flask import Flask, jsonify, json, request
from flask_restful import Api, Resource, reqparse, abort
import threading
import logging
import tensorflow as tf
from json import loads
from os import getenv
# from keras import models
from werkzeug.exceptions import BadRequest
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
api = Api(app)
# this set up ML model
MAIN_TEXT_MODEL = tf.keras.models.load_model('../resources/saved_model/text_query_v1')
MAIN_USER_MODEL = tf.keras.models.load_model('../resources/saved_model/user_query_v1')
MAIN_CAREGIVER_MODEL = tf.keras.models.load_model('../resources/saved_model/caregiver_query_v1')

#Variable for dataframe
CAREGIVER_DATAFRAME = None
CAREGIVER_DS = None

# this set up firestore auth and client , also using environment variable to store private key
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
db_ref_userPref = db.collection('user_pref')
db_key = db.collection('api_keys').document("matching_setting_api_keys")
db_index = db.collection('chat_room_pref')

# this set up the api resources and request json
video_post_args = reqparse.RequestParser()
video_post_args.add_argument("name", type=str, help="Name of the video is required", required=False)
video_post_args.add_argument("likes", type=int, help="Likes on the video is required", required=False)
video_post_args.add_argument("views", type=int, help="Views of the video is required", required=False)


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
    for doc in doc_snapshot:
        print("===============================")
        print(doc.to_dict())
    print("===============================\n===============================")
    callback_done_apikey.set()

# Watch the document
doc_watch_apikey = db_key.on_snapshot(on_snapshot_apikey)
doc_watch_chatRoomPrefs = db_index.on_snapshot(on_snapshot_chatRoomPrefs)

def get_error_msg():
    if app.config.get("FAB_API_SHOW_STACKTRACE"):
        return app.format_exc()
    return "Fatal error"


def abort_if_video_id_doesnt_exist(data):
    if (not data.exists):
        abort(404, message="Could not find the video...")


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
            abort_if_video_id_doesnt_exist(data)
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

            abort_if_video_id_doesnt_exist(id)
            return '', 204
        except BadRequest as e:
            return str(e), 400
        except Exception as e:
            logging.exception(e)
            return str(e), 500

api.add_resource(Video, "/video/<string:id>")
api.add_resource(match_user_resource, "/user/<string:id>")

@app.route("/chat_room/update/<string:id>")
def update_index(id):
    """
    :param id: document id of chat_room that need to be updated
    :return: 200 http code
    """
    data = db_index.document(str(id)).get()
    abort_if_video_id_doesnt_exist(data)
    return json.dumps(data.to_dict()), 200

@app.route("/user/match/<string:id>")
def match_user(id):
    """
    :param id: user id and a document id
    :return: list of potential candidate in form of list of chatrooms document id
    """
    return 0


if __name__ == "__main__":
    app.run(debug=True)  # dont run debug true if its in production
