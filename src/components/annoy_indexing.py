""" THIS PYTHON FILE CONTAINS THE CLASS FOR INDEXING EMBEDDINGS USING ANNOY"""

# importing the required libraries
import numpy as np
from annoy import AnnoyIndex
import os
from functools import reduce


from src.utils.utils import *
from src.logger.logger import logging

from src.components import config

# building a class for storing and searching in the index
class AnnoyIndexer:

    """ A class to built and search an annoy index """

    def _init_(self):
        self.index=None


    
    def build_index(self,embeddings_path:str,index_path:str):
        """ 
        builds a similarity index using the embeddings dictionary passed and returns the index path
        
        embeddings_path : path of the dictionary with index as the key and embeddings as value 
         
        """
        logging.info("Indexing has started")


        # importing the embedding json file
        with open(embeddings_path, 'r') as file:
            embeddings_dict = json.load(file)
        
        # defining the index path
        index_path = "artifacts/annoy_index.ann"


        # extracting indices and embeddings from the dictionary
        indices = embeddings_dict.keys()
        embeddings = list(embeddings_dict.values())

        # checking if the embedding size is equal to the embedding size specified in the CONFIG file
        assert len(embeddings[0])==config.EMBEDDING_SIZE,f"Embedding size {len(embeddings[0])} does not match with CONFIG EMBEDDING_SIZE {config.EMBEDDING_SIZE} "

        # creating the index
        self.index = AnnoyIndex(config.EMBEDDING_SIZE,config.ANNOY_METRIC)
        logging.info("Created an empty index")
        
        # inserting the embeddings into the index
        for index,embedding in zip(indices,embeddings):
            self.index.add_item(int(index),embedding)

        logging.info("Succesfully inserted embeddings into the index")

        # building and saving the annoy index
        self.index.build(config.ANNOY_N_TREE)
        logging.info("Successfully built the index")

        self.index.save(index_path)
        logging.info("Succesfully saved the index")

        return index_path
       
            
       

       


    def search(self, query_embedding:list, k:int, ids_lookup:dict=None)->list:
        """
        searches for the K nearest neighbors for the given query embedding

        query_embedding    : list of embedding of the queries we want to search
        k                  : no of nearest neightbor that we want to return
        ids_lookup         : a dictionary mapping where keys are article_ids and values are the embeddings
         
        returns a list of tuples of the form  [ (id,distance) , (id,distance) ]
        """

        # defining an empty list to store the results
        results = []

        for query in query_embedding:
            # getting the k nearest neightbor for the embedding
            result = self.index.get_nns_by_vector(query, k, include_distances=True)
            # result will be list of tuple of lists ( [a,b,c],[0.1,0.5,0.7] ) where a,b,c are indices(section_ids) and 0.1,0.5,0.7 are the similarity metrics
            # now we want to map the section_ids to article_ids
            ids =list( map( 
                           lambda x:ids_lookup[int(x)],
                            result[0]
                          ) )
            # sorting the result based on the metrics in descending order
            res = sorted(set(zip(ids,result[1])), key=lambda x:x[1], reverse=True)


            # appeding the nearest neighbors in the result list
            results.append(res)

        return results
    



    def save_index(self,index_path:str):
        """
        saves the index to the disk
        index_path: path where we want to store our index
        """
        self.index.save(index_path)
        logging.info(f"Index saved to {index_path}")

    


    def load_index(self,index_path:str):
        """
        loads the index from the disk
        index_path  : path of the index 
        """
        self.index = AnnoyIndex(config.EMBEDDING_SIZE, config.ANNOY_METRIC)
        self.index.load(index_path)
        logging.info(f"Index loaded from {index_path}")




if __name__=="__main__":

    obj=AnnoyIndexer()
    obj.build_index("artifacts/embeddings.json","artifacts/annoy_index.ann")
    