import os

from flask import Flask, jsonify, json, request
from flask_restful import Api, Resource, reqparse, abort
import threading
import logging
from circle_data_model import User
from json import loads
from os import getenv
#from keras import models
from werkzeug.exceptions import BadRequest
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
api = Api(app)
#this set up ML model
#model = models.load_model('../resources/saved_model/my_model')
#this set up firestore auth and client , also using environment variable to store private key
cred = credentials.Certificate(json.loads(os.environ["FIREBASE_KEY"] , strict=False))
default_app = initialize_app(cred)
db = firestore.client()
db_ref = db.collection('Videos')
db_key = db.collection('api_keys').document("matching_setting_api_keys")

#this set up the api resources and request json
video_post_args = reqparse.RequestParser()
video_post_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_post_args.add_argument("likes", type=int, help="Likes on the video is required", required=True)
video_post_args.add_argument("views", type=int, help="Views of the video is required", required=True)
video_post_args.add_argument("api_key", type=str , help="Api_keys is needed to post a video", required = True)
Videos = {}


#this set up firebase listening document for changes in api_keys

# Create an Event for notifying main thread.
callback_done = threading.Event()

# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    global api_key
    for doc in doc_snapshot:
        api_key = doc.get("api_key")
    callback_done.set()

doc_ref = db_key
# Watch the document
doc_watch = doc_ref.on_snapshot(on_snapshot)

def get_error_msg():
    if app.config.get("FAB_API_SHOW_STACKTRACE"):
        return app.format_exc()
    return "Fatal error"

def abort_if_video_id_doesnt_exist(data):
    if(not data.exists):
        abort(404 , message="Could not find the video...")

def abort_if_video_exists(id):
    if(db_ref.document(id).get().exists):
        abort(409, message="Video already exists with that ID...")

def check_api_keys(key):
    if(api_key != key):
        abort(401 , message="Unauthorized Access")

class Video(Resource):
    def get(self, id):

        try:
            args = video_post_args.parse_args()
            check_api_keys(args['api_key'])

            data = db_ref.document(id).get()
            abort_if_video_id_doesnt_exist(data)
            return json.dumps(data.to_dict()), 200
        except BadRequest as e:
            return str(e), 400
        except Exception as e:
            logging.exception(e)
            return str(e), 500


    def post(self, id):
        try:
            args = video_post_args.parse_args()
            check_api_keys(args['api_key'])

            abort_if_video_exists(id)

            db_ref.document(id).set(args)
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
            del Videos[id]
            return '', 204
        except BadRequest as e:
            return str(e), 400
        except Exception as e:
            logging.exception(e)
            return str(e), 500

api.add_resource(Video, "/video/<string:id>")



@app.route("/<int:id>")
def hello_world(id):
    data = db_ref.document(str(id)).get()
    abort_if_video_id_doesnt_exist(data)
    return json.dumps(data.to_dict()), 200

if __name__ == "__main__":
    app.run(debug=True) #dont run debug true if its in production

