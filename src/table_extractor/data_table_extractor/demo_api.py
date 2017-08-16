from rule_based_extractor import RuleBasedExtractor
from feature_extractor import RowFeatureExtractor
from Learner import CRFLearner
from data_extractor_2 import DataExtractor
from toponym_indexing import ToponymDetector
import json
from flask import Flask
from flask.ext.cors import CORS, cross_origin
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
	
@app.route("/rule-based", methods=['POST'])
@cross_origin()
def extractRuleBased():
	result_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\DemoData\\HTMLTable\\"
	req = request.get_json(force=True)
	# bsname = basename(req['fullpath'])
	# pre, ext = bsname.split('.')
	rbe = RuleBasedExtractor(req['fullpath'], result_dir)
	body_soup = rbe.getBody()
	tables = rbe.getCandidatesTable(body_soup)
	js = json.dumps(tables)
	# print js
	return Response(js, status=200, mimetype='application/json')
	# return a['nondata']

@app.route("/get-features", methods=['POST'])
@cross_origin()
def getFeatures():
	result_dir = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\DemoData\\FeaturesFile\\"
	req = request.get_json(force=True)
	rfe = RowFeatureExtractor(req['fullpath'], result_dir)
	table_soup = rfe.getTable()
	featuresfile = rfe.processTable(table_soup)
	js = {
		"featuresfile" : featuresfile
	}
	return Response(json.dumps(js), status=200, mimetype='application/json')

@app.route("/predict", methods=['POST'])
@cross_origin()
def predict():
	req = request.get_json(force=True)
	featurefile = req['featurefile']
	modelfile = req['modelfile']
	crf = CRFLearner(300, False)
	test_corpus = crf.prepareATest(featurefile)
	# print test_corpus
	predictions = crf.predictAtable([test_corpus], modelfile)
	# print predictions
	js = json.dumps(predictions[0])
	return Response(js, status=200, mimetype='application/json')

@app.route("/extract-data", methods=['POST'])
@cross_origin()
def extractData():
	req = request.get_json(force=True)
	tablefile = req['htmlfile']
	labelfile = req['labelfile']
	# tablefile = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\HTML\\eval2\\kasuskhusus\\levelgroup.html"
	# labelfile = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\Features\\kasuskhusus\\levelgroup.txt"

	extractor = DataExtractor()
	extracts = extractor.extract_table(tablefile,labelfile)
	js = json.dumps(extracts)
	return Response(js, status=200, mimetype='application/json')

@app.route("/detect-toponym", methods=['POST'])
@cross_origin()
def detectToponym():
	req = request.get_json(force=True)
	jsonfile = req['jsonfile']
	with open(jsonfile, 'r') as infile:
		data = infile.read()
	td = ToponymDetector()
	js = json.loads(data)
	lok = []
	td.get_leave_keys(js['table_data'], lok)
	topo_key = td.get_toponym_keys(lok, js['table_data'])
	print lok
	print topo_key
	if len(topo_key) > 0:
		td.add_toponym_index(js['table_data'], topo_key)
		retval = json.dumps(js)
	else:
		retval = json.dumps(js)
	return Response(retval, status=200, mimetype='application/json')
