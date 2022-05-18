from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse, abort

from datetime import datetime
#from keras import models
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
api = Api(app)
#this set up ML model
#model = models.load_model('../resources/saved_model/my_model')

#this set up firestore auth and client
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
db_ref = db.collection('Videos')

video_post_args = reqparse.RequestParser()
video_post_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_post_args.add_argument("likes", type=int, help="Likes on the video is required", required=True)
video_post_args.add_argument("views", type=int, help="Views of the video is required", required=True)
Videos = {}

def abort_if_video_id_doesnt_exist(id):
    print(db_ref.document(id).exist())
    if(not db_ref.document(id).exist()):
        abort(404 , message="Could not find the video...")

def abort_if_video_exists(id):
    if(db_ref.document(id).exist()):
        abort(409, message="Video already exists with that ID...")

class Video(Resource):
    def get(self, id):
        print(db_ref.document(id).exist())
        abort_if_video_id_doesnt_exist(id)
        return jsonify(db_ref.document(id)), 200

    def post(self, id):
        abort_if_video_exists(id)
        args = video_post_args.parse_args()
        try:
            db_ref.document(id).set(args)
            return jsonify({"success": True}), 200
        except Exception as e:
            return jsonify({"message": f"An Error Occured: {e}"}), 500

        Videos[id] = args
        return Videos[id], 201

    def delete(self, id):
        abort_if_video_id_doesnt_exist(id)
        del Videos[id]
        return '', 204

api.add_resource(Video, "/video/<int:id>")



@app.route('/', methods=['POST', 'GET'])
def index():
    return str("hello")

@app.route('/<float:prediction>', methods=['POST', 'GET'])
def predict_page(prediction):
    prediction_result = model.predict([float(prediction)])
    return str(prediction_result)


if __name__ == "__main__":
    app.run(debug=True) #dont run debug true if its in production

