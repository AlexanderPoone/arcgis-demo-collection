##############################################
#
#	Automatic Bug Triage and Assignment by Topic Modelling
#   Draft only
#
#	Author:			Alex Poon
#	Date:		  	Sep 28, 2021
#	Last update:  	Sep 29, 2021
#
##############################################

from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS
from urllib.parse import unquote as u
from urllib.request import urlopen, Request

from gensim import corpora, models, similarities, downloader			# Topic Modelling
import matplotlib.pyplot as plt


app = Flask(__name__)
CORS(app)

#  Possibly a MongoDB database

#  By topic modelling, word cloud maybe
def topicModelling():
	# Stream a training corpus directly from S3.
	corpus = corpora.MmCorpus("s3://path/to/corpus")

	# Train Latent Semantic Indexing with 200D vectors.
	lsi = models.LsiModel(corpus, num_topics=20)

	# Convert another corpus to the LSI space and index it.
	index = similarities.MatrixSimilarity(lsi[another_corpus])

	# Compute similarity of a query vs indexed documents.
	sims = index[query]


@app.route('/issuesToTopic', methods = ['POST'])
def issues_to_topic(repos=['https://github.com/SoftFeta/SWEnggTestRepo']):
	pass

if __name__ == "__main__":
    app.run(host='0.0.0.0', ssl_context=('cert.pem', 'privkey.pem'))