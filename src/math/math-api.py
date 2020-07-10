from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import json
from flask_cors import CORS
from functools import reduce


app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('as', type=int, action='append')
parser.add_argument('bs', type=int, action='append')


class Hello(Resource):
    def get(self):
        return {"message":"Hello from the math endpoint"}

class Add(Resource):
    def get(self):
        args = parser.parse_args()
        if args['bs'] == None:
            to_return = reduce((lambda x, y: x + y), args['as'])
        else:
            to_return = list(map(lambda x, y : x + y, args['as'] ,args['bs']))
        return to_return

class Subtract(Resource):
    def get(self):
        args = parser.parse_args()
        if args['bs'] == None:
            to_return = reduce((lambda x, y: x - y), args['as'])
        else:
            to_return = list(map(lambda x, y : x - y, args['as'] ,args['bs']))
        return to_return

class Multiply(Resource):
    def get(self):
        args = parser.parse_args()
        if args['bs'] == None:
            to_return = reduce((lambda x, y: x * y), args['as'])
        else:
            to_return = list(map(lambda x, y : x * y, args['as'] ,args['bs']))
        return to_return

class Divide(Resource):
    def get(self):
        args = parser.parse_args()
        if args['bs'] == None:
            to_return = reduce((lambda x, y: x / y), args['as'])
        else:
            to_return = list(map(lambda x, y : x / y, args['as'] ,args['bs']))
        return to_return

api.add_resource(Add,'/add/')
api.add_resource(Subtract,'/subtract/')
api.add_resource(Multiply,'/multiply/')
api.add_resource(Divide,'/divide/')

api.add_resource(Hello,'/hello/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
