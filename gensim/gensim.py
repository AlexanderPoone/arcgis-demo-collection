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

from flask import Flask, jsonify, request, send_from_directory, abort, send_file
from urllib.parse import unquote as u
from urllib.request import urlopen, Request

from gensim import corpora, models, similarities, downloader			# Topic Modelling

#  Possibly a MongoDB database



#  By topic modelling, word cloud maybe

'''
def topicModelling():
	"https://github.com/SoftFeta/SWEnggTestRepo"

# Stream a training corpus directly from S3.
corpus = corpora.MmCorpus("s3://path/to/corpus")

# Train Latent Semantic Indexing with 200D vectors.
lsi = models.LsiModel(corpus, num_topics=200)

# Convert another corpus to the LSI space and index it.
index = similarities.MatrixSimilarity(lsi[another_corpus])

# Compute similarity of a query vs indexed documents.
sims = index[query]
'''