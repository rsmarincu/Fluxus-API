from flask import Flask, request, send_file, make_response
from flask_restful import Resource, Api, reqparse
import json
from flask_cors import CORS
from functools import reduce
from werkzeug.datastructures import FileStorage
import pandas as pd

app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('as', type=int, action='append')
parser.add_argument('bs', type=int, action='append')
parser.add_argument('file', type=FileStorage, location='files')

class Hello(Resource):
    def get(self):
        return {"message":"Hello from the math endpoint"}

class Add(Resource):
    def get(self):
        args = parser.parse_args()
        if args['file'] == None:
            if args['bs'] == None:
                to_return = reduce((lambda x, y: x + y), args['as'])
            elif len(args['bs']) == 1:
                to_return = [x + args['bs'][0] for x in args['as']]
            else:
                to_return = list(map(lambda x, y : x + y, args['as'] ,args['bs']))
            return to_return
        else:
            file_ = args['file']
            csvfile = pd.read_csv(file_.stream)
            numeric = [col for col in csvfile if csvfile[col].dtype.kind != 'O']
            csvfile[numeric] += args['bs'][0]
            resp = make_response(csvfile.to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"   
            return resp

class Subtract(Resource):
    def get(self):
        args = parser.parse_args()
        if args['file'] == None:
            if args['bs'] == None:
                to_return = reduce((lambda x, y: x - y), args['as'])
            elif len(args['bs']) == 1:
                to_return = [x - args['bs'][0] for x in args['as']]
            else:
                to_return = list(map(lambda x, y : x - y, args['as'] ,args['bs']))
            return to_return
        else:
            file_ = args['file']
            csvfile = pd.read_csv(file_.stream)
            numeric = [col for col in csvfile if csvfile[col].dtype.kind != 'O']
            csvfile[numeric] -= args['bs'][0]
            resp = make_response(csvfile.to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"   
            return resp

class Multiply(Resource):
    def get(self):
        args = parser.parse_args()
        if args['file'] == None:
            if args['bs'] == None:
                to_return = reduce((lambda x, y: x * y), args['as'])
            elif len(args['bs']) == 1:
                to_return = [x * args['bs'][0] for x in args['as']]
            else:
                to_return = list(map(lambda x, y : x * y, args['as'] ,args['bs']))
            return to_return
        else:
            file_ = args['file']
            csvfile = pd.read_csv(file_.stream)
            numeric = [col for col in csvfile if csvfile[col].dtype.kind != 'O']
            csvfile[numeric] *= args['bs'][0]
            resp = make_response(csvfile.to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"   
            return resp

class Divide(Resource):
    def get(self):
        args = parser.parse_args()
        if args['file'] == None:
            if args['bs'] == None:
                to_return = reduce((lambda x, y: x / y), args['as'])
            elif len(args['bs']) == 1:
                to_return = [x / args['bs'][0] for x in args['as']]
            else:
                to_return = list(map(lambda x, y : x / y, args['as'] ,args['bs']))
            return to_return
        else:
            file_ = args['file']
            csvfile = pd.read_csv(file_.stream)
            numeric = [col for col in csvfile if csvfile[col].dtype.kind != 'O']
            csvfile[numeric] /= args['bs'][0]
            resp = make_response(csvfile.to_csv())
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"] = "text/csv"   
            return resp


api.add_resource(Add,'/add/')
api.add_resource(Subtract,'/subtract/')
api.add_resource(Multiply,'/multiply/')
api.add_resource(Divide,'/divide/')

api.add_resource(Hello,'/hello/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
