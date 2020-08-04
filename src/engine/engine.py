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
parser.add_argument('target', type=str)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
