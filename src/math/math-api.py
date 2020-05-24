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
        return {"message":"Hello from the math endpoint"}

class Add(Resource):
    def post(self):
        args = parser.parse_args()
        to_return = [a + b for b in args['bs'] for a in args['as']]
        return to_return

class Subtract(Resource):
    def post(self):
        args = parser.parse_args()
        to_return = [a - b for b in args['bs'] for a in args['as']]
        return to_return


api.add_resource(Add,'/add/')
api.add_resource(Subtract,'/subtract/')

api.add_resource(GetMessage,'/hello/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
