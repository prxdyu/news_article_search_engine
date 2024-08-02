from flask import Flask,request,render_template,jsonify
from src.components.annoy_indexing import AnnoyIndexer
from src.pipeline.search_pipeline import SearchPipeline
from src.utils.utils import *
from datetime import datetime

import pandas as pd
import sys
import os
import json
import pickle

import os

bucket_name = os.getenv('BUCKET_NAME')
print(f'BUCKET_NAME: {bucket_name} (type: {type(bucket_name)})')


# downloading the index if it does'nt present in the local
index_path = 'artifacts/annoy_index.ann'
if not os.path.exists(index_path):
    index_name = "annoy_index.ann"
    get_data_from_s3(index_name,index_path)


# downloading metadata
metadata_path = "artifacts/metadata.json"
if not os.path.exists(metadata_path):
    metadata_name = "metadata.json"
    get_data_from_s3(metadata_name, metadata_path)


# downloading metadata and mapping file
mapping_path = "artifacts/section_article_mapping.pkl"
if not os.path.exists(mapping_path):
    mapping_name = "section_article_mapping.pkl"
    get_data_from_s3(mapping_name, mapping_path)


# loading the index
index = AnnoyIndexer()
index.load_index(index_path)


# loading the metadata about articles
with open(metadata_path,'r') as file:
    metadata = json.load(file)

# Load the data from the pickle file
with open(mapping_path, 'rb') as file:
    mapping = pickle.load(file)




# creating a flask app
app=Flask(__name__)


# defining the ping route
@app.route('/ping',methods=['GET'])
def ping():
    """Ping the server to check the availability"""
    # defining the ping message
    ping_message = {"status":"OK",
                    "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
    return jsonify(ping_message)



# defining the route for getting results in json
@app.route("/api/search",methods=['POST'])
def search_api():
    """Searches for relevant articles from the index"""
    
    # accessing the request object
    req = request.get_json()

    # getting the search query and k from the request obejct
    query = [req["query"]]
    k = req['k']

    # searching for the relevant articles
    searcher = SearchPipeline()
    results = searcher.search(index, query, k, mapping, metadata)

    return jsonify(results)
    




# defining the route for getting results in webpage
@app.route("/search",methods=['GET','POST'])
def search_web():
    """
    Searches for relevant articles from the index
    returns the result in the form of webpage
    """
    if request.method == 'POST':
        # accessing the request object
        req = request.form

        # getting the search query and k from the request object
        query = [req["query"]]
        k = int(req["k"])
        #k = int(req.get("k", 3))  

        # searching for the relevant articles
        searcher = SearchPipeline()
        results = searcher.search(index, query, k, mapping, metadata)
        return render_template('index.html',query=query[0],k=k,results=results[0]['results'])
    
    else:
        return render_template('index.html',data={})


if __name__=="__main__":
    app.run(host="0.0.0.0")