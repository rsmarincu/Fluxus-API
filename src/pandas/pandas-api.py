from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import json
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('as', action='append')
parser.add_argument('bs', action='append')

class GetMessage(Resource):
    def get(self):
        return {"message":"Hello from the pandas endpoint"}


api.add_resource(GetMessage,'/pandas/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
