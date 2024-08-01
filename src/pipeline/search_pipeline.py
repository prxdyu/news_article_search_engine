import pandas as pd
import os
import sys
import pandas
import json
import pickle

from src.logger.logger import logging
from src.utils.utils import preprocess_text,get_embeddings,save_json
from src.components import config

from sentence_transformers import SentenceTransformer
from pprint import pprint
from src.components.annoy_indexing import AnnoyIndexer




class SearchPipeline:

    def __init__(self):
        pass

    # defining a function to search 
    def search(self, index, queries:list, k:int, ids_mapper:dict, metadata:dict)->list:
        """
        index      : index
        queries    : list of queries (strings)
        k          : no of neighbors to find
        ids_mapper : mapping from section_id to article_id
        """
        logging.info(f"Searching for {len(queries)} queries")


        # preprocessing the queries
        preprocessed_queries = list(map(lambda x:preprocess_text(x),queries))

        # getting the embeddings for the queries
        model = SentenceTransformer(config.EMBEDDING_MODEL)
        query_embeddings = get_embeddings(model,preprocessed_queries)

        # searching for the nearest neighbors
        search_results = index.search(query_embeddings,k,ids_mapper)   
        """ 
            
            structure of search_results if k=3 and we have 3 queries 
            [  
                [ (article_id,score),(article_id,score),(article_id,score) ],
                [ (article_id,score),(article_id,score),(article_id,score) ], 
                [ (article_id,score),(article_id,score),(article_id,score) ], 
            
            ]
        """
        # defining an empty list to store results
        results=[]

        # iterating through each query
        for i in range(len(search_results)):
            logging.info("Processing query: %s",queries[i])

            # creating a result variable for the ith query
            result={
                    "query":queries[i]
                    }
            result["results"]=[]
            skip = set()

            # iterating through the search results for the ith query
            for j in range(len(search_results[i])):

                if len(result["results"])>=k:
                    break
                # getting the article_id for the jth result of the ith query
                article_id = search_results[i][j][0]

                # checking if we already added this article_id in our result by checking if its present in the skip set
                if article_id in skip:
                    logging.info(f"Duplicate result -skipping: {article_id}")
                    continue

                # skipping the result if it has lesser score than our threshold
                score = search_results[i][j][1]
                if score<config.THRESHOLD_SCORE:
                    logging.info(f"Score below threshold -skipping: {article_id}")
                    continue

                # formatting the result
                formatted_result = {"article_id":article_id,
                                    "title":metadata[str(article_id)][0],
                                    "category":metadata[str(article_id)][1],
                                    "subcategory":metadata[str(article_id)][2],
                                    "score":score}
                # adding the formatted result to the result
                result['results'].append(formatted_result)
                # adding this article_id aka result to our skip set
                skip.add(article_id)

            # adding the results for the ith query in the results list
            results.append(result)
        
        logging.info("Search complete")
        return results
    

# CODE FOR TESTING PURPOSE
if __name__=="__main__":
    index = AnnoyIndexer()
    index.load_index('artifacts/annoy_index.ann')

    # loading the metadata about articles
    with open('artifacts/metadata.json','r') as file:
        metadata = json.load(file)

    # Load the data from the pickle file
    with open('artifacts/section_article_mapping.pkl', 'rb') as file:
        mapping = pickle.load(file)


    # queries = [lookup[i]["title"] for i in (0, 1)]
    queries = ["women entrepreneuship in india"]

    searcher = SearchPipeline()
    results  = searcher.search(index, queries, 3, mapping,metadata)

    pprint(results)
        




   