
from flask import Flask, json, request
from flask_restful import Api, Resource, reqparse, abort
import threading
from circle_data_model import circle_utility
import Model_Data_Manager
from firebase_admin import credentials, firestore, initialize_app
import os

app = Flask(__name__)
api = Api(app)
#json.loads(os.environ["FIREBASE_KEY"] , strict=False)
# this set up firestore auth and client , also using environment variable to store private key
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
db_ref_userPref = db.collection('users')
db_key = db.collection('api_keys').document("matching_setting_api_keys")
db_chat_room_pref = db.collection('chat_room_pref').where(u'is_open',u'==',True)
#initialize initial index
Model_Data_Manager.add_data_in_dataframe(db_chat_room_pref.get())
api_key = db_key.get()

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
    callback_done_chatRoomPrefs.set()

#this variable to ensure that only happen once in 1 instance
cold_boot = True
# Create a callback on_snapshot function to capture changes
def on_snapshot_chatRoomPrefs(doc_snapshot, changes, read_time):
    global cold_boot
    print(u'Callback received query snapshot.')
    for change in changes:
        if change.type.name == 'ADDED' and not cold_boot:
            Model_Data_Manager.add_data_in_dataframe(change.document)
            print(f'New data: {change.document.id}')
        elif change.type.name == 'MODIFIED':
            Model_Data_Manager.update_dataframe(change.document)
            print(f'Modified data: {change.document.id}')
        elif change.type.name == 'REMOVED':
            Model_Data_Manager.delete_data_in_dataframe(change.document)
            print(f'Removed data: {change.document.id}')
    cold_boot = False
    callback_done_chatRoomPrefs.set()

# Watch the document
doc_watch_apikey = db_key.on_snapshot(on_snapshot_apikey)
doc_watch_chatRoomPrefs = db_chat_room_pref.on_snapshot(on_snapshot_chatRoomPrefs)

def get_error_msg():
    if app.config.get("FAB_API_SHOW_STACKTRACE"):
        return app.format_exc()
    return "Fatal error"


def abort_if_user_id_doesnt_exist(data):
    if (not data.exists):
        abort(404, message="Could not find the user...")

def check_api_keys(key):
    global api_key
    if(api_key is None):
        api_key = db_key.get()
    if (api_key != key):
        abort(401, message="Unauthorized Access")

class match_user_resource(Resource):
    def get(self, id):
        # mulai processing metode get
        # return list semua user
        return 0

@app.route("/user/match", methods=["GET"])
def match_user():

    if request.method != 'GET':
        return "405 Method Not Allowed", 405
    # get data from firestore and check if its exist
    user_id = request.args.get("user_id", None)
    text = request.args.get("text", None)
    k_value = int(request.args.get("k_value", 3))
    if (user_id is None):
        return "id is not provided", 400
    if (text is None):
        return "text is not provided, it should be provided as url parameters", 400

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
    recommendation = Model_Data_Manager.predict(text,k_value)

    if (type(recommendation) == str):
        return json.dumps(recommendation), 404

    data = {
        "recommendation": recommendation[0].numpy().tolist()
    }
    data = list(map(lambda string: string.decode("utf-8").strip(), data['recommendation']))
    return json.dumps(data), 200


@app.route("/room/create", methods=["POST"])
def create_room():
    if request.method != 'POST':
        return "405 Method Not Allowed", 405
    room_data = request.form
    print(room_data)
    return 200

@app.route("/")
def index():
    """
    :param id: document id of chat_room that need to be updated
    :return: 200 http code
    """
    return "This Services is exclusive to our Circle App \n You can find more information on our github"


if __name__ == "__main__":
    app.run(debug=True)  # dont run debug true if its in production
