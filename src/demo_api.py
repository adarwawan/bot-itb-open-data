import json
from flask import Flask, render_template
from flask_cors import CORS, cross_origin
from flask import Response
from flask import request, jsonify
import os
from os.path import basename

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def hello():
	return "HAI"

@app.route("/academic")
def academica():
    return render_template('academic.html')

@app.route("/crawl-academic", methods=['POST'])
@cross_origin()
def extractRuleBased():
    print("AAAAAAAAAAAAAAAa")
    req = {}
    req['name'] = request.form['ListURL']
    print(req['name'])
    req['email']=request.form['URLAccepted']
    print(req['email'])
    filename = req['name'].encode('utf-8')
    with open(filename, 'r') as myfile:
        positive = myfile.read().splitlines()
    
    req['text'] = positive
    js = json.dumps(req)
    print(req)
    return Response(js, status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("5000")
    )