# importing the libraries
import pandas as pd
import numpy as np
import boto3
import os
import sys
from dataclasses import dataclass
import json

from src.logger.logger import logging
from src.exception.exception import CustomException
from src.utils.utils import *



""" # Retrieve repository secrets
import os
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY') """



@dataclass
class DataIngestionConfig:
    # defining the download path for raw_data and metadata
    raw_data_name = "raw.csv"
    raw_data_path = os.path.join("data", "raw.csv")
    meta_data_path = os.path.join("artifacts","metadata.json")
    
   

class DataIngestion:

    def __init__(self):
        # creating the object of the DataIngestionConfig class
        self.ingestion_config=DataIngestionConfig()


    def initiate_data_ingestion(self):
        logging.info("Data Ingestion Started")
        try:
            # downloading the data from the aws s3 bucket
            status = get_data_from_s3(self.ingestion_config.raw_data_name,self.ingestion_config.raw_data_path)
            if status:
                logging.info("Successfully downloaded raw data from AWS S3 bucket")
            # reading the food_mart_data from the aws s3 bucket
            data=pd.read_csv(self.ingestion_config.raw_data_path)
            # extracting the metadata about articles
            metadata = get_article_meta_data(data)
            # saving the metadata
            save_json(metadata,self.ingestion_config.meta_data_path)
            logging.info('Successfully saved metadata in local')
            # uploading the metadata to s3
            upload_to_s3(self.ingestion_config.meta_data_path.split('/')[-1])
            logging.info('Successfully saved metadata in AWS S3')

            logging.info("Data Ingestion Completed")
            return self.ingestion_config.raw_data_path
            
        except Exception as e:
            logging.info("Exception occured in the data_ingestion")
            raise CustomException(e,sys)
        

if __name__=="__main__":
    obj=DataIngestion()
    obj.initiate_data_ingestion()