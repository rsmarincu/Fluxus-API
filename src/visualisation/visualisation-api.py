import io
import json
import pandas as pd

from flask import Flask, request, send_file, make_response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from matplotlib import pyplot as plt
from werkzeug.datastructures import FileStorage
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)
CORS(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('file', type=FileStorage, location='files')
parser.add_argument('x-axis', type=str)
parser.add_argument('y-axis', type=str)


class Hello(Resource):
    def get(self):
        return {"message":"Hello from the visualisation endpoint!"}

class BarPlot(Resource):
    def post(self):
        fig = Figure()
        args = parser.parse_args()
        file_ = args['file']
        csvfile = pd.read_csv(file_.stream)
        ax = fig.add_subplot(1,1,1)       
        csvfile.plot(ax=ax, kind='bar', x=args['x-axis'], y=args['y-axis'])
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        resp = make_response(output.getvalue())
        resp.mimetype = 'image/png'
        return resp

class Histogram(Resource):
    def post(self):
        fig = Figure()
        args = parser.parse_args()
        file_ = args['file']
        csvfile = pd.read_csv(file_.stream)
        ax = fig.add_subplot(1,1,1)       
        csvfile[args['x-axis']].plot(ax=ax, kind='hist')
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        resp = make_response(output.getvalue())
        resp.mimetype = 'image/png'
        return resp

api.add_resource(Hello,'/hello/')
api.add_resource(BarPlot,'/barplot/')
api.add_resource(Histogram,'/histogram/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5002')
