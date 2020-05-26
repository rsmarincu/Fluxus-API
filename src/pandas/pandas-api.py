from flask import Flask, request, send_file, make_response
from flask_restful import Resource, Api, reqparse
import json
from flask_cors import CORS
import pandas as pd
from werkzeug.datastructures import FileStorage



app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('file', type=FileStorage, location='files')
parser.add_argument('labels', type=str, action='append')

class Hello(Resource):
    def get(self):
        return {"message":"Hello from the pandas endpoint!"}

class Labels(Resource):
    def post(self):
        data = parser.parse_args()
        file_ = data['file']
        csvfile = pd.read_csv(file_.stream)
        labels = list(csvfile.columns)
        return labels

class Columns(Resource):
    def post(self):
        data = parser.parse_args()
        file_ = data['file']
        labels = data['labels']
        csvfile = pd.read_csv(file_.stream)
        resp = make_response(csvfile[labels].to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"   
        return resp

api.add_resource(Hello,'/hello/')
api.add_resource(Labels,'/labels/')
api.add_resource(Columns,'/columns/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
