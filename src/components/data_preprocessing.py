# importing the required libraries
import pandas as pd
import numpy as np
from functools import reduce
import tqdm
import re
import os
import sys
from dataclasses import dataclass,field
from typing import List
from pathlib import Path

from src.logger.logger import logging
from src.exception.exception import CustomException 
from src.utils.utils import *

from config import SECTION_BY,INPUT_TYPE

""" # Load the .env file to access the environment variables
from dotenv import load_dotenv
load_dotenv() """

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')

BUCKET_NAME = os.getenv('BUCKET_NAME')
FILE_NAME = "preprocessed.csv"






@dataclass
class DataPreProcessingConfig:
    # defining based on what we are going to split our article (eg: sentence,paragraph)
    section_by:str =  SECTION_BY

    # defining which features are we going to consider eg: ['title'],['text'],['title','text']
    input_type: List[str] = field(default_factory=lambda: INPUT_TYPE)

    # defining the s3 path for storing proprocessed data
    processed_s3_path:str = f's3://{BUCKET_NAME}/{FILE_NAME}'

    # defining the s3 path for stroing the prepeocessed data locally
    processed_df_path = f"data/{FILE_NAME}"



   

class DataPreProcessing:

    def __init__(self):
        self.data_preprocessing_config = DataPreProcessingConfig()


    def initiate_data_processing(self,df_path):
        logging.info("Data Preprocessing is initiated")
        try:
            # reading the data with RFM features
            df = pd.read_csv(df_path)
            logging.info("Successfully read data for preprocessing")

            # removing the unwanted column
            df.drop(columns=['article_id.1'],inplace=True)

            # making the date as datetime dtype
            df['published date'] = pd.to_datetime(df['published date'])

            # preprocessing the data
            preprocessed_df,article_section_mapping_path,section_article_mapping_path = preprocess_data(df,SECTION_BY,INPUT_TYPE)
            logging.info("Successfully preprocessed the data")

            # saving the preprocess data both locally and in aws s3 
            preprocessed_df.to_csv(self.data_preprocessing_config.processed_df_path,index=True)
            preprocessed_df.to_csv(self.data_preprocessing_config.processed_s3_path,index=True,storage_options={
                                                                                'key': AWS_ACCESS_KEY_ID,
                                                                                'secret': AWS_SECRET_ACCESS_KEY
                                                                                })
            
            # uploading the mappings to the AWS S3 bucket
            upload_to_s3(article_section_mapping_path)
            upload_to_s3(section_article_mapping_path)
            logging.info("Successfully uploaded the preprocessed the data and the mappings to AWS S3 bucket")
            
            return self.data_preprocessing_config.processed_df_path

        except Exception as e:
            logging.info("Exception occured in the initiate_data_transformation")
            raise CustomException(e,sys)
        



if __name__=="__main__":
    obj=DataPreProcessing()
    obj.initiate_data_processing("data/raw.csv")


