from flask import Flask, render_template,request, redirect
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from keras import models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
api = Api(app)
model = models.load_model('../resources/saved_model/my_model')

Videos = {}
class Video(Resource):
    def get(self, id):
        return Videos[id]
    def post(self):
        return ""

api.add_resource(Video, "/helloworld/<string:name>")

class Todo(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow())

    def __repr__(self):
        return  '<Task %r>'% self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    return str("hello")

@app.route('/<float:prediction>', methods=['POST', 'GET'])
def predict_page(prediction):
    prediction_result = model.predict([float(prediction)])
    return str(prediction_result)


if __name__ == "__main__":
    app.run(debug=True) #dont run debug true if its in production

