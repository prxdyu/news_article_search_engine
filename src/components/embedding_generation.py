# importing the required libraries
import pandas as pd
import numpy as np
import os
import sys
from typing import List
from pathlib import Path

from dataclasses import dataclass,field


from sentence_transformers import SentenceTransformer

from src.logger.logger import logging
from src.exception.exception import CustomException 
from src.utils.utils import *


from config import EMBEDDING_MODEL

""" # Load the .env file to access the environment variables
from dotenv import load_dotenv
load_dotenv()
 """
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')

BUCKET_NAME = os.getenv('BUCKET_NAME')
FILE_NAME = "preprocessed.csv"





@dataclass
class EmbeddingConfig:

    # defining the path for saving the embeddings
    embeddings_path = os.path.join("artifacts", "embeddings.json")

   

class EmbeddingGeneration:

    def __init__(self):
        self.embedding_config = EmbeddingConfig()


    def initiate_embedding_generation(self,df_path):
        logging.info("Embedding generation has started")
        try:

            # reading the preprocessed data 
            df = pd.read_csv(df_path)
            logging.info("Successfully read preprocessed data for embedding generation")

            # defining the model
            model = SentenceTransformer(EMBEDDING_MODEL)

            # getting the embeddings
            embeddings = dict(zip(df.section_id.values.tolist(),get_embeddings(model,df.text.values.tolist())))
            logging.info("Successfully generated embeddings")


            # saving the embeddings locally and uploading it to the aws s3 bucket
            save_json(embeddings,self.embedding_config.embeddings_path)
            upload_to_s3(self.embedding_config.embeddings_path.split('/')[-1])

            logging.info("Successfully saved the embeddings both locally and in AWS S3 bucket")

            return self.embedding_config.embeddings_path
        

        except Exception as e:
            logging.info("Exception occured in the initiate_data_transformation")
            raise CustomException(e,sys)
        



if __name__=="__main__":
    obj=EmbeddingGeneration()
    obj.initiate_embedding_generation("data/preprocessed.csv")


